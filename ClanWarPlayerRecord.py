from sqlalchemy import Column, String, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
import uuid
from main import Base


class ClanWarPlayerRecord(Base):
    __tablename__ = 'ClanWarPlayerRecords'

    id = Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    attacks_used = Column(SmallInteger, nullable=False)
    stars = Column(SmallInteger, nullable=False)
    record_status = Column(String, nullable=False)
    member_id = Column(String, ForeignKey('members.id'), nullable=False, index=True)
    war_id = Column(String, ForeignKey('wars.id'), index=True)
