import uuid
from app.db.database import Database
from app.db.models import TodoTaskOrm, TodoListOrm
from app.db.unit_of_work import UnitOfWork
from app.entities import TodoList, TodoTask, TodoListCreate, TodoListUpdate, TodoTaskCreate, TodoTaskUpdate
from app.weight_service import WeightService
from app.slug_service import SlugService

from app.exceptions import TodoListNotFoundException, TodoTaskNotFoundException


class TodoService:
    def __init__(self, 
                 uow: UnitOfWork,
                 slug_service: SlugService,
                 weight_service: WeightService):
        self.uow = uow
        self.slug_service = slug_service
        self.weight_service = weight_service


    def create_todo_list(self, todo_list_create: TodoListCreate) -> TodoList:
        with self.uow as uow:
            todo_list_orm: TodoListOrm = uow.todo_lists.get_one_free(uow.session)
            if todo_list_orm is None:
                attempts = 5
                for _ in range(attempts):
                    slug = self.slug_service.generate_slug()
                    try:
                        todo_list_orm = uow.todo_lists.create(uow.session, slug=slug, name=todo_list_create.name, is_free=False)
                        break
                    except Exception:
                        continue
                else:
                    raise Exception("Failed to create a unique slug for the todo list after multiple attempts.")
            else:
                uow.todo_lists.update(uow.session, todo_list_orm, name=todo_list_create.name, is_free=False)
            todo_list = TodoList.model_validate(todo_list_orm)
            uow.commit()
        return todo_list
    

    def get_todo_list_by_slug(self, slug: str) -> TodoList:
        with self.uow as uow:
            todo_list_orm = uow.todo_lists.get_by_slug(uow.session, slug, with_tasks=True)
            if todo_list_orm is None or todo_list_orm.is_free:
                raise TodoListNotFoundException(f"Todo list with slug '{slug}' not found.")
            todo_list = TodoList.model_validate(todo_list_orm)
        return todo_list
    
    def update_todo_list(self, todo_list_slug: str, todo_list_update: TodoListUpdate) -> TodoList:
        with self.uow as uow:
            todo_list_orm = uow.todo_lists.get_by_slug(uow.session, todo_list_slug, with_block=True)
            if todo_list_orm is None:
                raise TodoListNotFoundException(f"Todo list with slug '{todo_list_slug}' not found.")
            uow.todo_lists.update(session = uow.session, todo_list = todo_list_orm, name = todo_list_update.name)
            todo_list = TodoList.model_validate(todo_list_orm)
            uow.commit()
        return todo_list
    
    def delete_todo_list(self, todo_list_slug: str) -> bool:
        with self.uow as uow:
            todo_list_orm = uow.todo_lists.get_by_slug(uow.session, todo_list_slug, with_block=True)
            if todo_list_orm is None:
                raise TodoListNotFoundException(f"Todo list with slug '{todo_list_slug}' not found.")
            uow.todo_lists.free(uow.session, todo_list_orm)
            result = uow.todo_tasks.delete_by_list_id(uow.session, todo_list_orm.id)
            uow.commit()
        return result
    
    def create_todo_task(self, todo_list_slug: str, todo_task_create: TodoTaskCreate) -> TodoTask:
        with self.uow as uow:
            todo_list_orm = uow.todo_lists.get_by_slug(uow.session, todo_list_slug, with_block=True)
            if todo_list_orm is None or todo_list_orm.is_free:
                raise TodoListNotFoundException(f"Todo list with slug '{todo_list_slug}' not found.")
            todo_list = TodoList.model_validate(todo_list_orm)

            weight = self.weight_service.calculate_weight(
                todo_list,
                todo_task_create.move_position,
                todo_task_create.target_task
            )
            todo_task_orm: TodoTaskOrm = uow.todo_tasks.create(uow.session, todo_list_id=todo_list_orm.id, task=todo_task_create.task, weight=weight, is_done=todo_task_create.is_done)
            todo_task = TodoTask.model_validate(todo_task_orm)
            uow.commit()
        return todo_task
    
    def delete_todo_task(self, todo_list_slug: str, todo_task_id: uuid.UUID) -> bool:
        with self.uow as uow:
            todo_list_orm = uow.todo_lists.get_by_slug(uow.session, todo_list_slug, with_block=True)
            if todo_list_orm is None or todo_list_orm.is_free:
                raise TodoListNotFoundException(f"Todo list with slug '{todo_list_slug}' not found.")
            todo_task_orm = uow.todo_tasks.get_by_id(uow.session, todo_task_id, with_block=True)
            if todo_task_orm is None:
                raise TodoTaskNotFoundException(f"Todo task with id '{todo_task_id}' not found.")
            result = uow.todo_tasks.delete(uow.session, todo_task_orm)
            uow.commit()
        return result
    
    def update_todo_task(self, todo_list_slug: str, todo_task_id: uuid.UUID, todo_task_update: TodoTaskUpdate) -> TodoTask:
        with self.uow as uow:
            todo_list_orm = uow.todo_lists.get_by_slug(uow.session, todo_list_slug, with_block=True)
            if todo_list_orm is None or todo_list_orm.is_free:
                raise TodoListNotFoundException(f"Todo list with slug '{todo_list_slug}' not found.")
            todo_list = TodoList.model_validate(todo_list_orm)

            todo_task_orm = uow.todo_tasks.get_by_id(uow.session, todo_task_id, with_block=True)
            if todo_task_orm is None:
                raise TodoTaskNotFoundException(f"Todo task with id '{todo_task_id}' not found.")
            if todo_task_update.move_position is not None:
                weight = self.weight_service.calculate_weight(
                    todo_list,
                    todo_task_update.move_position,
                    todo_task_update.target_task,
                    moving_task_id=todo_task_id
                )
            else:
                weight = None
            todo_task_orm: TodoTaskOrm = uow.todo_tasks.update(uow.session, todo_task_orm, task=todo_task_update.task, is_done=todo_task_update.is_done, weight=weight)
            todo_task = TodoTask.model_validate(todo_task_orm)
            uow.commit()
        return todo_task
    