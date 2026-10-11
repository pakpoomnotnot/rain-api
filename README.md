# Rain API

A REST API built with FastAPI that serves rainfall data from Supabase / PostgreSQL.
It provides two main features:

1. **Max rainfall summary** - the highest rainfall over the last 1, 3 and 24 hours, with station names.
2. **72-hour rainfall forecast** - a time series for every station (3-hour steps) from the latest model run.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/rain/max-summary` | Max rainfall for 1h / 3h / 24h. Calls the RPCs `get_max_rain_1h`, `get_max_rain_3h` and `get_max_rain_24h` in parallel, with a 30-second timeout. |
| GET | `/rain/forecast-timeseries` | 72-hour rainfall forecast from the RPC `get_rain_forecast_timeseries_72h`. |

### `/rain/forecast-timeseries` query parameters

| Param | Type | Default | Description |
|---|---|---|---|
| `station_code` | string | - | Filter by station code, e.g. `BKN` |
| `limit` | int (1-5000) | 500 | Maximum number of records |

Results are sorted by `forecast_datetime`, newest first:

```json
{
  "run": { "run_time": "..." },
  "count": 24,
  "station_code": "BKN",
  "data": [ ... ]
}
```

Interactive API docs are available at `http://localhost:9000/docs`.

## Project structure

```
app/
  main.py              # Creates the FastAPI app and includes routers
  supabase_client.py   # Supabase client (reads config from env)
  routers/rain.py      # /rain/* endpoints
  db/connection.py     # psycopg2 connection (direct Postgres access)
config/
  settings.py          # Loads environment variables
```

## Configuration (environment variables)

Copy the example file and fill in real values. `.env` is git-ignored and must not be committed.

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `DB_HOST` | Yes | PostgreSQL host |
| `DB_PORT` | No | Defaults to `5432` |
| `DB_NAME` | No | Defaults to `postgres` |
| `DB_USER` | No | Defaults to `postgres` |
| `DB_PASSWORD` | Yes | PostgreSQL password |
| `SUPABASE_URL` | Yes | Supabase URL, e.g. `http://<host>:8000` |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Supabase service role key |

The app fails at startup with a clear error if a required variable is missing.

## Running locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9000
```

## Running with Docker

```bash
docker build -t rain-api .
docker run --env-file .env -p 9000:9000 rain-api
```
