"""Proposal-only recovery agent."""
from typing import Any, Dict, List

from .base import BaseAgent


class RecoveryAgent(BaseAgent):
    """Convert high-priority recommendations into human-approved proposals."""

    def __init__(self) -> None:
        super().__init__("RecoveryAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        status = state.get("operational_status", "HEALTHY")
        recommendations = state.get("recommendations", [])
        if status == "HEALTHY":
            state["recovery_recommendations"] = []
            return state
        state["recovery_recommendations"] = [
            {
                "action": item["action"],
                "priority": item["priority"],
                "requires_human_approval": True,
                "execution": "proposal_only",
            }
            for item in recommendations
            if item.get("priority") in {"critical", "high"}
        ]
        return state
