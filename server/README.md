# Server

## Local Development

### Prerequisites
- Python 3.13
- PostgreSQL
- uv (package manager)

### Setup

1. Install dependencies:
```bash
uv sync
```

2. Make sure PostgreSQL is running locally

3. Run the application:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres uvicorn src.main:app --reload
```

Then run:
```bash
uvicorn src.main:app --reload
```

### Endpoints

- `GET /` - Health check
- `GET /health` - Database connection check
- `GET /api/dzialy` - Get all dzialy
- `GET /api/rozdzialy` - Get all rozdzialy
- `GET /api/paragrafy` - Get all paragrafy
- `GET /api/grupy_wydatkow` - Get all grupy wydatkow
- `GET /api/czesci_budzetowe` - Get all czesci budzetowe
- `GET /api/zrodla_finansowania` - Get all zrodla finansowania

## Deployment

The application is ready for Railway deployment. Make sure to set the `DATABASE_URL` environment variable in Railway settings.
