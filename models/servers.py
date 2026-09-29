from typing import List

from sqlmodel import SQLModel, Field, Enum, Relationship

class ServerRole(str, Enum):
    main = "main"
    dreambooth = "dreambooth"

class Server(SQLModel, table=True):
    id: int = Field(primary_key=True)
    intranet_ip: str
    role: ServerRole
    is_enabled: bool

    tasks: List["Task"] = Relationship(back_populates="server")