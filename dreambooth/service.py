import os, subprocess, shutil, datetime

from typing import Optional

from sqlmodel import Session, select

from database.connection import get_session
from dreambooth.utils import get_current_server, get_weights_dir, OUTPUT_DIR, get_instance_dir
from models.models import Task, TaskType

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, EulerAncestralDiscreteScheduler

async def get_current_task(session: Session) -> Optional[Task]:
    server = await get_current_server(session)
    statement = select(Task).where(Task.server_id == server.id, Task.state == "started").order_by(Task.id)
    task = session.exec(statement).first()
    return task

async def get_next_task(session: Session) -> Optional[Task]:
    server = await get_current_server(session)
    statement = select(Task).where(Task.server_id == server.id, Task.state == "pending").order_by(Task.id)
    return session.exec(statement).first()

async def run_task():
    session = next(get_session())
    task = await get_current_task(session)
    if not task:
        task = await get_next_task(session)
    print(task)
    if task:
        instance = task.instance
        task.state = "started"
        session.add(task)
        session.commit()
        if task.type == TaskType.train:
            command = f"python train.py --instance_id=\"{instance.id}\""
            subprocess.run(command, shell=True)
        else:
            command = f"python generate_images.py --instance_id=\"{instance.id}\" --task_id=\"{task.id}\""
            subprocess.run(command, shell=True)
            weights_path = get_weights_dir(instance)
            if os.listdir(weights_path):
                if task.is_model_deletion_required:
                    shutil.rmtree(weights_path)
                shutil.rmtree(get_instance_dir(instance.uuid))
        task.state = "success"
        task.updated_at = datetime.datetime.utcnow()
        session.add(task)
        instance = task.instance
        instance.updated_at = datetime.datetime.utcnow()
        session.add(instance)
        session.commit()
        session.close()
        await run_task()
    else:
        session.close()