import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Load dburl
load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/todo_db"
)


# Create db engine
engine = create_engine(DATABASE_URL, echo=True)

# Generate a db session when API req is made


def get_db():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
