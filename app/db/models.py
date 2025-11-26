import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Float, String, ForeignKey
import uuid

from typing import Annotated

uuidpk = Annotated[uuid.UUID, mapped_column(primary_key=True)]

class Base(DeclarativeBase):
    pass

class TodoListOrm(Base):
    __tablename__ = "todo_lists"
    id: Mapped[uuidpk]
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(16), unique=True)
    is_free: Mapped[bool] = mapped_column(default=True)

    tasks: Mapped[list["TodoTaskOrm"]] = relationship(
        back_populates="todo_list",
        order_by="TodoTaskOrm.weight",
        cascade="all, delete-orphan")

class TodoTaskOrm(Base):
    __tablename__ = "todo_tasks"

    id: Mapped[uuidpk]
    task: Mapped[str] = mapped_column(String(255))
    is_done: Mapped[bool] = mapped_column(default=False)
    todo_list_id: Mapped[uuidpk] = mapped_column(ForeignKey("todo_lists.id"))
    weight: Mapped[float] = mapped_column(Float, default=0.0)

    todo_list: Mapped["TodoListOrm"] = relationship(back_populates="tasks")
