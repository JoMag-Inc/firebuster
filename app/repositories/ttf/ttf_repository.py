"""TTF Repository layer for data persistence."""

from abc import ABC, abstractmethod
from app.models.ttf_result import TTFResult
from sqlmodel import Session, select, delete


class TTFRepository(ABC):
    """Abstract base repository for TTF result persistence.

    Implementations should provide:
    - Retrieval of cached TTF results by coordinates
    - Persistence of new TTF calculation results

    Example:
        To create a custom repository implementation:

        >>> class CustomTTFRepository(TTFRepository):
        ...     def get(self, lat: float, lon: float) -> TTFResult | None:
        ...         # Custom retrieval logic
        ...         return my_storage.find(lat, lon)
        ...
        ...     def save(self, result: TTFResult) -> None:
        ...         # Custom save logic
        ...         my_storage.store(result)vk
    """

    @abstractmethod
    def get(self, lat: float, lon: float) -> TTFResult | None:
        """Retrieve a cached TTF result for specific coordinates.

        Args:
            lat: Latitude coordinate (decimal degrees)
            lon: Longitude coordinate (decimal degrees)

        Returns:
            TTFResult if a cached result exists for the coordinates, None otherwise.
        """
        pass

    @abstractmethod
    def save(self, result: TTFResult) -> None:
        """Persist a TTF calculation result.

        Args:
            result: TTFResult instance containing calculation data and metadata

        Raises:
            Implementation-specific exceptions for storage failures
        """

    @abstractmethod
    def delete(self, lat: float, lon: float) -> int:
        """Delete a TTF calculation result

        Args:
            lat: Latitude`

            lon: Longitude
        """


class PostgresTTFRepository(TTFRepository):
    """PostgreSQL implementation of TTF repository.

    Attributes:
        session: SQLModel Session instance for database operations

    Example:
        >>> from sqlmodel import Session, create_engine
        >>> engine = create_engine("postgresql://user:pass@localhost/db")
        >>> with Session(engine) as session:
        ...     repo = PostgresTTFRepository(session)
        ...     result = repo.get(lat=60.123, lon=5.456)
    """

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

    def delete(self, lat: float, lon: float) -> int:
        stmt = delete(TTFResult).where(
            TTFResult.latitude == lat,
            TTFResult.longitude == lon,
        )
        result = self.session.exec(stmt)
        self.session.commit()
        return result.rowcount or 0
