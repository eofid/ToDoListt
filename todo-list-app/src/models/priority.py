"""
Модель приоритета задачи
"""
from enum import Enum


class Priority(Enum):
    """Уровни приоритета согласно глоссарию"""
    HIGH = "Высокий"
    MEDIUM = "Средний"
    LOW = "Низкий"

    @property
    def numeric_value(self) -> int:
        """Числовое значение для сортировки"""
        values = {
            Priority.HIGH: 3,
            Priority.MEDIUM: 2,
            Priority.LOW: 1
        }
        return values[self]

    def __str__(self) -> str:
        return self.value