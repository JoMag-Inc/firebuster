"""TTF Repository layer for data persistence."""

from abc import ABC, abstractmethod
from app.models.ttf_result import TTFResult
from sqlmodel import Session, select


class TTFReposiotry(ABC):
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

        Note:
            Implementations should handle duplicate coordinates according to their
            business logic (e.g., update existing, create new version, etc.)
        """
        pass


class PostgresTTFRepository(TTFReposiotry):
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
        """Retrieve a TTF result from PostgreSQL by coordinates.

        Queries the database for a TTF result matching the exact latitude and
        longitude values. Returns the first matching result if found.

        Args:
            lat: Latitude coordinate (decimal degrees, must match exactly)
            lon: Longitude coordinate (decimal degrees, must match exactly)

        Returns:
            TTFResult: First matching result from database, or None if no match found
        """
        result = self.session.exec(
            select(TTFResult).where(
                TTFResult.latitude == lat, TTFResult.longitude == lon
            )
        )
        return result.first()

    def save(self, result: TTFResult) -> None:
        """Save a TTF result to PostgreSQL.

        Adds the result to the session, commits the transaction, and refreshes
        the instance with any database-generated values (e.g., ID, timestamps).

        Args:
            result: TTFResult instance to persist
        """
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
