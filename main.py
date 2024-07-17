from fastapi import FastAPI, status, HTTPException, Request, Response, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database_stuff import engine
from sqlmodel import Session, select
from classes import *
from datetime import datetime
from typing import Optional

CURRENT_USER = None

app = FastAPI()
app.mount("/frontend", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend")

@app.get('/')
def main(response: Response, request: Request, user_id: int | None = Cookie(default=None)):
    global CURRENT_USER
    if user_id == None:
        session = Session(bind=engine)
        ask = select(Users)
        answer = session.exec(ask).all()
        if answer:
            highest_id = answer[-1].id + 1
        else:
            highest_id = 0
        user_id = highest_id
        new_user = Users(id = highest_id)
        CURRENT_USER = user_id
        session.add(new_user)
        session.commit()
        session = Session(bind=engine)
        project_request = select(Project).where(Project.user_id == user_id)
        projects = session.exec(project_request).all()
        tasks_request = select(Task)
        tasks = session.exec(tasks_request).all()
        response = templates.TemplateResponse(
            request=request,
            name='index.html',
            context={
                'user_id': user_id,
                'projects': projects,
                'tasks': tasks
            }
        )
        response.set_cookie(key="user_id", value=user_id, httponly=True)
    else:
        CURRENT_USER = user_id
        session = Session(bind=engine)
        project_request = select(Project).where(Project.user_id == user_id)
        projects = session.exec(project_request).all()
        tasks_request = select(Task)
        tasks = session.exec(tasks_request).all()
        response = templates.TemplateResponse(
            request=request,
            name='index.html',
            context={
                'user_id': user_id,
                'projects': projects,
                'tasks': tasks
            }
        )
        response.set_cookie(key="user_id", value=user_id, httponly=True)
    return response


@app.get('/create_project/{user_id}')
def create_project(request: Request, user_id: int):
    global CURRENT_USER
    if user_id == CURRENT_USER:
        session = Session(bind=engine)
        new_project = Project(user_id = user_id, name = 'Новый проект', description = 'Описание проекта', done = 0)
        session.add(new_project)
        session.commit()
        return RedirectResponse('/')
    else:
        return RedirectResponse('/')


@app.get('/create_task/{user_id}/{project_id}')
def create_task(request: Request, user_id: int, project_id: int):
    global CURRENT_USER
    if user_id == CURRENT_USER:
        session = Session(bind=engine)
        new_task = Task(project_id = project_id, description = 'Новая задача', done = 0)
        session.add(new_task)
        session.commit()
        return RedirectResponse('/')
    else:
        return RedirectResponse('/')