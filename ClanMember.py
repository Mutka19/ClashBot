from sqlalchemy import Column, String, SmallInteger
from models import Base


class ClanMember(Base):
    __tablename__ = "clanmembers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    ranking = Column(SmallInteger)
