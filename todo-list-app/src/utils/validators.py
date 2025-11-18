"""
Валидаторы данных согласно Use Case сценариям
"""
from datetime import date
from typing import Dict, Any


def validate_task_data(task_data: Dict[str, Any]) -> bool:
    """Валидация данных задачи - соответствует альтернативным потокам Use Case"""

    # Проверка обязательного поля title
    if not task_data.get('title') or not task_data['title'].strip():
        return False

    # Проверка длины заголовка
    if len(task_data['title'].strip()) > 200:
        return False

    # Проверка длины описания
    if task_data.get('description') and len(task_data['description']) > 2000:
        return False

    # Проверка даты (не может быть в прошлом)
    if task_data.get('due_date') and task_data['due_date'] < date.today():
        return False

    return True


def validate_date_format(date_string: str) -> bool:
    """Проверка формата даты"""
    try:
        date.fromisoformat(date_string)
        return True
    except ValueError:
        return False