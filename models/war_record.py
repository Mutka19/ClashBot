from sqlalchemy import Column, String, DateTime
from repository.db_model import Base


class WarRecord(Base):
    __tablename__ = "war_records"

    id = Column(String, primary_key=True)
    end_time = Column(DateTime, nullable=False)
    result = Column(String)
