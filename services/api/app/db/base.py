"""SQLAlchemy declarative base."""

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    # Store all datetimes as timezone-aware (TIMESTAMP WITH TIME ZONE on
    # Postgres). Models default to timezone-aware UTC values, and asyncpg
    # refuses to bind an aware datetime to a naive TIMESTAMP column.
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }
