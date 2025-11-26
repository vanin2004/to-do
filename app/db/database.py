import random
from sqlalchemy import select, text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.models import Base, TodoTaskOrm, TodoListOrm
from app.db.unit_of_work import UnitOfWork
from app.core import settings
import uuid

import time

class Database:
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url, 
            echo=settings.db_echo,
            pool_size=settings.db_pool_size, 
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
        )
        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Подключение к базе данных успешно!")
        self.metadata = Base.metadata
        self.session_maker = sessionmaker(autoflush=False, bind=self.engine)
        self.__create_tables()

    def get_unit_of_work(self):
        return UnitOfWork(self.session_maker)

    def __create_tables(self):
        # self.metadata.drop_all(self.engine)
        self.metadata.create_all(self.engine)

    def test_connection(self):
        with self.session_maker() as session:
            res = session.execute(text("SELECT VERSION()"))
            print("Database version:", res.scalar())

        
    def dispose(self):
        self.engine.dispose()
