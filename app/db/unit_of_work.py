"""Unit of Work pattern implementation for transaction management."""
from sqlalchemy.orm import Session, sessionmaker
from app.db.repositories import TodoListRepository, TodoTaskRepository


class UnitOfWork:
    """Unit of Work manages database transactions and provides access to repositories."""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
        self.session: Session | None = None

        self.todo_lists = TodoListRepository()
        self.todo_tasks = TodoTaskRepository()

    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()