from typing import Dict
from core.registry.base import BaseAgent

class AgentRegistry:
    _agents: Dict[str, BaseAgent] = {}

    @classmethod
    def register(cls, agent: BaseAgent):
        """Register an agent in the platform registry."""
        cls._agents[agent.name] = agent

    @classmethod
    def get(cls, name: str) -> BaseAgent:
        """Retrieve an agent by its unique name."""
        if name not in cls._agents:
            raise ValueError(f"Agent '{name}' is not registered in the AgentRegistry.")
        return cls._agents[name]

    @classmethod
    def list_agents(cls) -> Dict[str, str]:
        """List all registered agents and their descriptions."""
        return {name: agent.description for name, agent in cls._agents.items()}
