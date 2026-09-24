"""AI Service API Routes"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.schemas.recommendation import RecommendationListResponse, RecommendationGenerateRequest
from app.schemas.twin import TwinListResponse, TwinResponse
from app.services.prediction_service import prediction_service
from app.services.simulation_service import simulation_service
from app.services.recommendation_service import recommendation_service
from app.services.twin_service import twin_service
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["ai"])


@router.post("/predict/cpu", response_model=PredictionResponse)
async def predict_cpu(request: PredictionRequest):
    """Predict CPU usage for a service"""
    result = await prediction_service.predict(
        service_id=request.service_id,
        prediction_type="cpu",
        horizon_minutes=request.horizon_minutes
    )
    return PredictionResponse(data=result, timestamp=datetime.now())


@router.post("/predict/memory", response_model=PredictionResponse)
async def predict_memory(request: PredictionRequest):
    """Predict memory usage for a service"""
    result = await prediction_service.predict(
        service_id=request.service_id,
        prediction_type="memory",
        horizon_minutes=request.horizon_minutes
    )
    return PredictionResponse(data=result, timestamp=datetime.now())


@router.post("/predict/failure", response_model=PredictionResponse)
async def predict_failure(request: PredictionRequest):
    """Predict failure probability for a service"""
    result = await prediction_service.predict(
        service_id=request.service_id,
        prediction_type="failure",
        horizon_minutes=request.horizon_minutes
    )
    return PredictionResponse(data=result, timestamp=datetime.now())


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_scenario(request: SimulationRequest):
    """Run simulation scenario"""
    result = await simulation_service.simulate(
        scenario=request.scenario,
        service_id=request.service_id,
        parameters=request.parameters
    )
    return SimulationResponse(data=result, timestamp=datetime.now())


@router.get("/recommendations", response_model=RecommendationListResponse)
async def get_recommendations():
    """Get all recommendations"""
    recommendations = await recommendation_service.generate_recommendations()
    return RecommendationListResponse(data=recommendations, timestamp=datetime.now())


@router.post("/recommendations/generate", response_model=RecommendationListResponse)
async def generate_recommendations(request: RecommendationGenerateRequest):
    """Generate new recommendations"""
    recommendations = await recommendation_service.generate_recommendations(
        infrastructure_ids=request.infrastructure_ids,
        incident_ids=request.incident_ids,
        force_regenerate=request.force_regenerate
    )
    return RecommendationListResponse(data=recommendations, timestamp=datetime.now())


@router.get("/twins", response_model=TwinListResponse)
async def get_twins():
    """Get all digital twins"""
    twins = await twin_service.get_twins()
    return TwinListResponse(data=twins, timestamp=datetime.now())


@router.get("/twins/{twin_id}", response_model=TwinResponse)
async def get_twin(twin_id: str):
    """Get specific digital twin"""
    twin = await twin_service.get_twin_by_id(twin_id)
    if not twin:
        raise HTTPException(status_code=404, detail="Twin not found")
    return TwinResponse(data=twin, timestamp=datetime.now())


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-service", "timestamp": datetime.now().isoformat()}
