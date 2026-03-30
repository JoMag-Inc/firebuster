from app.repositories.weather.weather_repository import WeatherRepository
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import create_engine, MetaData, Table, select, func, and_
from decouple import config
import pandas as pd
from datetime import datetime, timedelta, timezone

WEATHER_TABLE_NAME = "weather_data"


class SQLAlchemyWeatherRepository(WeatherRepository):
    def __init__(self):
        self.engine = create_engine(config("DATABASE_URL"))
        self.metadata = MetaData()
        self.table = Table(WEATHER_TABLE_NAME, self.metadata, autoload_with=self.engine)

    def get_connection(self):
        return self.engine

    def get_by_location(self, longitude: float, latitude: float):
        cuttoff = datetime.now(timezone.utc) - timedelta(hours=1)
        stmt = select(self.table).where(
            and_(
                self.table.c.longitude == longitude,
                self.table.c.latitude == latitude,
                self.table.created_at > cuttoff,
            )
        )

        with self.engine.connect() as conn:
            rows = conn.execute(stmt).fetchall()
            if not rows:
                return None
            df = pd.DataFrame(rows, columns=[c.name for c in self.table.columns])
            df = df.drop(columns=["longitude", "latitude", "created_at"])
            return df.to_csv(index=False)

    def add(self, weather_data: pd.DataFrame, longitude, latitude):
        df = weather_data.copy()
        df["longitude"] = longitude
        df["latitude"] = latitude
        self.add_weather_data_pd(weather_data, WEATHER_TABLE_NAME)

    def add_weather_data_pd(self, df_weather: pd.DataFrame, table_name):
        engine = self.get_connection()
        records = df_weather.to_dict(orient="records")
        stmt = insert(WEATHER_TABLE_NAME).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=["longitude", "latitude", "timestamp"],
            set_={
                "temperature": stmt.excluded.temperature,
                "humidity": stmt.excluded.humidity,
                "wind_speed": stmt.excluded.wind_speed,
                "created_at": func.now(),
            },
        )

        with engine.begin() as conn:
            conn.execute(stmt)
