from fastapi import FastAPI, status, HTTPException, Request, Response, Cookie, Form
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


def check_user(user_id):
    session = Session(bind=engine)
    request = select(Users).where(Users.id == user_id)
    result = session.exec(request).all()
    if result == []:
        return False
    else:
        return True


def check_project(user_id, project_id):
    session = Session(bind=engine)
    request = select(Project).where(Project.id == project_id)
    result = session.exec(request).all()
    print(result)
    if result == []:
        return False
    else:
        return True


def check_task(user_id, project_id, task_id):
    session = Session(bind=engine)
    request = select(Task).where(Task.id == task_id)
    result = session.exec(request).all()
    if result == []:
        return False
    else:
        return True

@app.get('/')
async def main(response: Response, request: Request, user_id: int | None = Cookie(default=None)):
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
        new_user = Users(id = highest_id, hideprojects = 0)
        CURRENT_USER = user_id
        session.add(new_user)
        session.commit()
        session = Session(bind=engine)
        user_request = select(Users).where(Users.id == user_id)
        user = session.exec(user_request).one()
        hide = user.hideprojects
        project_request = select(Project).where(Project.user_id == user_id)
        projects = session.exec(project_request).all()
        tasks_request = select(Task)
        tasks = session.exec(tasks_request).all()
        session.close()
        response = templates.TemplateResponse(
            request=request,
            name='index.html',
            context={
                'hideprojects': hide,
                'user_id': user_id,
                'projects': projects,
                'tasks': tasks
            }
        )
        response.set_cookie(key="user_id", value=user_id)
    else:
        CURRENT_USER = user_id
        session = Session(bind=engine)
        user_request = select(Users).where(Users.id == user_id)
        user = session.exec(user_request).one()
        if user.hideprojects == 0:
            project_request = select(Project).where(Project.user_id == user_id)
            projects = session.exec(project_request).all()
            tasks_request = select(Task)
            tasks = session.exec(tasks_request).all()
        else:
            project_request = select(Project).where(Project.user_id == user_id).where(Project.done == 0)
            projects = session.exec(project_request).all()
            tasks_request = select(Task)
            tasks = session.exec(tasks_request).all()
        session.close()
        response = templates.TemplateResponse(
            request=request,
            name='index.html',
            context={
                'hideprojects': user.hideprojects,
                'user_id': user_id,
                'projects': projects,
                'tasks': tasks
            }
        )
        response.set_cookie(key="user_id", value=user_id)
    return response


@app.get('/create_project/{user_id}')
async def create_project(request: Request, user_id: int):
    global CURRENT_USER
    if user_id == None:
        return RedirectResponse('/')
    if user_id == CURRENT_USER:
        session = Session(bind=engine)
        new_project = Project(user_id = user_id, name = 'Новый проект', description = 'Описание проекта', done = 0, hidden = 0)
        session.add(new_project)
        session.commit()
        session.close()
        return RedirectResponse('/')
    else:
        return RedirectResponse('/')


@app.get('/create_task/{user_id}/{project_id}')
async def create_task(request: Request, user_id: int, project_id: int):
    global CURRENT_USER
    if user_id == CURRENT_USER:
        if check_project(user_id, project_id):
            session = Session(bind=engine)
            ask = select(Project).where(Project.id == project_id)
            result = session.exec(ask).one()
            if result.user_id == user_id:
                new_task = Task(project_id=project_id, description='Новая задача', done=0)
                session.add(new_task)
                session.commit()
                result.done = 0
                session.add(result)
                session.commit()
                session.refresh(result)
            session.close()
            return RedirectResponse('/')
        else:
            return RedirectResponse('/')
    else:
        return RedirectResponse('/')


@app.get('/edittaskdesc/{user_id}/{project_id}/{task_id}')
async def edit_task(request: Request, user_id: int, project_id: int, task_id: int, newdesc=None):
    global CURRENT_USER
    if user_id == CURRENT_USER:
        if check_user(user_id) and check_task(user_id, project_id, task_id) and check_project(user_id, project_id):
            session = Session(bind=engine)
            task_request = select(Task).where(Task.id == task_id)
            task = session.exec(task_request).all()
            task_project = task[0].project_id
            project_request = select(Project).where(Project.id == project_id)
            project = session.exec(project_request).all()
            project_user = project[0].user_id
            if task_project == project_id and project_user == user_id:
                newdesc = str(newdesc)
                if newdesc.lstrip().rstrip() != '':
                    session = Session(bind=engine)
                    task_request = select(Task).where(Task.id == task_id)
                    task = session.exec(task_request).one()
                    task.description = newdesc
                    session.add(task)
                    session.commit()
                    session.refresh(task)
                    session.close()
                return RedirectResponse('/')
            else:
                return RedirectResponse('/')
    return RedirectResponse('/')


@app.get('/editprojectname/{user_id}/{project_id}')
async def edit_project(request: Request, user_id: int, project_id: int, newname=None):
    global CURRENT_USER
    if user_id == CURRENT_USER:
        if check_user(user_id) and check_project(user_id, project_id):
            session = Session(bind=engine)
            project_request = select(Project).where(Project.id == project_id)
            project = session.exec(project_request).one()
            if project.user_id == user_id:
                newname = str(newname)
                if newname.rstrip().lstrip() != '':
                    project.name = newname
                    session.add(project)
                    session.commit()
                    session.refresh(project)
                return RedirectResponse('/')
            session.close()
        else:
            return RedirectResponse('/')
    else:
        return RedirectResponse('/')


