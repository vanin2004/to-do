import uuid
from fastapi import APIRouter, Depends

from app.entities import TodoList, TodoTask, TodoListCreate, TodoTaskCreate, TodoTaskUpdate, TodoListUpdate
from app.todo_service import TodoService

from app.di import get_todo_service

router = APIRouter()

@router.post("/lists/")
async def create_list(list: TodoListCreate, todo_service: TodoService= Depends(get_todo_service)) -> TodoList:
    """
    Создать пустой список.
    Возвращает созданный список
    """
    return todo_service.create_todo_list(list)

@router.get("/lists/{slug}")
async def get_list_by_slug(slug: str, todo_service: TodoService = Depends(get_todo_service)) -> TodoList:
    """
    Получить список по slug.
    Возвращает найденный список или ошибку, если список не найден.
    """
    return todo_service.get_todo_list_by_slug(slug)

@router.delete("/lists/{slug}")
async def delete_list(slug: str, todo_service: TodoService = Depends(get_todo_service)) -> dict:
    """
    Удалить список по slug.
    Возвращает результат удаления в виде {"success": true/false}. либо ошибку, если список не найден.
    """
    result = todo_service.delete_todo_list(slug)
    return {"success": result}

@router.put("/lists/{slug}")
async def update_list(slug: str, list: TodoListUpdate, todo_service: TodoService = Depends(get_todo_service)) -> TodoList:
    """
    Обновить список по slug.
    Возвращает обновленный список или ошибку, если список не найден.
    """
    return todo_service.update_todo_list(slug, list)
    
@router.post("/lists/{slug}/tasks")
async def add_task_to_list(slug: str, task: TodoTaskCreate, todo_service: TodoService = Depends(get_todo_service)) -> TodoTask:
    """
    Добавить задачу в список по slug.
    Возвращает созданную задачу или ошибку, если список не найден.
    """
    return todo_service.create_todo_task(slug, task)

@router.delete("/lists/{slug}/tasks/{task_id}")
async def delete_task_from_list(slug: str, task_id: uuid.UUID, todo_service: TodoService = Depends(get_todo_service)) -> dict:
    """
    Удалить задачу из списка по slug и task_id.
    Возвращает результат удаления в виде {"success": true/false}. либо ошибку, если список или задача не найдены.
    """
    return {"success": todo_service.delete_todo_task(slug, task_id)}

@router.put("/lists/{slug}/tasks/{task_id}")
async def update_task_in_list(slug: str, task_id: uuid.UUID, task: TodoTaskUpdate, todo_service: TodoService = Depends(get_todo_service)) -> TodoTask:
    """
    Обновить задачу в списке по slug и task_id.
    Возвращает обновленную задачу или ошибку, если список или задача не найдены.
    """
    return todo_service.update_todo_task(slug, task_id, task) 