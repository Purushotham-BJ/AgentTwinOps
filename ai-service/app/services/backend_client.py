"""Client for communicating with existing backend API"""
import httpx
from typing import List, Dict, Any
from app.config.settings import settings


class BackendClient:
    """HTTP client for backend API"""
    
    def __init__(self):
        self.base_url = settings.BACKEND_API_URL
        self.timeout = 10.0
        self.token = settings.BACKEND_API_TOKEN
        self._cached_token = None
    
    async def _get_service_token(self) -> str:
        """Get or create a service account token for backend authentication"""
        if self._cached_token:
            return self._cached_token
            
        # Try configured token first
        if self.token:
            return self.token
            
        # Otherwise, try to authenticate with service credentials from environment
        service_email = settings.BACKEND_SERVICE_EMAIL if hasattr(settings, 'BACKEND_SERVICE_EMAIL') else None
        service_password = settings.BACKEND_SERVICE_PASSWORD if hasattr(settings, 'BACKEND_SERVICE_PASSWORD') else None
        
        if service_email and service_password:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/api/v1/auth/login",
                        headers={"Content-Type": "application/json"},
                        json={"email": service_email, "password": service_password}
                    )
                    response.raise_for_status()
                    data = response.json()
                    self._cached_token = data.get("data", {}).get("access_token")
                    return self._cached_token
            except httpx.HTTPError:
                pass
        
        return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    async def _get_headers_async(self) -> Dict[str, str]:
        """Get request headers with authentication (async version with token refresh)"""
        headers = {"Content-Type": "application/json"}
        token = await self._get_service_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    async def get_infrastructure(self) -> List[Dict[str, Any]]:
        """Fetch all infrastructure services"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = await self._get_headers_async()
                response = await client.get(
                    f"{self.base_url}/api/v1/infrastructure",
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                # Backend returns: {"success": true, "data": {"items": [...], "total": N}}
                data = result.get("data", {})
                return data.get("items", [])
            except httpx.HTTPError as e:
                # Log the error for debugging
                print(f"Backend connection failed: {e}")
                # In REAL mode, raise error instead of fallback
                if settings.AI_SERVICE_MODE == "real":
                    raise Exception(f"Backend infrastructure API unavailable: {e}")
                # Development fallback
                return self._mock_infrastructure()
    
    async def get_infrastructure_by_id(self, service_id: str) -> Dict[str, Any] | None:
        """Fetch specific infrastructure service"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = await self._get_headers_async()
                response = await client.get(
                    f"{self.base_url}/api/v1/infrastructure/{service_id}",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data")
            except httpx.HTTPError:
                # In REAL mode, raise error instead of fallback
                if settings.AI_SERVICE_MODE == "real":
                    raise Exception(f"Backend infrastructure/{service_id} API unavailable")
                # Development fallback
                infrastructure = self._mock_infrastructure()
                return next((svc for svc in infrastructure if svc["id"] == service_id), None)
    
    async def get_incidents(self) -> List[Dict[str, Any]]:
        """Fetch all incidents"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = await self._get_headers_async()
                response = await client.get(
                    f"{self.base_url}/api/v1/incidents",
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                # Backend returns: {"success": true, "data": {"items": [...], "total": N}}
                data = result.get("data", {})
                return data.get("items", [])
            except httpx.HTTPError:
                # In REAL mode, raise error instead of fallback
                if settings.AI_SERVICE_MODE == "real":
                    raise Exception("Backend incidents API unavailable")
                # Development fallback
                return self._mock_incidents()
    
    def _mock_infrastructure(self) -> List[Dict[str, Any]]:
        """Mock infrastructure data for development"""
        from datetime import datetime
        now = datetime.now().isoformat()
        return [
            {
                "id": "svc_001",
                "service_name": "auth-service",
                "service_type": "api",
                "status": "healthy",
                "host": "10.0.1.10",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "svc_002",
                "service_name": "payment-service",
                "service_type": "api",
                "status": "degraded",
                "host": "10.0.1.15",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "svc_003",
                "service_name": "database-postgres",
                "service_type": "database",
                "status": "healthy",
                "host": "10.0.2.5",
                "created_at": now,
                "updated_at": now,
            },
        ]
    
    def _mock_incidents(self) -> List[Dict[str, Any]]:
        """Mock incident data for development"""
        from datetime import datetime
        now = datetime.now().isoformat()
        return [
            {
                "id": "inc_001",
                "service_id": "svc_002",
                "severity": "high",
                "incident_type": "performance_degradation",
                "resolution_status": "open",
                "timestamp": now,
            },
        ]


# Singleton instance
backend_client = BackendClient()
