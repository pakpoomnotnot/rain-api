# Rain API

REST API (FastAPI) สำหรับดึงข้อมูลปริมาณฝนจากฐานข้อมูล Supabase / PostgreSQL
ให้บริการ 2 อย่างหลัก:

1. **สรุปฝนสูงสุด** — ค่าฝนสูงสุดในช่วง 1 ชม., 3 ชม. และ 24 ชม. พร้อมชื่อสถานี
2. **ฝนพยากรณ์ล่วงหน้า 72 ชม.** — time series ของทุกสถานี (ราย 3 ชม.) จาก model run ล่าสุด

## Endpoints

| Method | Path | คำอธิบาย |
|---|---|---|
| GET | `/rain/max-summary` | ค่าฝนสูงสุด 1h / 3h / 24h (เรียก RPC `get_max_rain_1h`, `get_max_rain_3h`, `get_max_rain_24h` แบบขนาน, timeout 30 วินาที) |
| GET | `/rain/forecast-timeseries` | ฝนพยากรณ์ 72 ชม. จาก RPC `get_rain_forecast_timeseries_72h` |

### `/rain/forecast-timeseries` query parameters

| Param | Type | Default | คำอธิบาย |
|---|---|---|---|
| `station_code` | string | – | กรองตามรหัสสถานี เช่น `BKN` |
| `limit` | int (1–5000) | 500 | จำนวน record สูงสุด |

ผลลัพธ์เรียงตาม `forecast_datetime` จากใหม่ไปเก่า:

```json
{
  "run": { "run_time": "..." },
  "count": 24,
  "station_code": "BKN",
  "data": [ ... ]
}
```

เอกสาร API แบบ interactive: `http://localhost:9000/docs`

## โครงสร้างโปรเจกต์

```
app/
  main.py              # สร้าง FastAPI app และ include router
  supabase_client.py   # Supabase client (อ่านค่าจาก env)
  routers/rain.py      # endpoints /rain/*
  db/connection.py     # psycopg2 connection (ต่อ Postgres ตรง)
config/
  settings.py          # โหลด environment variables
```

## การตั้งค่า (Environment variables)

คัดลอกไฟล์ตัวอย่างแล้วใส่ค่าจริง (`.env` ถูก ignore ไว้แล้ว ห้าม commit):

```bash
cp .env.example .env
```

| Variable | Required | คำอธิบาย |
|---|---|---|
| `DB_HOST` | ✅ | host ของ PostgreSQL |
| `DB_PORT` | | default `5432` |
| `DB_NAME` | | default `postgres` |
| `DB_USER` | | default `postgres` |
| `DB_PASSWORD` | ✅ | รหัสผ่าน PostgreSQL |
| `SUPABASE_URL` | ✅ | URL ของ Supabase เช่น `http://<host>:8000` |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | service role key ของ Supabase |

## รันบนเครื่อง

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9000
```

## รันด้วย Docker

```bash
docker build -t rain-api .
docker run --env-file .env -p 9000:9000 rain-api
```
