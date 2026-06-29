from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The unique identifier of the agent (e.g. 'candidate')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of what the agent does."""
        pass

    @property
    @abstractmethod
    def required_inputs(self) -> list[str]:
        """The keys required in the shared state before execution."""
        pass

    @property
    @abstractmethod
    def produced_outputs(self) -> list[str]:
        """The keys that will be produced or updated in the shared state."""
        pass

    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent business logic.
        
        Args:
            state: The shared execution state dictionary.
            
        Returns:
            Dict[str, Any]: The updates to apply to the shared state.
        """
        pass
