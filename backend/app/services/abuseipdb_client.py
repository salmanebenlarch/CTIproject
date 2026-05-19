import httpx
from app.core.config import get_settings

settings = get_settings()

ABUSEIPDB_BASE_URL = "https://api.abuseipdb.com/api/v2"


class AbuseIPDBClient:
    def __init__(self):
        self.api_key = settings.abuseipdb_api_key
        self.headers = {
            "Key": self.api_key,
            "Accept": "application/json"
        }

    async def check_ip(self, ip_address: str, max_age_in_days: int = 90) -> dict:
        """Vérifie la réputation d'une adresse IP."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ABUSEIPDB_BASE_URL}/check",
                headers=self.headers,
                params={
                    "ipAddress": ip_address,
                    "maxAgeInDays": max_age_in_days,
                    "verbose": True
                }
            )
            response.raise_for_status()
            return response.json().get("data", {})


# ✅ Cette ligne est indispensable pour l'import
abuseipdb_client = AbuseIPDBClient()