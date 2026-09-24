"""Base agent class"""
from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.config.settings import settings


class BaseAgent:
    """Base class for all agents in the multi-agent system"""
    
    def __init__(self, name: str):
        self.name = name
        self.llm = self._init_llm()
    
    def _init_llm(self) -> BaseChatModel:
        """Initialize LLM based on configuration"""
        if settings.OPENAI_API_KEY:
            return ChatOpenAI(
                model=settings.AI_MODEL,
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
                api_key=settings.OPENAI_API_KEY,
            )
        elif settings.ANTHROPIC_API_KEY:
            return ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
                api_key=settings.ANTHROPIC_API_KEY,
            )
        else:
            # Development fallback — uses deterministic logic
            return None
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process state and return updated state"""
        raise NotImplementedError("Subclass must implement process method")
