#    Copyright 2024 Daemon Mutka
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from sqlalchemy import Column, String, ForeignKey, SmallInteger, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from repository.db_model import Base


class ClanWarAttackRecord(Base):
    __tablename__ = "clan_war_attack_records"

    id = Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    stars = Column(SmallInteger, nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)
    town_hall_diff = Column(SmallInteger, nullable=False)
    cw_player_record_id = Column(
        String, ForeignKey("clan_war_player_records.id"), nullable=False, index=True
    )
