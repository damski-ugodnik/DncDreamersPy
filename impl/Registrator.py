from abc import ABC, abstractmethod


class Registrator(ABC):

    @abstractmethod
    def record(self, user_id: int, value: str):
        pass
