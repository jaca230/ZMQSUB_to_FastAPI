from abc import ABC, abstractmethod
from typing import Optional, Type
from pydantic import BaseModel

class Service(ABC):
    query_model: Optional[Type[BaseModel]] = None

    @abstractmethod
    def get(self, **kwargs):
        pass
