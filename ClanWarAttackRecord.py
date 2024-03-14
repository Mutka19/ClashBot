from sqlalchemy import Column, String, ForeignKey, SmallInteger, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from main import Base


class ClanWarAttackRecord(Base):
    __tablename__ = "ClanWarAttackRecords"

    id = Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    stars = Column(SmallInteger, nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)
    town_hall_diff = Column(SmallInteger, nullable=False)
    cw_player_record_id = Column(String, ForeignKey("ClanWarPlayerRecords.id"), nullable=False, index=True)
