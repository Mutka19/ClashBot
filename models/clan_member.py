from sqlalchemy import Column, String, SmallInteger, Integer, Numeric
from repository.db_model import Base


class ClanMember(Base):
    __tablename__ = "clanmembers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    ranking = Column(SmallInteger)
    efficiency = Column(Numeric(5, 2), default=100.00)
    participation = Column(Numeric(5, 2), default=100.00)
