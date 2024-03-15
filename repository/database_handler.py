from sqlalchemy.orm import sessionmaker
from db_model import engine


class DatabaseHandler:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def add_object(self, obj):
        self.session.add(obj)

    def commit(self):
        self.session.commit()

    def query(self, model):
        return self.session.query(model)

    def close(self):
        self.session.close()

