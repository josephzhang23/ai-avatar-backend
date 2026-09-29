import socket, uuid

from sqlmodel import Session, select

from models.models import Instance
from models.servers import Server

DATA_DIR = "/mnt/ai_avatar/data"
INSTANCE_IMAGES_DIR = DATA_DIR + "/instance_images"
OUTPUT_DIR = "/mnt/ai_avatar/stable_diffusion_outputs"

def get_class_data_dir(instance: Instance) -> str:
    return f"{DATA_DIR}/{instance.class_name}"

def get_instance_dir(instance_uuid: uuid.UUID) -> str:
    return f"{INSTANCE_IMAGES_DIR}/{instance_uuid}"

def get_weights_dir(instance: Instance) -> str:
    return f"/mnt/ai_avatar/stable_diffusion_weights/{instance.uuid}"

def get_outputs_dir(instance: Instance) -> str:
    return f"{OUTPUT_DIR}/{instance.uuid}"

async def get_current_server(session: Session) -> Server:
    intranet_ip = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
    return session.exec(select(Server).where(
        Server.intranet_ip == intranet_ip)).one()