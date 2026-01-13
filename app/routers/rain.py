from fastapi import APIRouter, HTTPException
from supabase import create_client
import asyncio

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