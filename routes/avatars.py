import uuid

from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import select

from database.connection import get_session
from models.models import Avatar
from models.models import Instance

avatar_router = APIRouter(
    tags=["Avatars"]
)

@avatar_router.get("/{instance_uuid}", response_model=List[dict])
async def retrieve_avatars(instance_uuid: uuid.UUID, session=Depends(get_session)) -> List[dict]:
    statement = select(Avatar).join(Instance).where(Instance.uuid == instance_uuid).order_by(Avatar.id.desc())
    avatars = session.exec(statement).all()
    print(f"{instance_uuid} avatars count: {len(avatars)}")
    return [{
        "url": f"https://app1.aiavatar.art/avatars/{instance_uuid}/{avatar.filename}",
        "style": {
            "width": avatar.style.width,
            "height": avatar.style.height
        }
    } for avatar in avatars]