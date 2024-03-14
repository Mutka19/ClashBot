from sqlalchemy import Column, String, SmallInteger
from main import Base


class ClanMember(Base):
    __tablename__ = "ClanMembers"

    id = Column(String, primary_key=True)
    position = Column(String, nullable=False)
    ranking = Column(SmallInteger)
