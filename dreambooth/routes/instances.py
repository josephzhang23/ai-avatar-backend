import os, shutil, uuid, asyncio

from fastapi import APIRouter, UploadFile, Form

from typing import List

from database.connection import get_session

from dreambooth.utils import get_instance_dir
from dreambooth.service import get_current_task

import dreambooth.service

instance_router = APIRouter(
    tags=["Instances"]
)


@instance_router.post("/new")
async def create_instance(images: List[UploadFile], instance_uuid: uuid.UUID = Form()):
    instance_dir = get_instance_dir(instance_uuid)
    os.makedirs(instance_dir)
    for image in images:
        with open(f"{instance_dir}/{image.filename}", "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, lambda: asyncio.run(run_task_if_free()))
    return

async def run_task_if_free():
    session = next(get_session())
    current_task = await get_current_task(session)
    session.close()
    print(f"current task: {current_task}")
    if not current_task:
        await dreambooth.service.run_task()