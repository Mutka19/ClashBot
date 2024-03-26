from sqlalchemy import Column, String, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
import uuid
from repository.db_model import Base


class ClanWarPlayerRecord(Base):
    __tablename__ = "clan_war_player_records"

    id = Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    attacks_used = Column(SmallInteger, nullable=False)
    stars = Column(SmallInteger, nullable=False)
    record_status = Column(String, nullable=False)
    war_id = Column(String, index=True)
    member_id = Column(String, ForeignKey("clan_members.id"), nullable=False, index=True)
