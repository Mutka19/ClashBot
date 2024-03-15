import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DATABASE_URI = os.environ.get("DATABASE_URI")
engine = create_engine(DATABASE_URI, echo=True)
Base = declarative_base()
