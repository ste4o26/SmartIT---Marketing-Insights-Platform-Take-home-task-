# SmartIT - Marketing Insights Platform

Two FastAPI services for crypto market data:

- `api`: public API for authentication and protected crypto endpoints.
- `market_data`: internal market-data service that fetches ticker data from Binance and derives simple trading signals.

## Requirements
- Python 3.12+
- Docker and Docker Compose

## Setup With Docker
Create an environment file:

```bash
cp example_env .env
```

Fill `.env`:
Start both services:

```bash
docker compose up --build
```

Service URLs:
- Public API: `http://localhost:8001`
- Market-data service: `http://localhost:8002`
- Public API docs: `http://localhost:8001/docs`
- Market-data docs: `http://localhost:8002/docs`

Stop the services:
```bash
docker compose down
```

## Local Setup
Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create `.env`:
```bash
cp example_env .env
```

For local runs, use this service URL in `.env`:
```bash
MARKET_DATA_SERVICE_BASE_URL=http://localhost:8002
```

Run the market-data service:
```bash
uvicorn market_data.main:app --host 0.0.0.0 --port 8002 --reload
```

Run the public API in another terminal:
```bash
source .venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```

## Data Flow
The public API validates the user token before serving crypto routes. 
It then creates a service-to-service token and calls `market_data`. 
The market-data service validates that internal token, fetches data from Binance, 
  caches ticker responses, and returns either ticker data or a generated signal.