@app.get('/deletetask/{user_id}/{project_id}/{task_id}')
async def delete_task(request: Request, user_id: int, project_id: int, task_id: int):
    global CURRENT_USER
    if CURRENT_USER == user_id:
        if check_user(user_id) and check_task(user_id, project_id, task_id) and check_project(user_id, project_id):
            session = Session(bind=engine)
            task_request = select(Task).where(Task.id == task_id)
            task = session.exec(task_request).one()
            task_project = task.project_id
            project_request = select(Project).where(Project.id == project_id)
            project = session.exec(project_request).all()
            project_user = project[0].user_id
            if task_project == project_id and project_user == user_id:
                session.delete(task)
                session.commit()
                session.close()
                session = Session(bind=engine)
                ask1 = select(Task).where(Task.project_id == project_id)
                ask2 = select(Task).where(Task.project_id == project_id).where(Task.done == 1)
                result1 = session.exec(ask1).all()
                result2 = session.exec(ask2).all()
                session.close()
                if result1 == result2:
                    session = Session(bind=engine)
                    ask = select(Project).where(Project.id == project_id)
                    result = session.exec(ask).one()
                    result.done = 1
                    session.add(result)
                    session.commit()
                    session.refresh(result)
                    session.close()
                if result1 != result2:
                    session = Session(bind=engine)
                    ask = select(Project).where(Project.id == project_id)
                    result = session.exec(ask).one()
                    result.done = 0
                    session.add(result)
                    session.commit()
                    session.refresh(result)
                    session.close()
                return RedirectResponse('/')
            else:
                session.close()
                return RedirectResponse('/')
    return RedirectResponse('/')


@app.get('/deleteproject/{user_id}/{project_id}')
async def delete_project(request: Request, user_id: int, project_id: int):
    global CURRENT_USER
    if user_id == CURRENT_USER:
        if check_user(user_id) and check_project(user_id, project_id):
            session = Session(bind=engine)
            project_request = select(Project).where(Project.id == project_id)
            project = session.exec(project_request).one()
            if project.user_id == user_id:
                session.delete(project)
                task_request = select(Task).where(Task.project_id == project_id)
                tasks = session.exec(task_request).all()
                for task in tasks:
                    session.delete(task)
                    session.commit()
                session.commit()
                session.close()
                return RedirectResponse('/')
        else:
            return RedirectResponse('/')
    else:
        return RedirectResponse('/')


@app.get('/taskdone/{user_id}/{project_id}/{task_id}')
async def task_done(request: Request, user_id: int, project_id: int, task_id: int):
    global CURRENT_USER
    if user_id == CURRENT_USER:
        if check_user(user_id) and check_task(user_id, project_id, task_id) and check_project(user_id, project_id):
            session = Session(bind=engine)
            task_request = select(Task).where(Task.id == task_id)
            task = session.exec(task_request).one()
            task_project = task.project_id
            project_request = select(Project).where(Project.id == project_id)
            project = session.exec(project_request).one()
            project_user = project.user_id
            if task_project == project_id and project_user == user_id:
                if task.done == 0:
                    task.done = 1
                    session.add(task)
                    session.commit()
                    session.refresh(task)
                elif task.done == 1:
                    task.done = 0
                    session.add(task)
                    session.commit()
                    session.refresh(task)
                session.close()
                session = Session(bind=engine)
                ask1 = select(Task).where(Task.project_id == project_id)
                ask2 = select(Task).where(Task.project_id == project_id).where(Task.done == 1)
                result1 = session.exec(ask1).all()
                result2 = session.exec(ask2).all()
                session.close()
                if result1 == result2:
                    session = Session(bind=engine)
                    ask = select(Project).where(Project.id == project_id)
                    result = session.exec(ask).one()
                    result.done = 1
                    session.add(result)
                    session.commit()
                    session.refresh(result)
                    session.close()
                if result1 != result2:
                    session = Session(bind=engine)
                    ask = select(Project).where(Project.id == project_id)
                    result = session.exec(ask).one()
                    result.done = 0
                    session.add(result)
                    session.commit()
                    session.refresh(result)
                    session.close()
                return RedirectResponse('/')
            else:
                return RedirectResponse('/')
    return RedirectResponse('/')


@app.get('/hideprojects/{user_id}')
async def hide_projects(request: Request, user_id: int):
    global CURRENT_USER
    if user_id == CURRENT_USER:
        if check_user(user_id):
            session = Session(bind=engine)
            user_request = select(Users).where(Users.id == user_id)
            user = session.exec(user_request).one()
            if user.hideprojects == 0:
                user.hideprojects = 1
                session.add(user)
                session.commit()
                session.refresh(user)
            elif user.hideprojects == 1:
                user.hideprojects = 0
                session.add(user)
                session.commit()
                session.refresh(user)
            session.close()
            return RedirectResponse('/')
        else:
            return RedirectResponse('/')
    else:
        return RedirectResponse('/')


@app.get('/hidetasks/{user_id}/{project_id}')
async def hide_tasks(request: Request, user_id: int, project_id: int):
    global CURRENT_USER
    if user_id == CURRENT_USER:
        if check_user(user_id) and check_project(user_id, project_id):
            session = Session(bind=engine)
            project_req = select(Project).where(Project.id == project_id)
            project = session.exec(project_req).one()
            if project.user_id == user_id:
                if project.hidden == 0:
                    project.hidden = 1
                    session.add(project)
                    session.commit()
                    session.refresh(project)
                elif project.hidden == 1:
                    project.hidden = 0
                    session.add(project)
                    session.commit()
                    session.refresh(project)
                return RedirectResponse('/')
            session.close()
            return RedirectResponse('/')
    return RedirectResponse('/')