from sqlmodel import SQLModel, Field, Relationship

from models.models import Style

class Example(SQLModel, table=True):
    id: int = Field(primary_key=True)

    style_id: int = Field(foreign_key="style.id")

    model_id: int = Field(foreign_key="model.id")