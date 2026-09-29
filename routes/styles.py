from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlmodel import select, or_

from database.connection import get_session
from models.models import Style, Model
from models.packs import Pack
from models.classes import Class
from models.class_style_links import ClassStyleLink
from models.examples import Example

style_router = APIRouter(
    tags=["Styles"]
)


@style_router.get("/", response_model=List[dict])
async def retrieve_all_Style(session=Depends(get_session)) -> List[dict]:
    statement = select(Style).join(Pack).order_by(
        Pack.order, Pack.id, Style.order, Style.id)
    styles = session.exec(statement).all()
    return [{
        "id": style.id,
        "name": style.name,
        "is_default": style.pack_id == 1,
        "classes": [{
            "name": c.name
        } for c in style.classes]
    } for style in styles]

# @style_router.get("/{class_name}/{pack_id}", response_model=List[Style])


async def retrieve_styles(class_name: str, pack_id: Optional[int], session=Depends(get_session)) -> List[Style]:
    statement = select(Style, Class, ClassStyleLink).where(ClassStyleLink.class_id == Class.id,
                                                           ClassStyleLink.style_id == Style.id).where(Class.name == class_name).order_by(Style.order, Style.id)
    if pack_id:
        statement = statement.where(Style.pack_id == pack_id)
    results = session.exec(statement).all()
    return [result[0] for result in results]

# @style_router.get("/example", response_model=List[dict])
# async def retrieve_all_example_Style(session=Depends(get_session))-> List[dict]:
#     examples = {}
#     statement = select(Style, ClassStyleLink, Class).where(ClassStyleLink.style_id == Style.id, ClassStyleLink.class_id == Class.id, or_(Class.name == "man", Class.name == "woman")).join(Pack).order_by(Class.name.desc(), Pack.order, Pack.id, Style.order, Style.id)
#     results = session.exec(statement).all()
#     for style, _, style_class in results:
#         if style.name in examples:
#             examples[style.name].append(f"https://app1.aiavatar.art/styles/examples/{style.id}/{style_class.name}.png")
#         else:
#             examples[style.name] = [f"https://app1.aiavatar.art/styles/examples/{style.id}/{style_class.name}.png"]
#     return [{
#         "name": k,
#         "images": v
#         } for k, v in examples.items()]


@style_router.get("/example", response_model=List[dict])
async def retrieve_all_style_examples(session=Depends(get_session)) -> List[dict]:
    statement = select(Example, Style, Model).where(
        Example.style_id == Style.id, Example.model_id == Model.id).order_by(Example.id)
    results = session.exec(statement).all()
    style_examples = {}
    for example, style, model in results:
        exampleItem = {
            "url": f"https://app1.aiavatar.art/examples/{example.id}.png",
            "width": style.width,
            "height": style.height,
            "model": {
                "class": {
                    "name": model.c.name,
                },
                "images": [
                    f"https://app1.aiavatar.art/models/{model.id}/1_300.jpg"
                ]
            }
        }
        if style.name in style_examples:
            style_examples[style.name].append(exampleItem)
        else:
            style_examples[style.name] = [exampleItem]
    return [{
        "name": k,
        "examples": v
    } for k, v in style_examples.items()]
