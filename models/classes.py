from typing import List

from sqlmodel import SQLModel, Field, Relationship

from models.class_style_links import ClassStyleLink

class Class(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str

    styles: List["Style"] = Relationship(back_populates="classes", link_model=ClassStyleLink)

    models: List["Model"] = Relationship(back_populates="c")