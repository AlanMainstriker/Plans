from typing import Optional
from sqlmodel import Field, SQLModel, create_engine


sqlite_file_name = "tasks.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


def create_db(engine):
    SQLModel.metadata.create_all(engine)


create_db(engine)