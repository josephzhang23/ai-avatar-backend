from sqlmodel import SQLModel, Field

class ClassStyleLink(SQLModel, table=True):
    class_id: int = Field(foreign_key="class.id", primary_key=True)
    style_id: int = Field(foreign_key="style.id", primary_key=True)