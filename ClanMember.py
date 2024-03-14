from sqlalchemy import Column, String
from main import Base


class ClanMember(Base):
    __tablename__ = "ClanMember"
