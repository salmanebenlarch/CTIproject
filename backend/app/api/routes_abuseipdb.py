from fastapi import APIRouter, HTTPException
from app.services.abuseipdb_client import abuseipdb_client

router = APIRouter(prefix="/api/abuseipdb", tags=["AbuseIPDB"])

@router.get("/check/{ip_address}")
async def check_ip_reputation(ip_address: str, max_age_in_days: int = 90):
    try:
        result = await abuseipdb_client.check_ip(ip_address, max_age_in_days)
        return {"ip": ip_address, "result": result}  # ← wrapper avec "ip" et "result"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))