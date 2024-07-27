from typing import Optional
from sqlmodel import Field, SQLModel, create_engine


sqlite_url = 'mysql://sql7722457:HRt9kU4N16@sql7.freemysqlhosting.net:3306/sql7722457'
engine = create_engine(sqlite_url, echo=True, pool_size=100, max_overflow=0)


def create_db(engine):
    SQLModel.metadata.create_all(engine)


create_db(engine)