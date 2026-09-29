import datetime
import uuid as uuid_pkg

from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship, Enum
from pydantic import BaseModel

from models.servers import Server
from models.classes import Class
from models.class_style_links import ClassStyleLink

class Instance(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_cloud_kit_record_id: Optional[str]
    user_uuid: Optional[uuid_pkg.UUID]
    class_name: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, nullable=False)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, nullable=False)
    uuid: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4)

    avatars: List["Avatar"] = Relationship(back_populates="instance", sa_relationship_kwargs={"order_by": "desc(Avatar.id)"})

class InstanceItem(BaseModel):
    uuid: uuid_pkg.UUID
    updated_at: datetime.datetime

class TaskType(str, Enum):
    train = "train"
    generate_images = "generate_images"

class TaskState(str, Enum):
    pending = "pending"
    started = "started"
    success = "success"
    failure = "failure"

class TaskStyleLink(SQLModel, table=True):
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    task: "Task" = Relationship(back_populates="task_style_links")

    style_id: int = Field(foreign_key="style.id", primary_key=True)
    style: "Style" = Relationship(sa_relationship_kwargs={'foreign_keys':"[TaskStyleLink.style_id]"})

    num_images: int

class Task(SQLModel, table=True):
    id: int = Field(primary_key=True)
    type: TaskType
    state: TaskState = Field(default=TaskState.pending)
    estimated_time: datetime.time
    is_model_deletion_required: Optional[bool]
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, nullable=False)

    instance_id: int = Field(foreign_key="instance.id")
    instance: Instance = Relationship(sa_relationship_kwargs={'foreign_keys':"[Task.instance_id]"})

    server_id: int = Field(foreign_key="server.id")
    server: Server = Relationship(back_populates="tasks")

    task_style_links: List["TaskStyleLink"] = Relationship(back_populates="task")

class TaskItem(BaseModel):
    state: TaskState

class Style(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    prompt: str
    width: int
    height: int
    guidance_scale: Optional[float]
    order: Optional[int]

    pack_id: int = Field(foreign_key="pack.id")

    classes: List[Class] = Relationship(back_populates="styles", link_model=ClassStyleLink)
    avatars: List["Avatar"] = Relationship(back_populates="style")

class Avatar(SQLModel, table=True):
    id: int = Field(primary_key=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, nullable=False)
    filename: str
    width: Optional[int]
    height: Optional[int]
    
    instance_id: int = Field(foreign_key="instance.id")
    instance: Instance = Relationship(back_populates="avatars")

    style_id: int = Field(foreign_key="style.id")
    style: Style = Relationship(back_populates="avatars")

    task_id: int = Field(foreign_key="task.id")

class Model(SQLModel, table=True):
    id: int = Field(primary_key=True)

    class_id: int = Field(foreign_key="class.id")
    c: Class = Relationship(back_populates="models")