"""
Модель задачи (Task)
Соответствует диаграмме классов предметной области
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional, Dict, Any

class TaskStatus(Enum):
    """Статусы задачи согласно диаграмме состояний"""
    NOT_STARTED = "Не начата"
    IN_PROGRESS = "В процессе"
    COMPLETED = "Выполнена"
    POSTPONED = "Отложена"

    def __str__(self) -> str:
        return self.value


class Task:
    """Класс задачи - центральная сущность системы"""

    def __init__(
        self,
        title: str,
        description: str = "",
        category: Optional[str] = None,
        priority: str = "Средний",
        due_date: Optional[date] = None,
        task_id: Optional[int] = None
    ):
        self.id = task_id or id(self)
        self.title = title
        self.description = description
        self.category = category
        self.priority = priority
        self.due_date = due_date
        self.status = TaskStatus.NOT_STARTED
        self.creation_date = datetime.now()
        self.modification_date = datetime.now()

    def update(self, **kwargs) -> None:
        """Обновление данных задачи"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.modification_date = datetime.now()

    def set_status(self, status: TaskStatus) -> None:
        """Изменение статуса задачи"""
        self.status = status
        self.modification_date = datetime.now()

    def is_overdue(self) -> bool:
        """Проверка просрочена ли задача"""
        if not self.due_date:
            return False
        return self.due_date < date.today() and self.status != TaskStatus.COMPLETED

    def is_due_soon(self) -> bool:
        """Проверка приближения дедлайна"""
        if not self.due_date:
            return False
        days_until_due = (self.due_date - date.today()).days
        return 0 <= days_until_due <= 2 and self.status != TaskStatus.COMPLETED

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь для хранения"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status.value,
            'creation_date': self.creation_date.isoformat(),
            'modification_date': self.modification_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Десериализация из словаря"""
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            category=data.get('category'),
            priority=data.get('priority', 'Средний'),
            due_date=date.fromisoformat(data['due_date']) if data.get('due_date') else None,
            task_id=data['id']
        )

        task.status = TaskStatus(data['status'])
        task.creation_date = datetime.fromisoformat(data['creation_date'])
        task.modification_date = datetime.fromisoformat(data['modification_date'])

        return task

    def __str__(self) -> str:
        return f"{self.title} ({self.status.value})"