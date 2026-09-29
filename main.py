import argparse

from fastapi import FastAPI

from routes.styles import style_router
from routes.instances import instance_router
from routes.avatars import avatar_router
from routes.tasks import task_router

import uvicorn

app = FastAPI()

# Register routes

app.include_router(style_router, prefix="/style")
app.include_router(instance_router, prefix="/instance")
app.include_router(avatar_router, prefix="/avatar")
app.include_router(task_router, prefix="/task")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--test", 
    action='store_true'
)
args = parser.parse_args()

if __name__ == '__main__':
    if args.test:
        uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
    else:
        uvicorn.run("main:app", host="0.0.0.0", reload=True)