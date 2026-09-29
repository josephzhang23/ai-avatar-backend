import asyncio

from fastapi import FastAPI

from database.connection import get_session
from dreambooth.routes.instances import instance_router
from dreambooth.service import run_task

import uvicorn

app = FastAPI()

# Register routes

app.include_router(instance_router, prefix="/instance")

@app.on_event("startup")
async def on_startup():
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, lambda: asyncio.run(run_task()))

if __name__ == '__main__':
    uvicorn.run("dreambooth_main:app", host="0.0.0.0")