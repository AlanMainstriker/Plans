from typing import Optional
from sqlmodel import SQLModel, Field


class Project(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int
    name: str
    done: int
    hidden: int


class Task(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    project_id: int
    description: str
    done: int


class Users(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    hideprojects: int
