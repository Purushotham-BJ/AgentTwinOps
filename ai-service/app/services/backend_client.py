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

    async def _get_headers_async(self, token_override: str | None = None) -> Dict[str, str]:
        """Get request headers with authentication (async version with token refresh)"""
        headers = {"Content-Type": "application/json"}
        token = token_override or await self._get_service_token()
        if token:
            headers["Authorization"] = token if token.startswith("Bearer ") else f"Bearer {token}"
        return headers

    async def get_infrastructure(self, auth_token: str | None = None) -> List[Dict[str, Any]]:
        """Fetch all infrastructure services"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = await self._get_headers_async(auth_token)
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

    async def get_infrastructure_by_id(
        self, service_id: str, auth_token: str | None = None
    ) -> Dict[str, Any] | None:
        """Fetch specific infrastructure service"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = await self._get_headers_async(auth_token)
                response = await client.get(
                    f"{self.base_url}/api/v1/infrastructure/{service_id}",
                    headers=headers
                )
                if response.status_code == 404:
                    return None
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

    async def get_incidents(self, auth_token: str | None = None) -> List[Dict[str, Any]]:
        """Fetch all incidents"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = await self._get_headers_async(auth_token)
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

    def get_metrics(
        self, service_id: str, limit: int = 200, auth_token: str | None = None
    ) -> List[Dict[str, Any]]:
        """Fetch historical metrics for a specific service (Synchronous)"""
        with httpx.Client(timeout=self.timeout) as client:
            try:
                token = auth_token or self._cached_token or self.token
                if not token:
                    service_email = settings.BACKEND_SERVICE_EMAIL if hasattr(settings, 'BACKEND_SERVICE_EMAIL') else None
                    service_password = settings.BACKEND_SERVICE_PASSWORD if hasattr(settings, 'BACKEND_SERVICE_PASSWORD') else None
                    if service_email and service_password:
                        try:
                            response = client.post(
                                f"{self.base_url}/api/v1/auth/login",
                                headers={"Content-Type": "application/json"},
                                json={"email": service_email, "password": service_password}
                            )
                            response.raise_for_status()
                            token = response.json().get("data", {}).get("access_token")
                            self._cached_token = token
                        except httpx.HTTPError:
                            pass

                headers = {"Content-Type": "application/json"}
                if token:
                    headers["Authorization"] = token if token.startswith("Bearer ") else f"Bearer {token}"

                response = client.get(
                    f"{self.base_url}/api/v1/metrics/service/{service_id}?limit={limit}",
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()

                # MetricListResponse schema
                items = result.get("items", [])

                # Ensure they are sorted by timestamp ascending
                items.sort(key=lambda x: x.get("timestamp", ""))

                return items
            except httpx.HTTPError as e:
                print(f"Backend metrics connection failed: {e}")
                if settings.AI_SERVICE_MODE == "real":
                    raise Exception(f"Backend metrics API unavailable: {e}")
                return self._mock_metrics(service_id, limit)

    async def get_twin_by_service(
        self, service_id: str, auth_token: str | None = None
    ) -> Dict[str, Any] | None:
        """Fetch the persisted Digital Twin without modifying it."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = await self._get_headers_async(auth_token)
            response = await client.get(
                f"{self.base_url}/api/v1/twins/by-service/{service_id}",
                headers=headers,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

    async def update_twin_predicted_state(
        self, service_id: str, predicted_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """PATCH the twin's predicted_state via the backend API.

        Calls PATCH /api/v1/twins/by-service/{service_id}/predicted-state.
        Returns the updated twin dict on success.
        Raises an exception on failure so the caller can handle it honestly.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = await self._get_headers_async()
            response = await client.patch(
                f"{self.base_url}/api/v1/twins/by-service/{service_id}/predicted-state",
                headers=headers,
                json={"predicted_state": predicted_state},
            )
            response.raise_for_status()
            return response.json()

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

    def _mock_metrics(self, service_id: str, count: int = 40) -> List[Dict[str, Any]]:
        """Mock historical metrics for development/fallback"""
        from datetime import datetime, timedelta
        import random
        now = datetime.now()
        metrics = []
        # Generate oldest to newest
        for i in range(count):
            ts = now - timedelta(minutes=(count - i) * 5)
            metrics.append({
                "id": f"metric_{i}",
                "service_id": service_id,
                "cpu_usage": 30.0 + random.random() * 20.0,
                "memory_usage": 45.0 + random.random() * 10.0,
                "disk_usage": 50.0,
                "network_usage": 1000.0,
                "latency": 50.0,
                "timestamp": ts.isoformat()
            })
        return metrics


# Singleton instance
backend_client = BackendClient()
