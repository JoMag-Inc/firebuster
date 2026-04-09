from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime


class TTFResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    latitude: float
    longitude: float
    calculated_at: datetime
    ttf_points: list = Field(sa_column=Column(JSON))
