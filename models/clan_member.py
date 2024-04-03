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
