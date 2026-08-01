from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .routes import project_router, user_router, comment_router, notification_router, task_router, auth_router

app = FastAPI(
    title=settings.app_name
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.mount('/static', StaticFiles(directory=settings.static_dir), name='static')

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(user_router)
app.include_router(comment_router)
app.include_router(notification_router)
app.include_router(task_router)


@app.get('/')
def root():
    return {
        'message': 'Работает'
    }

@app.get('/health')
def health_check():
    return {'status': 'healthy'}