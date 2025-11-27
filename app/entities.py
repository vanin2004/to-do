from pydantic import BaseModel, Field, model_validator
import uuid
from enum import Enum

class TodoTask(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID = Field(description="Уникальный идентификатор задачи")
    task: str = Field(description="Текст задачи")
    is_done: bool = Field(description="Статус выполнения задачи")
    weight: float = Field(description="Вес задачи для упорядочивания (чем меньше вес, тем выше задача в списке)")
    
class TodoList(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID = Field(description="Уникальный идентификатор списка")
    name: str = Field(description="Название списка")
    slug: str = Field(description="Уникальный слаг списка для доступа")
    tasks: list[TodoTask] = Field(description="Список задач")

class TodoListCreate(BaseModel):
    name: str = Field(description="Название списка")

    model_config = {"from_attributes": True}

from pydantic import Field
from enum import Enum

class MovePosition(str, Enum):
    """Позиция перемещения задачи в списке"""
    
    BEFORE = Field("before", description="Поместить перед указанной задачей")
    AFTER = Field("after", description="Поместить после указанной задачи")
    FIRST = Field("first", description="Поместить в начало списка")
    LAST = Field("last", description="Поместить в конец списка")

class TodoTaskCreate(BaseModel):
    task: str = Field(default= "", description="Текст задачи")   
    is_done: bool | None = Field(default=None, description="Статус выполнения задачи")
    target_task: uuid.UUID | None = Field(default=None, description="Идентификатор задачи для позиционирования")
    move_position: MovePosition | None = Field(default=None, description="Позиция перемещения задачи в списке")

    model_config = {"from_attributes": True}
    
    @model_validator(mode='after')
    def validate_at_least_one_field(self):
        if self.move_position and self.move_position in [MovePosition.FIRST, MovePosition.LAST] and self.target_task is not None:
            raise ValueError('target_task must be None when move_position is FIRST or LAST')
        
        if self.move_position is None and self.target_task is not None:
            raise ValueError('target_task must be None when move_position is None')
        
        return self


class TodoTaskUpdate(BaseModel):
    task: str | None = Field(default=None, description="Текст задачи")
    is_done: bool | None = Field(default=None, description="Статус выполнения задачи")
    target_task: uuid.UUID | None = Field(default=None, description="Идентификатор задачи для позиционирования")
    move_position: MovePosition | None = Field(default=None, description="Позиция перемещения задачи в списке")

    model_config = {"from_attributes": True}

    @model_validator(mode='after')
    def validate_at_least_one_field(self):
        provided_fields = [
            field for field in ['task', 'is_done', 'move_position', 'target_task'] 
            if getattr(self, field) is not None
        ]
        
        if not provided_fields:
            raise ValueError('At least one field must be provided for update')
        
        if self.move_position and self.move_position in [MovePosition.FIRST, MovePosition.LAST] and self.target_task is not None:
            raise ValueError('target_task must be None when move_position is FIRST or LAST')
        
        if self.move_position is None and self.target_task is not None:
            raise ValueError('target_task must be None when move_position is None')
        
        return self

class TodoListUpdate(BaseModel):
    name: str | None = Field(default=None, description="Название списка")

    model_config = {"from_attributes": True}



