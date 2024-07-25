from main import app, CURRENT_USER
from fastapi.testclient import TestClient
from database_stuff import engine
from sqlmodel import Session, select
from classes import *


client = TestClient(app)


def get_id():
    session = Session(bind=engine)
    request = select(Users)
    result = session.exec(request).all()
    highest_id = result[-1].id + 1
    session.close()
    return highest_id


USER_ID = str(get_id())


def test_main_page():
    response = client.get('/')
    assert response.status_code == 200


def test_add_project(user_id=USER_ID):
    response = client.get('/create_project/' + user_id)
    assert response.status_code == 200


def test_hide_projects(user_id=USER_ID):
    response = client.get('/hideprojects/' + user_id)
    assert response.status_code == 200