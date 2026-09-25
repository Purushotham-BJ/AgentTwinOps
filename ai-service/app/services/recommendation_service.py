"""Recommendation orchestration over real backend operational data."""
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.agents.recommendation import RecommendationAgent
from app.schemas.recommendation import Recommendation
from app.services.backend_client import backend_client


class RecommendationService:
    def __init__(self) -> None:
        self.agent = RecommendationAgent()

    async def generate_recommendations(
        self,
        infrastructure_ids: List[str] | None = None,
        incident_ids: List[str] | None = None,
        force_regenerate: bool = False,
        auth_token: str | None = None,
    ) -> List[Recommendation]:
        infrastructure = await backend_client.get_infrastructure(auth_token=auth_token)
        selected = set(infrastructure_ids or [str(item["id"]) for item in infrastructure])
        services = [item for item in infrastructure if str(item["id"]) in selected]
        if infrastructure_ids and len(services) != len(set(infrastructure_ids)):
            raise ValueError("Infrastructure service not found")
        incidents = await backend_client.get_incidents(auth_token=auth_token)
        if incident_ids:
            incidents = [item for item in incidents if str(item.get("id")) in set(incident_ids)]

        generated: List[Recommendation] = []
        for service in services:
            service_id = str(service["id"])
            metrics = backend_client.get_metrics(service_id, limit=1, auth_token=auth_token)
            metric = metrics[-1] if metrics else {}
            twin = await backend_client.get_twin_by_service(service_id, auth_token=auth_token)
            service_incidents = [item for item in incidents if str(item.get("service_id")) == service_id]
            for raw in self.agent.generate(service, metric, twin, service_incidents):
                generated.append(Recommendation(
                    **raw,
                    created_at=datetime.now(timezone.utc),
                ))
        return generated


recommendation_service = RecommendationService()
