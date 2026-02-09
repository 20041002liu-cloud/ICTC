from abc import ABC, abstractmethod


class BaseClient(ABC):
    @abstractmethod
    def evaluate(self, prompt: str) -> str:
        """Return raw model response text."""
        raise NotImplementedError
