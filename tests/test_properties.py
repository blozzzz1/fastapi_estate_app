from fastapi.testclient import TestClient

from tests.conftest import PROPERTY_PAYLOAD


def test_create_property_requires_auth(client: TestClient) -> None:
    response = client.post("/api/properties", json=PROPERTY_PAYLOAD)
    assert response.status_code == 401


def test_create_and_get_property(auth_client: TestClient) -> None:
    created = auth_client.post("/api/properties", json=PROPERTY_PAYLOAD)
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == PROPERTY_PAYLOAD["title"]
    assert body["city"] == "Moscow"
    assert body["owner_id"] >= 1

    fetched = auth_client.get(f"/api/properties/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]


def test_get_property_not_found(client: TestClient) -> None:
    response = client.get("/api/properties/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Property not found"


def test_list_filters(auth_client: TestClient) -> None:
    auth_client.post("/api/properties", json=PROPERTY_PAYLOAD)
    auth_client.post(
        "/api/properties",
        json={
            **PROPERTY_PAYLOAD,
            "title": "Country house",
            "city": "Sochi",
            "property_type": "house",
            "deal_type": "rent",
            "price": 150_000,
            "area": 120,
            "rooms": 4,
            "description": "Sea view villa",
        },
    )

    by_city = auth_client.get("/api/properties", params={"city": "Moscow"})
    assert by_city.status_code == 200
    assert by_city.json()["total"] == 1
    assert by_city.json()["items"][0]["city"] == "Moscow"

    by_price = auth_client.get(
        "/api/properties",
        params={"min_price": 10_000_000, "max_price": 15_000_000},
    )
    assert by_price.json()["total"] == 1
    assert by_price.json()["items"][0]["price"] == 12_000_000

    by_rooms = auth_client.get("/api/properties", params={"rooms": 2})
    assert by_rooms.json()["total"] == 1

    by_type = auth_client.get(
        "/api/properties",
        params={"property_type": "house", "deal_type": "rent"},
    )
    assert by_type.json()["total"] == 1
    assert by_type.json()["items"][0]["title"] == "Country house"

    by_q = auth_client.get("/api/properties", params={"q": "metro"})
    assert by_q.json()["total"] == 1
    assert "metro" in by_q.json()["items"][0]["description"].lower()


def test_list_sort_and_pagination(auth_client: TestClient) -> None:
    for price in (3_000_000, 1_000_000, 2_000_000):
        auth_client.post(
            "/api/properties",
            json={**PROPERTY_PAYLOAD, "title": f"Apt {price}", "price": price},
        )

    sorted_asc = auth_client.get(
        "/api/properties",
        params={"sort_by": "price", "sort_order": "asc"},
    )
    prices = [item["price"] for item in sorted_asc.json()["items"]]
    assert prices == sorted(prices)

    page1 = auth_client.get(
        "/api/properties",
        params={"page": 1, "page_size": 2, "sort_by": "price", "sort_order": "asc"},
    )
    assert page1.json()["total"] == 3
    assert len(page1.json()["items"]) == 2

    page2 = auth_client.get(
        "/api/properties",
        params={"page": 2, "page_size": 2, "sort_by": "price", "sort_order": "asc"},
    )
    assert len(page2.json()["items"]) == 1


def test_my_only_requires_auth(client: TestClient) -> None:
    response = client.get("/api/properties", params={"my_only": True})
    assert response.status_code == 401


def test_my_only_returns_own_listings(auth_client: TestClient, register_user) -> None:
    assert auth_client.post("/api/properties", json=PROPERTY_PAYLOAD).status_code == 201

    other = register_user(email="other@example.com", full_name="Other")
    assert (
        other.post(
            "/api/properties",
            json={**PROPERTY_PAYLOAD, "title": "Other apartments", "city": "Kazan"},
        ).status_code
        == 201
    )

    mine = auth_client.get("/api/properties", params={"my_only": True})
    assert mine.status_code == 200
    assert mine.json()["total"] == 1
    assert mine.json()["items"][0]["title"] == PROPERTY_PAYLOAD["title"]


def test_update_own_property(auth_client: TestClient) -> None:
    created = auth_client.post("/api/properties", json=PROPERTY_PAYLOAD)
    property_id = created.json()["id"]

    updated = auth_client.patch(
        f"/api/properties/{property_id}",
        json={"price": 11_000_000, "title": "Updated"},
    )
    assert updated.status_code == 200
    assert updated.json()["price"] == 11_000_000
    assert updated.json()["title"] == "Updated"


def test_update_foreign_property_forbidden(auth_client: TestClient, register_user) -> None:
    created = auth_client.post("/api/properties", json=PROPERTY_PAYLOAD)
    property_id = created.json()["id"]

    other = register_user(email="intruder@example.com")
    response = other.patch(f"/api/properties/{property_id}", json={"price": 1})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_delete_own_property(auth_client: TestClient) -> None:
    created = auth_client.post("/api/properties", json=PROPERTY_PAYLOAD)
    property_id = created.json()["id"]

    deleted = auth_client.delete(f"/api/properties/{property_id}")
    assert deleted.status_code == 204
    assert auth_client.get(f"/api/properties/{property_id}").status_code == 404


def test_delete_foreign_property_forbidden(auth_client: TestClient, register_user) -> None:
    created = auth_client.post("/api/properties", json=PROPERTY_PAYLOAD)
    property_id = created.json()["id"]

    other = register_user(email="intruder2@example.com")
    response = other.delete(f"/api/properties/{property_id}")
    assert response.status_code == 403
