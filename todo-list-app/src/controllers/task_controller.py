"""
Контроллер задач - бизнес-логика согласно диаграммам последовательности
"""
import json
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, date

# АБСОЛЮТНЫЕ ИМПОРТЫ
from models.task import Task, TaskStatus
from utils.validators import validate_task_data


class TaskController:
    """Основной контроллер управления задачами"""

    def __init__(self, storage_path: str = "data/tasks.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.tasks: List[Task] = []
        self.filtered_tasks: List[Task] = []
        self.current_filters: Dict[str, Any] = {}
        self.logger = self._setup_logger()

        self.load_tasks()

    def _setup_logger(self) -> logging.Logger:
        """Настройка логирования"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def create_task(self, task_data: Dict[str, Any]) -> Task:
        """Создание новой задачи - соответствует Use Case 'Add Task'"""
        self.logger.info("Creating new task")

        # Валидация данных
        if not validate_task_data(task_data):
            raise ValueError("Invalid task data")

        # Создание задачи
        task = Task(
            title=task_data['title'],
            description=task_data.get('description', ''),
            category=task_data.get('category'),
            priority=task_data.get('priority', 'Средний'),
            due_date=task_data.get('due_date')
        )

        self.tasks.append(task)
        self.apply_filters(self.current_filters)
        self.save_changes()

        self.logger.info(f"Task created: {task.title} (ID: {task.id})")
        return task

    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> Task:
        """Обновление задачи - соответствует Use Case 'Edit Task'"""
        self.logger.info(f"Updating task ID: {task_id}")

        task = self.find_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Валидация данных
        if not validate_task_data(task_data):
            raise ValueError("Invalid task data")

        # Обновление задачи
        update_data = {}
        if 'title' in task_data:
            update_data['title'] = task_data['title']
        if 'description' in task_data:
            update_data['description'] = task_data['description']
        if 'category' in task_data:
            update_data['category'] = task_data['category']
        if 'priority' in task_data:
            update_data['priority'] = task_data['priority']
        if 'due_date' in task_data:
            update_data['due_date'] = task_data['due_date']

        task.update(**update_data)
        self.apply_filters(self.current_filters)
        self.save_changes()

        self.logger.info(f"Task updated: {task.title} (ID: {task.id})")
        return task

    def delete_task(self, task_id: int) -> bool:
        """Удаление задачи"""
        self.logger.info(f"Deleting task ID: {task_id}")

        task = self.find_task(task_id)
        if task:
            self.tasks.remove(task)
            self.apply_filters(self.current_filters)
            self.save_changes()
            self.logger.info(f"Task deleted: {task.title} (ID: {task.id})")
            return True
        return False

    def change_task_status(self, task_id: int, status: TaskStatus) -> Task:
        """Изменение статуса задачи - соответствует Use Case 'Complete Task'"""
        self.logger.info(f"Changing task status ID: {task_id} to {status}")

        task = self.find_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        if task.status == status:
            self.logger.warning(f"Task already has status: {status}")
            return task

        task.set_status(status)
        self.apply_filters(self.current_filters)
        self.save_changes()

        self.logger.info(f"Task status changed: {task.title} -> {status.value}")
        return task

    def find_task(self, task_id: int) -> Optional[Task]:
        """Поиск задачи по ID"""
        return next((task for task in self.tasks if task.id == task_id), None)

    def apply_filters(self, filters: Dict[str, Any]) -> List[Task]:
        """Применение фильтров - соответствует Use Case 'Filter Tasks'"""
        self.current_filters = filters
        self.filtered_tasks = self.tasks.copy()

        # Фильтрация по статусу
        if filters.get('status'):
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if task.status.value == filters['status'].value
            ]

        # Фильтрация по категории
        if filters.get('category'):
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if task.category == filters['category']
            ]

        # Фильтрация по приоритету
        if filters.get('priority'):
            self.filtered_tasks = [
                task for task in self.filtered_tasks
                if task.priority == filters['priority']
            ]

        self.logger.info(f"Filters applied: {len(self.filtered_tasks)} tasks match criteria")
        return self.filtered_tasks

    def sort_tasks(self, criteria: str, reverse: bool = False) -> List[Task]:
        """Сортировка задач"""
        sort_key = {
            'due_date': lambda t: t.due_date or date.max,
            'priority': lambda t: {'Высокий': 3, 'Средний': 2, 'Низкий': 1}.get(t.priority, 2),
            'creation_date': lambda t: t.creation_date,
            'title': lambda t: t.title.lower()
        }.get(criteria, lambda t: t.creation_date)

        sorted_tasks = sorted(self.filtered_tasks, key=sort_key, reverse=reverse)
        self.logger.info(f"Tasks sorted by: {criteria}")
        return sorted_tasks

    def load_tasks(self) -> None:
        """Загрузка задач из хранилища"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
                self.filtered_tasks = self.tasks.copy()
                self.logger.info(f"Loaded {len(self.tasks)} tasks from storage")
            else:
                self.logger.info("No existing storage found, starting with empty task list")
        except Exception as e:
            self.logger.error(f"Error loading tasks: {e}")
            self.tasks = []
            self.filtered_tasks = []

    def save_changes(self) -> None:
        """Сохранение изменений"""
        try:
            data = [task.to_dict() for task in self.tasks]
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Saved {len(self.tasks)} tasks to storage")
        except Exception as e:
            self.logger.error(f"Error saving tasks: {e}")

    def final_save(self) -> None:
        """Финальное сохранение при закрытии приложения"""
        self.save_changes()
        self.logger.info("Final save completed")

    def get_tasks(self) -> List[Task]:
        """Получение всех задач"""
        return self.tasks

    def get_filtered_tasks(self) -> List[Task]:
        """Получение отфильтрованных задач"""
        return self.filtered_tasks