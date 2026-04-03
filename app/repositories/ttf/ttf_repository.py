from abc import ABC, abstractmethod
from app.models.ttf_result import TTFResult
from sqlmodel import Session, select


class TTFReposiotry(ABC):
    @abstractmethod
    def get(self, lat: float, lon: float) -> TTFResult | None:
        pass

    @abstractmethod
    def save(self, result: TTFResult) -> None:
        pass


class PostgresTTFRepository(TTFReposiotry):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, lat: float, lon: float) -> TTFResult | None:
        result = self.session.exec(
            select(TTFResult).where(
                TTFResult.latitude == lat, TTFResult.longitude == lon
            )
        )
        return result.first()

    def save(self, result: TTFResult) -> None:
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
