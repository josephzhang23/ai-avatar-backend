import requests, datetime, math
import uuid as uuid_pkg

from typing import List, Union

from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException, status
from sqlmodel import select

from database.connection import get_session
from models.models import Instance, InstanceItem, Task, TaskType, TaskStyleLink, Style
from models.servers import Server
from models.package_identifier import PackageIdentifier
from routes.tasks import retrieve_active_tasks
from routes.styles import retrieve_styles

instance_router = APIRouter(
    tags=["Instances"]
)

@instance_router.get("/", response_model=List[InstanceItem])
async def retrieve_instances(user_cloud_kit_record_id: Union[str, None] = None, user_uuid: Union[uuid_pkg.UUID, None] = None, session=Depends(get_session)) -> List[InstanceItem]:
    if not user_cloud_kit_record_id and not user_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user id supplied"
        )
    statement = select(Instance).order_by(Instance.updated_at.desc())
    if user_cloud_kit_record_id:
        statement = statement.where(Instance.user_cloud_kit_record_id == user_cloud_kit_record_id)
    else:
        statement = statement.where(Instance.user_uuid == user_uuid)
    instances = session.exec(statement).all()
    # instance_items_stats = [{"uuid": instance.uuid, "avatars_count": len(instance.avatars)} for instance in instances]
    # print(f"instances: {instance_items_stats}")
    return instances

@instance_router.post("/new")
async def create_instance(images: List[UploadFile], package_identifier: PackageIdentifier = Form(None), user_cloud_kit_record_id: str = Form(None), user_uuid: uuid_pkg.UUID = Form(None), class_name: str = Form(), style_ids: List[int] = Form(None), session=Depends(get_session)):
    if not user_cloud_kit_record_id and not user_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user id supplied"
        )
    instance = Instance(user_cloud_kit_record_id=user_cloud_kit_record_id, user_uuid=user_uuid, class_name=class_name)
    session.add(instance)
    session.commit()
    session.refresh(instance)
    server_id = session.exec("SELECT server.id, (SELECT COALESCE(SUM(estimated_time), '00:00:00') FROM task WHERE task.server_id = server.id AND (task.state = 'pending' or task.state = 'started')) as t from server WHERE role = 'dreambooth' AND is_enabled = TRUE ORDER BY t LIMIT 1;").one().id
    train_task = Task(type=TaskType.train, instance_id=instance.id, server_id=server_id, estimated_time=datetime.time(0, int(len(images) * 1.5)))
    session.add(train_task)
    print(f"style ids: {style_ids}")
    if style_ids:
        statement = select(Style).where(Style.id.in_(style_ids))
        styles = session.exec(statement).all()
    else:
        styles = await retrieve_styles(class_name, 1, session)
        # print(f"styles: {styles}")
    num_images = 60 if package_identifier == "avatars-60" else 120
    num_images_per_style = math.ceil(num_images / len(styles))
    estimated_seconds_per_512_512_image = 7
    estimated_seconds = 0
    for style in styles:
        estimated_seconds += (style.width * style.height) / (512 * 512) * 1.1 * estimated_seconds_per_512_512_image * num_images_per_style
    estimated_time =  (datetime.datetime.min + datetime.timedelta(seconds=estimated_seconds)).time()
    generate_images_task = Task(type=TaskType.generate_images, instance_id=instance.id, server_id=server_id, estimated_time=estimated_time, is_model_deletion_required=True)
    session.add(generate_images_task)
    session.commit()
    session.refresh(generate_images_task)
    for style in styles:
        session.add(TaskStyleLink(task_id=generate_images_task.id, style_id=style.id, num_images=num_images_per_style))
    session.commit()
    statement = select(Server).where(Server.id == server_id)
    server = session.exec(statement).one()
    response = requests.post("http://" + server.intranet_ip + ':8000/instance/new', data = {'instance_uuid': instance.uuid}, files = [("images", (image.filename, image.file)) for image in images])
    print(response.content)
    return await retrieve_active_tasks(user_cloud_kit_record_id, user_uuid, session)