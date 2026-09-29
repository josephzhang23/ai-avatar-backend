import datetime
import uuid as uuid_pkg
from typing import Union, List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import select, or_, func

from database.connection import get_session
from models.models import Task, Instance, TaskItem, TaskStyleLink
from models.servers import Server

task_router = APIRouter(
    tags=["Tasks"]
)

@task_router.get("/", response_model=List[TaskItem])
async def retrieve_all_Task(session=Depends(get_session)) -> List[TaskItem]:
    statement = select(Task).where(or_(Task.state == "started", Task.state == "pending")).order_by(Task.id)
    return session.exec(statement).all()

@task_router.get("/active", response_model=List[dict])
async def retrieve_active_tasks(user_cloud_kit_record_id: Union[str, None] = None, user_uuid: Union[uuid_pkg.UUID, None] = None, session=Depends(get_session)) -> List[dict]:
    if not user_cloud_kit_record_id and not user_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user id supplied"
        )
    statement = select(Task, Instance).where(Task.instance_id == Instance.id).where(or_(Task.state == "started", Task.state == "pending")).order_by(Task.id)
    if user_cloud_kit_record_id:
        statement = statement.where(Instance.user_cloud_kit_record_id == user_cloud_kit_record_id)
    else:
        statement = statement.where(Instance.user_uuid == user_uuid)
    results = session.exec(statement).all()
    # print(results)
    tasks = [task for task, _ in results]
    task_items = []
    for task in tasks:
        estimated_datetime = datetime.datetime.min
        statement = select(Task).join(Server).where(Task.server_id == task.server_id, or_(Task.state == "started", Task.state == "pending")).order_by(Task.id)
        server_tasks = session.exec(statement).all()
        # print(server_tasks)
        for server_task in server_tasks:
            estimated_datetime += datetime.datetime.combine(datetime.date.min, server_task.estimated_time) - datetime.datetime.min
            # print(estimated_datetime)
            if task == server_task:
                break
        estimated_time_left = estimated_datetime - datetime.datetime.min
        stmt = select(func.sum(TaskStyleLink.num_images)).where(TaskStyleLink.task_id == task.id)
        num_images = session.exec(stmt).first()
        task_items.append({
            "type": task.type,
            "estimated_time_left": estimated_time_left,
            "num_images": num_images,
        })
    print(f"active tasks: {task_items}")
    return task_items
    

