from fastapi import APIRouter
from fastapi.responses import FileResponse

model_router = APIRouter(
    tags=["Models"]
)

@model_router.get("/{model_id}/{image_id}")
async def retrieve_model_image(model_id: int, image_id: int):
    return FileResponse(f"/mnt/ai_avatar/models/{model_id}/{image_id}.jpg")