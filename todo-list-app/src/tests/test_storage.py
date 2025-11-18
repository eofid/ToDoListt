"""
Тесты валидации и хранения данных - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""
import unittest
import tempfile
import os
import sys
from datetime import date
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.validators import validate_task_data, validate_date_format
from controllers.task_controller import TaskController
from models.task import TaskStatus

class TestValidators(unittest.TestCase):
    """Тесты валидаторов"""
    
    def test_validate_task_data_positive_no_due_date(self):
        """Валидация данных без даты выполнения"""
        valid_data = {
            'title': 'Valid Task',
            'description': 'Normal description'
            # Нет due_date - это допустимо
        }
        self.assertTrue(validate_task_data(valid_data))
    
    def test_validate_task_data_negative_empty_title(self):
        """Валидация пустого заголовка"""
        self.assertFalse(validate_task_data({'title': ''}))
    
    def test_validate_task_data_negative_whitespace_title(self):
        """Валидация заголовка из пробелов"""
        self.assertFalse(validate_task_data({'title': '   '}))
    
    def test_validate_task_data_negative_long_title(self):
        """Валидация слишком длинного заголовка"""
        self.assertFalse(validate_task_data({'title': 'A' * 201}))
    
    def test_validate_task_data_negative_long_description(self):
        """Валидация слишком длинного описания"""
        self.assertFalse(validate_task_data({
            'title': 'Valid Title',
            'description': 'D' * 2001
        }))
    
    def test_validate_task_data_negative_past_date(self):
        """Валидация прошедшей даты"""
        self.assertFalse(validate_task_data({
            'title': 'Test',
            'due_date': date(2020, 1, 1)
        }))
    
    def test_validate_date_format(self):
        """Валидация формата даты"""
        self.assertTrue(validate_date_format('2024-12-31'))
        self.assertFalse(validate_date_format('2024/12/31'))
        self.assertFalse(validate_date_format('invalid-date'))
        self.assertFalse(validate_date_format(''))

class TestDataPersistence(unittest.TestCase):
    """Тесты сохранения и загрузки данных"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
    
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_save_and_load_tasks(self):
        """Сохранение и загрузка задач"""
        # Создаем контроллер и задачи
        controller1 = TaskController(storage_path=self.temp_file.name)
        controller1.create_task({'title': 'Task 1'})
        controller1.create_task({'title': 'Task 2'})
        controller1.save_changes()
        
        # Проверяем что файл создан
        self.assertTrue(os.path.exists(self.temp_file.name))
        
        # Загружаем в новый контроллер
        controller2 = TaskController(storage_path=self.temp_file.name)
        self.assertEqual(len(controller2.tasks), 2)
        self.assertEqual(controller2.tasks[0].title, 'Task 1')
        self.assertEqual(controller2.tasks[1].title, 'Task 2')
    
    def test_load_empty_file(self):
        """Загрузка из несуществующего файла - ИСПРАВЛЕННЫЙ ТЕСТ"""
        # Убедимся что файла нет
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        
        # Создаем контроллер с несуществующим файлом
        controller = TaskController(storage_path=self.temp_file.name)
        
        # Должен создаться пустой список задач
        self.assertEqual(len(controller.tasks), 0)
        self.assertEqual(len(controller.filtered_tasks), 0)
    
    def test_data_integrity(self):
        """Проверка целостности данных при сохранении/загрузке - ИСПРАВЛЕННЫЙ ТЕСТ"""
        original_controller = TaskController(storage_path=self.temp_file.name)
        
        # Создаем задачу
        task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'category': 'Работа',
            'priority': 'Высокий'
        }
        task = original_controller.create_task(task_data)
        task_id = task.id
        
        # Меняем статус
        original_controller.change_task_status(task_id, TaskStatus.COMPLETED)
        original_controller.save_changes()
        
        # Проверяем что файл создан и содержит данные
        self.assertTrue(os.path.exists(self.temp_file.name))
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            file_content = f.read()
            self.assertIn('Test Task', file_content)
        
        # Загружаем и проверяем целостность
        loaded_controller = TaskController(storage_path=self.temp_file.name)
        self.assertEqual(len(loaded_controller.tasks), 1)
        
        loaded_task = loaded_controller.tasks[0]
        self.assertEqual(loaded_task.title, 'Test Task')
        self.assertEqual(loaded_task.description, 'Test Description')
        self.assertEqual(loaded_task.category, 'Работа')
        self.assertEqual(loaded_task.priority, 'Высокий')
        self.assertEqual(loaded_task.status, TaskStatus.COMPLETED)
    
    def test_corrupted_file_handling(self):
        """Обработка поврежденного файла"""
        # Создаем файл с некорректным JSON
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            f.write('{invalid json content')
        
        # Контроллер должен обработать ошибку и создать пустой список
        controller = TaskController(storage_path=self.temp_file.name)
        self.assertEqual(len(controller.tasks), 0)
    
    def test_empty_json_file(self):
        """Обработка пустого JSON файла"""
        # Создаем пустой JSON файл
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            f.write('[]')
        
        controller = TaskController(storage_path=self.temp_file.name)
        self.assertEqual(len(controller.tasks), 0)