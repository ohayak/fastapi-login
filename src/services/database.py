from typing import Any, Callable, Generator
from settings import settings
from sqlalchemy.engine.url import URL
from sqlalchemy.future import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import Engine
from sqlmodel import Session, create_engine




url = URL.create(
    drivername=settings.db_driver,
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)
engine: Engine = create_engine(url)

def get_session(commit_on_exit=True) -> Generator[Session, Any, None]:
    with sessionmaker(engine, class_=Session) as session:
        yield session
        if commit_on_exit:
            session.commit()