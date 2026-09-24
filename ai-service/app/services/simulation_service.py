"""Simulation service with LangGraph orchestration"""
from typing import Dict, Any
from datetime import datetime
from uuid import uuid4
from langgraph.graph import StateGraph, END
from app.orchestration.state import SimulationState
from app.agents import SimulationAgent
from app.services.backend_client import backend_client
from app.schemas.simulation import SimulationResult, SimulationImpact
from app.schemas.common import MetricPoint


class SimulationService:
    """Service for running what-if simulations"""
    
    def __init__(self):
        self.simulation_agent = SimulationAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph for simulation workflow"""
        workflow = StateGraph(SimulationState)
        
        # Add nodes
        workflow.add_node("baseline", self._baseline_node)
        workflow.add_node("simulation", self._simulation_node)
        
        # Define edges
        workflow.set_entry_point("baseline")
        workflow.add_edge("baseline", "simulation")
        workflow.add_edge("simulation", END)
        
        return workflow.compile()
    
    async def _baseline_node(self, state: SimulationState) -> SimulationState:
        """Capture baseline state"""
        service_id = state["service_id"]
        
        # Get all infrastructure and find the specific service
        infrastructure = await backend_client.get_infrastructure()
        service = None
        if infrastructure:
            service = next((svc for svc in infrastructure if svc.get("id") == service_id), None)
        
        # If service not found, create a default baseline
        if not service:
            service = {
                "id": service_id,
                "service_name": f"service-{service_id[:8]}",
                "status": "active",
                "service_type": "application",
                "host": "unknown",
                "port": 8080
            }
        
        state["baseline_state"] = service
        return state
    
    async def _simulation_node(self, state: SimulationState) -> SimulationState:
        """Run simulation"""
        result = await self.simulation_agent.process(state)
        state["simulated_state"] = result.get("simulation_result", {})
        return state
    
    async def simulate(
        self, 
        scenario: str, 
        service_id: str,
        parameters: Dict[str, Any] = None
    ) -> SimulationResult:
        """Run simulation scenario"""
        
        # Initialize state
        initial_state: SimulationState = {
            "scenario": scenario,
            "service_id": service_id,
            "parameters": parameters or {},
            "baseline_state": {},
            "simulated_state": {},
            "impact_analysis": {},
            "timeline": [],
            "mitigation_steps": [],
        }
        
        # Run graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Extract results
        sim_result = final_state.get("simulated_state", {})
        impact_data = sim_result.get("impact", {})
        timeline_data = sim_result.get("timeline", [])
        recommendations = sim_result.get("recommendations", [])
        
        # Build impact
        impact = SimulationImpact(
            cpu_delta=impact_data.get("cpu_delta", 0.0),
            memory_delta=impact_data.get("memory_delta", 0.0),
            latency_delta=impact_data.get("latency_delta", 0.0),
            failure_probability=impact_data.get("failure_probability", 0.0),
        )
        
        # Build timeline
        timeline = [
            MetricPoint(
                timestamp=datetime.fromisoformat(point["timestamp"]),
                value=point["value"]
            )
            for point in timeline_data
        ]
        
        # Build result
        result = SimulationResult(
            id=str(uuid4()),
            scenario=scenario,
            service_id=service_id,
            status="completed",
            predicted_impact=impact,
            timeline=timeline,
            recommendations=recommendations,
            created_at=datetime.now(),
            completed_at=datetime.now(),
        )
        
        return result


# Singleton instance
simulation_service = SimulationService()
