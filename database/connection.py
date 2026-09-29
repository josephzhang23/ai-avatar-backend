import os
from sqlmodel import create_engine, Session

DATABASE_URL = os.environ["DATABASE_URL"]

connect_args = {
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 10,
    "keepalives_count": 5,
}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session
