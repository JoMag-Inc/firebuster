from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime


class TTFResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    latitude: float
    longitude: float
    calculated_at: datetime
    ttf_minutes: list = Field(sa_column=Column(JSON))
    weather_input: list = Field(sa_column=Column(JSON))
