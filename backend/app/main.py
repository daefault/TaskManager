from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from .config import settings
from fastapi.templating import Jinja2Templates
from .routes import project_router, user_router, comment_router, notification_router, task_router, auth_router

app = FastAPI(
    title=settings.app_name
)

app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router, prefix='/api')
app.include_router(project_router, prefix='/api')
app.include_router(user_router, prefix='/api')
app.include_router(comment_router, prefix='/api')
app.include_router(notification_router, prefix='/api')
app.include_router(task_router, prefix='/api')


@app.get('/')
def home(request: Request):
    return templates.TemplateResponse(request=request, name="base.html")

@app.get('/projects')
def projects_page(request: Request):
    return templates.TemplateResponse(request=request, name="projects.html")

@app.get('/projects/{project_id}')
def project_detail_page(request: Request):
    return templates.TemplateResponse(request=request, name='project_detail.html')

@app.get('/projects/{project_id}/tasks')
def project_tasks_page(request: Request):
    return templates.TemplateResponse(request=request, name='project_tasks.html')

@app.get('/register')
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name='register.html')

@app.get('/tasks/{task_id}')
def task_detail_page(request: Request):
    return templates.TemplateResponse(request=request, name='task_detail.html')

@app.get('/notifications')
def notifications_page(request: Request):
    return templates.TemplateResponse(request=request, name='notifications.html')

@app.get('/health')
def health_check():
    return {'status': 'healthy'}
