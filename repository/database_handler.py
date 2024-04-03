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

from sqlalchemy.orm import sessionmaker
from repository.db_model import engine


class DatabaseHandler:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def add_object(self, obj):
        self.session.add(obj)

    def rollback(self):
        self.session.rollback()

    def commit(self):
        self.session.commit()

    def delete(self, obj):
        self.session.delete(obj)

    def flush(self):
        self.session.flush()

    def query(self, model):
        return self.session.query(model)

    def close(self):
        self.session.close()
