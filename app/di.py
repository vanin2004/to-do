from fastapi import Depends
from functools import lru_cache

from app.core import settings

from app.slug_service import SlugService
from app.weight_service import WeightService
from app.todo_service import TodoService
from app.db.unit_of_work import UnitOfWork
from app.db.database import Database

@lru_cache()
def get_database()-> Database:
    return Database(settings.database_url)

def get_unit_of_work(db = Depends(get_database)) -> UnitOfWork:
    return db.get_unit_of_work()

def get_slug_service() -> SlugService:
    return SlugService()

def get_weight_service() -> WeightService:
    return WeightService()

def get_todo_service(uow: UnitOfWork = Depends(get_unit_of_work),
                     slug_service: SlugService = Depends(get_slug_service),
                     weight_service: WeightService = Depends(get_weight_service)) -> TodoService:
    return TodoService(uow=uow, slug_service=slug_service, weight_service=weight_service)