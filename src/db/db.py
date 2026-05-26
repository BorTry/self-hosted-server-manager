import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

print(__file__)

load_dotenv("./.env")
DATABASE_URL = os.environ.get("DATABASE_URL")

if (not DATABASE_URL):
    print(DATABASE_URL)
    raise Exception()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)