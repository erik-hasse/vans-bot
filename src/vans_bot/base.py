from abc import ABC, abstractmethod


class BaseChecker(ABC):
    @abstractmethod
    def check_for_messages(self) -> list[str]:
        pass
