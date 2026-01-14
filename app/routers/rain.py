from fastapi import APIRouter, HTTPException
from supabase import create_client
import asyncio
from typing import Optional
from fastapi import Query
from datetime import datetime

SUPABASE_URL = "http://10.198.110.39:8000"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJzZXJ2aWNlX3JvbGUiLAogICAgImlzcyI6ICJzdXBhYmFzZS1kZW1vIiwKICAgICJpYXQiOiAxNjQxNzY5MjAwLAogICAgImV4cCI6IDE3OTk1MzU2MDAKfQ.DaYlNEoUrrEn2Ig7tqibS-PHK5vgusbcbo7X36XVt4Q"

supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
router = APIRouter(prefix="/rain", tags=["Rain"])


@router.get("/max-summary")
async def max_rain_summary():
    """
    Endpoint: GET /rain/max-summary
    Return: ค่าฝนสูงสุด 1h, 3h, 24h พร้อมชื่อสถานี
    """
    try:
        # เรียกแบบ parallel เพื่อลดเวลา
        max_1h_task = asyncio.create_task(
            asyncio.to_thread(supabase.rpc("get_max_rain_1h").execute)
        )
        max_3h_task = asyncio.create_task(
            asyncio.to_thread(supabase.rpc("get_max_rain_3h").execute)
        )
        max_24h_task = asyncio.create_task(
            asyncio.to_thread(supabase.rpc("get_max_rain_24h").execute)
        )
        
        # รอให้ทั้ง 3 เสร็จพร้อมกัน (timeout 30 วินาที)
        max_1h, max_3h, max_24h = await asyncio.wait_for(
            asyncio.gather(max_1h_task, max_3h_task, max_24h_task),
            timeout=30.0
        )
        
        return {
            "max_1h": max_1h.data,
            "max_3h": max_3h.data,
            "max_24h": max_24h.data
        }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Query timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
      
@router.get("/forecast-timeseries")
async def rain_forecast_timeseries(
    station_code: Optional[str] = Query(
        default=None,
        description="รหัสสถานี เช่น BKN"
    ),
    limit: int = Query(
        default=500,
        ge=1,
        le=5000,
        description="จำนวน record สูงสุด"
    )
):
    """
    ทุก station + ทุก timestep (3 ชม.) จาก run ล่าสุด
    - เรียง forecast_datetime ล่าสุดขึ้นก่อน
    - filter ตาม station_code ได้
    - limit ได้
    """
    try:
        res = await asyncio.to_thread(
            supabase.rpc("get_rain_forecast_timeseries_72h").execute
        )

        data = res.data or []

        # 🔹 filter ตาม station_code
        if station_code:
            data = [
                row for row in data
                if row.get("station_code") == station_code
            ]

        # 🔹 sort ตาม forecast_datetime (ล่าสุด -> เก่า)
        data.sort(
            key=lambda r: datetime.fromisoformat(
                r["forecast_datetime"].replace("Z", "")
            ),
            reverse=True
        )

        # 🔹 limit จำนวนข้อมูล
        data = data[:limit]

        return {
            "run": {
                "run_time": data[0]["model_run_time"] if data else None
            },
            "count": len(data),
            "station_code": station_code,
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))