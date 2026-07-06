from abc import ABC, abstractmethod
from typing import Any


class AbstractQueryInterpreter(ABC):
    @abstractmethod
    def interpret(self, query: str) -> dict[str, Any]:
        raise NotImplementedError