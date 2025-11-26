"""Repository for TodoTask entity operations."""
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.db.models import TodoTaskOrm
import uuid


class TodoTaskRepository:
    """Repository for managing TodoTask entities."""
    
    def create(
        self,
        session: Session,
        task: str,
        todo_list_id: uuid.UUID,
        is_done: bool = False,
        weight: float = 0.0
    ) -> TodoTaskOrm:
        """Create a new todo task."""
        todo_task = TodoTaskOrm(
            id=uuid.uuid4(),
            task=task,
            is_done=is_done,
            todo_list_id=todo_list_id,
            weight=weight
        )
        session.add(todo_task)
        session.flush()
        return todo_task
    
    def get_by_id(self, session: Session, task_id: uuid.UUID, with_block: bool = False) -> TodoTaskOrm | None:
        """Get todo task by ID."""
        stmt = select(TodoTaskOrm).where(TodoTaskOrm.id == task_id)
        if with_block:
            stmt = stmt.with_for_update()
        return session.execute(stmt).scalar_one_or_none()
    
    def get_by_list_id(self, session: Session, list_id: uuid.UUID, with_block: bool = False) -> list[TodoTaskOrm]:
        """Get all tasks for a todo list."""
        stmt = select(TodoTaskOrm).where(TodoTaskOrm.todo_list_id == list_id).order_by(TodoTaskOrm.weight)
        if with_block:
            stmt = stmt.with_for_update()

        return list(session.execute(stmt).scalars().all())
    
    def update(
        self,
        session: Session,
        todo_task: TodoTaskOrm,
        task: str = None,
        is_done: bool = None,
        weight: float = None
    ) -> TodoTaskOrm:
        """Update todo task."""
        if task is not None:
            todo_task.task = task
        if is_done is not None:
            todo_task.is_done = is_done
        if weight is not None:
            todo_task.weight = weight
        session.flush()
        return todo_task
    
    def delete(self, session: Session, todo_task: TodoTaskOrm) -> None:
        """Delete todo task."""
        session.delete(todo_task)
        session.flush()
    
    def delete_by_id(self, session: Session, task_id: uuid.UUID) -> bool:
        """Delete todo task by ID. Returns True if deleted, False if not found."""
        todo_task = self.get_by_id(session, task_id)
        if todo_task:
            self.delete(session, todo_task)
            return True
        return False
    
    def delete_by_list_id(self, session: Session, list_id: uuid.UUID) -> None:
        """Delete all todo tasks by list ID."""
        stmt = delete(TodoTaskOrm).where(TodoTaskOrm.todo_list_id == list_id)
        session.execute(stmt)
        session.flush()