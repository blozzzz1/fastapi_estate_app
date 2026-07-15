# Real Estate API (FastAPI)

CRUD API for real estate listings with search filters and JWT authentication via HttpOnly cookies.

## Features

- Register / login / logout / current user
- JWT stored in an HttpOnly cookie (`access_token`)
- Property CRUD (create/update/delete require auth; owners only)
- Public search with filters, pagination, and sorting

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open docs: http://127.0.0.1:8000/docs

## Tests

```bash
pytest -v
```

## Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Create account + set cookie |
| POST | `/api/auth/login` | Login + set cookie |
| POST | `/api/auth/logout` | Clear cookie |
| GET | `/api/auth/me` | Current user (auth required) |

## Properties

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/properties` | Public (except `my_only`) |
| GET | `/api/properties/{id}` | Public |
| POST | `/api/properties` | Required |
| PATCH | `/api/properties/{id}` | Owner |
| DELETE | `/api/properties/{id}` | Owner |

### Query filters

- `q` — search in title, description, address
- `city`, `property_type`, `deal_type`
- `min_price`, `max_price`, `min_area`, `max_area`
- `rooms`, `min_rooms`, `max_rooms`
- `is_active`, `owner_id`, `my_only`
- `page`, `page_size`, `sort_by` (`price|area|rooms|created_at`), `sort_order` (`asc|desc`)

### Example search

```
GET /api/properties?city=Moscow&deal_type=sale&property_type=apartment&min_price=5000000&max_price=15000000&rooms=2&sort_by=price&sort_order=asc
```

## Property types

`apartment`, `house`, `studio`, `commercial`, `land`

## Deal types

`sale`, `rent`
