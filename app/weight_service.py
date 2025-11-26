from asyncio import tasks
from app.entities import TodoList, MovePosition, TodoTask
import uuid
from typing import Optional

class WeightService:
    
    def calculate_weight(
        self, 
        todo_list: TodoList, 
        position: MovePosition, 
        target_task_id: Optional[uuid.UUID] = None,
        moving_task_id: Optional[uuid.UUID] = None
    ) -> float:
        tasks = todo_list.tasks
        normal_step = 100.0

        # Если список пустой или будет содержать одну задачу после перемещения
        if len(tasks) == 0 or (len(tasks) == 1 and moving_task_id is not None):
            return normal_step
        
        if moving_task_id is not None and target_task_id is not None and moving_task_id == target_task_id:
            return next((task.weight for task in tasks if task.id == moving_task_id), normal_step)
        
        # Фильтруем задачи, исключая перемещаемую задачу (если она уже в списке)
        existing_tasks = [task for task in tasks if task.id != moving_task_id]
        
        if not existing_tasks:
            return normal_step

        if position == MovePosition.FIRST:
            min_weight = min(task.weight for task in existing_tasks)
            return min_weight - normal_step

        elif position == MovePosition.LAST:
            max_weight = max(task.weight for task in existing_tasks)
            return max_weight + normal_step

        elif position == MovePosition.BEFORE and target_task_id:
            return self._calculate_before_weight(existing_tasks, target_task_id, normal_step)

        elif position == MovePosition.AFTER and target_task_id:
            return self._calculate_after_weight(existing_tasks, target_task_id, normal_step)

        max_weight = max(task.weight for task in existing_tasks)
        return max_weight + normal_step

    def _calculate_before_weight(
        self, 
        tasks: list[TodoTask], 
        target_task_id: uuid.UUID, 
        normal_step: float
    ) -> float:
        # Находим целевую задачу
        target_task = next((task for task in tasks if task.id == target_task_id), None)
        if not target_task:
            return max(task.weight for task in tasks) + normal_step

        # Находим задачу, которая идет перед целевой
        previous_tasks = [task for task in tasks if task.weight < target_task.weight]
        
        if not previous_tasks:
            # Если перед целевой нет задач, ставим в самое начало
            return target_task.weight - normal_step
        
        # Находим ближайшую задачу перед целевой
        closest_previous = max(previous_tasks, key=lambda t: t.weight)
        
        # Вычисляем средний вес между предыдущей и целевой задачами
        return (closest_previous.weight + target_task.weight) / 2

    def _calculate_after_weight(
        self, 
        tasks: list, 
        target_task_id: uuid.UUID, 
        normal_step: float
    ) -> float:
        """Рассчитать вес для позиции ПОСЛЕ целевой задачи"""
        # Находим целевую задачу
        target_task = next((task for task in tasks if task.id == target_task_id), None)
        if not target_task:
            return max(task.weight for task in tasks) + normal_step

        # Находим задачу, которая идет после целевой
        next_tasks = [task for task in tasks if task.weight > target_task.weight]
        
        if not next_tasks:
            # Если после целевой нет задач, ставим в самый конец
            return target_task.weight + normal_step
        
        # Находим ближайшую задачу после целевой
        closest_next = min(next_tasks, key=lambda t: t.weight)
        
        # Вычисляем средний вес между целевой и следующей задачами
        return (target_task.weight + closest_next.weight) / 2