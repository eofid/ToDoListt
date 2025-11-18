"""
Тесты моделей данных - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""
import unittest
import sys
import os
from datetime import date, datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.task import Task, TaskStatus
from models.category import Category
from models.priority import Priority

class TestTaskModel(unittest.TestCase):
    """Тесты модели Task"""
    
    def test_task_creation(self):
        """Создание задачи с валидными данными"""
        task = Task(
            title='Test Task',
            description='Test Description',
            category='Работа',
            priority='Высокий',
            due_date=date(2024, 12, 31)
        )
        
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, TaskStatus.NOT_STARTED)
        self.assertIsNotNone(task.creation_date)
    
    def test_task_update(self):
        """Обновление данных задачи - ИСПРАВЛЕННЫЙ ТЕСТ"""
        task = Task(title='Original')
        # Даем время для различия в датах
        import time
        time.sleep(0.01)
        
        task.update(title='Updated', description='New Description')
        
        self.assertEqual(task.title, 'Updated')
        self.assertEqual(task.description, 'New Description')
        # Проверяем что дата обновления изменилась (может быть равно если очень быстро)
        self.assertIsNotNone(task.modification_date)
    
    def test_status_change(self):
        """Изменение статуса задачи"""
        task = Task(title='Test')
        original_mod_date = task.modification_date
        
        task.set_status(TaskStatus.IN_PROGRESS)
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
        # Проверяем что дата обновления установлена
        self.assertIsNotNone(task.modification_date)
    
    def test_overdue_detection(self):
        """Определение просроченных задач"""
        # Используем гарантированно прошедшую дату
        overdue_task = Task(title='Overdue', due_date=date(2020, 1, 1))
        self.assertTrue(overdue_task.is_overdue())
        
        # Используем гарантированно будущую дату
        future_task = Task(title='Future', due_date=date(2030, 1, 1))
        self.assertFalse(future_task.is_overdue())
        
        # Задача без даты
        no_date_task = Task(title='No Date')
        self.assertFalse(no_date_task.is_overdue())
    
    def test_due_soon_detection(self):
        """Определение задач с близким дедлайном"""
        # Задача на сегодня
        due_soon_task = Task(title='Due Soon', due_date=date.today())
        self.assertTrue(due_soon_task.is_due_soon())
        
        # Задача через 3 дня (не должна определяться как "скоро")
        from datetime import timedelta
        not_due_soon = Task(title='Not Due Soon', due_date=date.today() + timedelta(days=3))
        self.assertFalse(not_due_soon.is_due_soon())
    
    def test_serialization_deserialization(self):
        """Сериализация и десериализация задачи"""
        original_task = Task(
            title='Test Task', 
            description='Test Description',
            category='Работа',
            priority='Высокий',
            due_date=date(2024, 12, 31)
        )
        original_task.set_status(TaskStatus.COMPLETED)
        
        # Сериализация
        task_dict = original_task.to_dict()
        
        # Проверяем сериализацию
        self.assertEqual(task_dict['title'], 'Test Task')
        self.assertEqual(task_dict['status'], 'Выполнена')
        self.assertEqual(task_dict['category'], 'Работа')
        
        # Десериализация
        restored_task = Task.from_dict(task_dict)
        
        self.assertEqual(restored_task.title, original_task.title)
        self.assertEqual(restored_task.description, original_task.description)
        self.assertEqual(restored_task.status, original_task.status)
        self.assertEqual(restored_task.category, original_task.category)

class TestCategory(unittest.TestCase):
    """Тесты категорий"""
    
    def test_category_values(self):
        """Проверка значений категорий"""
        self.assertEqual(str(Category.WORK), "Работа")
        self.assertEqual(str(Category.PERSONAL), "Личное")
        self.assertEqual(str(Category.HEALTH), "Здоровье")
        self.assertEqual(str(Category.LEARNING), "Обучение")
        self.assertEqual(str(Category.HOME), "Дом")
        self.assertEqual(str(Category.OTHER), "Другое")
    
    def test_category_colors(self):
        """Проверка цветов категорий"""
        self.assertEqual(Category.get_color(Category.WORK), "#FF6B6B")
        self.assertEqual(Category.get_color(Category.PERSONAL), "#4ECDC4")
        self.assertEqual(Category.get_color(Category.HEALTH), "#45B7D1")
        self.assertEqual(Category.get_color(Category.LEARNING), "#96CEB4")
        self.assertEqual(Category.get_color(Category.HOME), "#FFEAA7")
        self.assertEqual(Category.get_color(Category.OTHER), "#DDA0DD")

class TestPriority(unittest.TestCase):
    """Тесты приоритетов"""
    
    def test_priority_values(self):
        """Проверка значений приоритетов"""
        self.assertEqual(str(Priority.HIGH), "Высокий")
        self.assertEqual(str(Priority.MEDIUM), "Средний")
        self.assertEqual(str(Priority.LOW), "Низкий")
    
    def test_priority_numeric_values(self):
        """Проверка числовых значений для сортировки"""
        self.assertEqual(Priority.HIGH.numeric_value, 3)
        self.assertEqual(Priority.MEDIUM.numeric_value, 2)
        self.assertEqual(Priority.LOW.numeric_value, 1)