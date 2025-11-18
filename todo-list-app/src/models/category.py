"""
Модель категории задач
"""
from enum import Enum


class Category(Enum):
    """Категории задач согласно глоссарию"""
    WORK = "Работа"
    PERSONAL = "Личное"
    HEALTH = "Здоровье"
    LEARNING = "Обучение"
    HOME = "Дом"
    OTHER = "Другое"

    @classmethod
    def get_color(cls, category: 'Category') -> str:
        """Получение цвета для категории"""
        colors = {
            cls.WORK: "#FF6B6B",
            cls.PERSONAL: "#4ECDC4",
            cls.HEALTH: "#45B7D1",
            cls.LEARNING: "#96CEB4",
            cls.HOME: "#FFEAA7",
            cls.OTHER: "#DDA0DD"
        }
        return colors.get(category, "#CCCCCC")

    def __str__(self) -> str:
        return self.value