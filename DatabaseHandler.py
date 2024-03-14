from sqlalchemy.orm import sessionmaker
from models import engine


class DatabaseHandler:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def add_object(self, obj):
        self.session.add(obj)

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()

