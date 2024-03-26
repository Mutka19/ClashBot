from sqlalchemy import Column, String, SmallInteger, Integer, Numeric
from repository.db_model import Base


class ClanMember(Base):
    __tablename__ = "clan_members"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    position = Column(String, nullable=False)
    ranking = Column(SmallInteger)
    efficiency = Column(Numeric(5, 2), default=0.00)
    participation = Column(Numeric(5, 2), default=100.00)
