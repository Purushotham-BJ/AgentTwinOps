"""Digital Twin service"""
from typing import List
from datetime import datetime
from uuid import uuid4
import random
from app.services.backend_client import backend_client
from app.services.prediction_service import prediction_service
from app.schemas.twin import TwinObject, TwinState


class TwinService:
    """Service for managing Digital Twins"""
    
    async def get_twins(self) -> List[TwinObject]:
        """Get all digital twins"""
        infrastructure = await backend_client.get_infrastructure()
        
        twins = []
        for svc in infrastructure:
            twin = await self._create_twin_from_infrastructure(svc)
            twins.append(twin)
        
        return twins
    
    async def get_twin_by_id(self, twin_id: str) -> TwinObject | None:
        """Get specific digital twin"""
        # Extract service_id from twin_id (format: twin_<service_id>)
        service_id = twin_id.replace("twin_", "")
        
        service = await backend_client.get_infrastructure_by_id(service_id)
        if not service:
            return None
        
        return await self._create_twin_from_infrastructure(service)
    
    async def _create_twin_from_infrastructure(self, service: dict) -> TwinObject:
        """Create digital twin from infrastructure service"""
        service_id = service["id"]
        
        # Generate current state
        current_state = TwinState(
            cpu_usage=40 + random.random() * 30,
            memory_usage=50 + random.random() * 25,
            latency_ms=50 + random.random() * 100,
            error_rate=random.random() * 2,
            request_rate=100 + random.random() * 200,
            status=service.get("status", "unknown"),
        )
        
        # Get prediction for future state
        try:
            cpu_pred = await prediction_service.predict(service_id, "cpu", 360)
            mem_pred = await prediction_service.predict(service_id, "memory", 360)
            
            predicted_state = TwinState(
                cpu_usage=cpu_pred.predicted_value,
                memory_usage=mem_pred.predicted_value,
                latency_ms=current_state.latency_ms * (1 + cpu_pred.failure_probability * 0.5),
                error_rate=current_state.error_rate * (1 + cpu_pred.failure_probability),
                request_rate=current_state.request_rate,
                status="degraded" if cpu_pred.risk_level in ["high", "critical"] else "healthy",
            )
            
            # Calculate health score
            health_score = self._calculate_health_score(
                current_state, 
                cpu_pred.failure_probability,
                service.get("status", "unknown")
            )
        except:
            # Fallback if prediction fails
            predicted_state = current_state
            health_score = 75.0
        
        # Build twin object
        twin = TwinObject(
            id=f"twin_{service_id}",
            name=service["service_name"],
            service_id=service_id,
            service_type=service["service_type"],
            current_state=current_state,
            predicted_state=predicted_state,
            health_score=health_score,
            sync_status="synced",
            last_synced=datetime.now(),
        )
        
        return twin
    
    def _calculate_health_score(
        self, 
        state: TwinState, 
        failure_prob: float,
        status: str
    ) -> float:
        """Calculate health score 0-100"""
        score = 100.0
        
        # Deduct for high resource usage
        if state.cpu_usage > 80:
            score -= (state.cpu_usage - 80) * 2
        if state.memory_usage > 80:
            score -= (state.memory_usage - 80) * 2
        
        # Deduct for high latency
        if state.latency_ms > 200:
            score -= min(30, (state.latency_ms - 200) / 10)
        
        # Deduct for error rate
        score -= state.error_rate * 10
        
        # Deduct for failure probability
        score -= failure_prob * 40
        
        # Deduct for unhealthy status
        if status in ["unhealthy", "inactive"]:
            score -= 30
        elif status == "degraded":
            score -= 15
        
        return max(0.0, min(100.0, score))


# Singleton instance
twin_service = TwinService()
