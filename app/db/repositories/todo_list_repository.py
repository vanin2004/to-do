"""Repository for TodoList entity operations."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import TodoListOrm
import uuid


class TodoListRepository:
    """Repository for managing TodoList entities."""
    
    def create(self, session: Session, name: str, slug: str, is_free: bool = True) -> TodoListOrm:
        """Create a new todo list."""
        todo_list = TodoListOrm(
            id=uuid.uuid4(),
            name=name,
            slug=slug,
            is_free=is_free
        )
        session.add(todo_list)
        # session.flush()
        return todo_list
    
    def get_one_free(self, session: Session) -> TodoListOrm | None:
        """Get one free todo list."""
        stmt = select(TodoListOrm).where(TodoListOrm.is_free == True).limit(1).with_for_update(skip_locked=True)
        result = session.execute(stmt).scalar_one_or_none()
        return result
    
    def get_by_slug(self, session: Session, slug: str, with_tasks: bool = False, with_block: bool = False) -> TodoListOrm | None:
        """Get todo list by slug."""
        if with_block:
            stmt = select(TodoListOrm).where(TodoListOrm.slug == slug).with_for_update()
        else:
            stmt = select(TodoListOrm).where(TodoListOrm.slug == slug)
        result = session.execute(stmt).scalar_one_or_none()
        if result and with_tasks:
            result.tasks
        return result
    
    def get_by_id(self, session: Session, list_id: uuid.UUID, with_tasks: bool = False, with_block: bool = False) -> TodoListOrm | None:
        """Get todo list by ID."""
        if with_block:
            stmt = select(TodoListOrm).where(TodoListOrm.id == list_id).with_for_update()
        else:
            stmt = select(TodoListOrm).where(TodoListOrm.id == list_id)
        result = session.execute(stmt).scalar_one_or_none()
        if result and with_tasks:
            result.tasks
        return result
    
    def update(self, session: Session, todo_list: TodoListOrm, name: str = None) -> TodoListOrm:
        """Update todo list."""
        if name is not None:
            todo_list.name = name

        return todo_list
    
    def free(self, session: Session, todo_list: TodoListOrm) -> None:
        """Mark todo list as free."""
        todo_list.is_free = True
        session.flush()

    def take_up(self, session: Session, todo_list: TodoListOrm) -> None:
        """Mark todo list as taken."""
        todo_list.is_free = False
        session.flush()
    
    def delete(self, session: Session, todo_list: TodoListOrm) -> None:
        """Delete todo list."""
        session.delete(todo_list)
        session.flush()
    
    def delete_by_slug(self, session: Session, slug: str) -> bool:
        """Delete todo list by slug. Returns True if deleted, False if not found."""
        todo_list = self.get_by_slug(session, slug)
        if todo_list:
            self.delete(session, todo_list)
            return True
        return False
