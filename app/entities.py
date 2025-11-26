from pydantic import BaseModel, model_validator
import uuid
from enum import Enum

class TodoTask(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    task: str
    is_done: bool
    weight: float
    
class TodoList(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    slug: str
    tasks: list[TodoTask]

class TodoListCreate(BaseModel):
    name: str

    model_config = {"from_attributes": True}

class MovePosition(str, Enum):
    BEFORE = "before"
    AFTER = "after"
    FIRST = "first"
    LAST = "last"

class TodoTaskCreate(BaseModel):
    task: str | None = None
    is_done: bool | None = None
    target_task: uuid.UUID | None = None
    move_position: MovePosition | None = None

    model_config = {"from_attributes": True}
    
    @model_validator(mode='after')
    def validate_at_least_one_field(self):
        provided_fields = [
            field for field in ['task', 'is_done', 'move_position', 'target_task', 'target_task'] 
            if getattr(self, field) is not None
        ]
        
        if not provided_fields:
            raise ValueError('At least one field must be provided for update')
        
        if self.move_position in [MovePosition.FIRST, MovePosition.LAST] and self.target_task is not None:
            raise ValueError('target_task must be None when move_position is FIRST or LAST')
        
        if self.move_position is None and self.target_task is not None:
            raise ValueError('target_task must be None when move_position is None')
        
        return self


class TodoTaskUpdate(BaseModel):
    task: str | None = None
    is_done: bool | None = None
    target_task: uuid.UUID | None = None
    move_position: MovePosition | None = None

    model_config = {"from_attributes": True}

class TodoListUpdate(BaseModel):
    name: str | None = None

    model_config = {"from_attributes": True}



