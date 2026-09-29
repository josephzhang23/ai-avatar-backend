from typing import Optional

from sqlmodel import SQLModel, Field

class Pack(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    order: Optional[int]