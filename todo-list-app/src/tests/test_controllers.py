"""
Тесты контроллеров - Use Case тестирование
"""
import unittest
import tempfile
import os
import sys
from datetime import date

# Импорты из проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from controllers.task_controller import TaskController
from models.task import TaskStatus

class TestTaskControllerUseCases(unittest.TestCase):
    """Use Case тестирование TaskController"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.controller = TaskController(storage_path=self.temp_file.name)
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
    
    # Use Case: Add Task
    def test_uc_add_task_positive(self):
        """UC-AT-001: Позитивное создание задачи"""
        task_data = {'title': 'Test Task'}
        task = self.controller.create_task(task_data)
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, TaskStatus.NOT_STARTED)
    
    def test_uc_add_task_negative_empty_title(self):
        """UC-AT-002: Создание с пустым заголовком"""
        with self.assertRaises(ValueError):
            self.controller.create_task({'title': ''})
    
    # Use Case: Edit Task
    def test_uc_edit_task_positive(self):
        """UC-ET-001: Редактирование задачи"""
        task = self.controller.create_task({'title': 'Original'})
        updated = self.controller.update_task(task.id, {'title': 'Updated'})
        self.assertEqual(updated.title, 'Updated')
    
    def test_uc_edit_task_negative_not_found(self):
        """UC-ET-002: Редактирование несуществующей задачи"""
        with self.assertRaises(ValueError):
            self.controller.update_task(999, {'title': 'Test'})
    
    # Use Case: Complete Task
    def test_uc_complete_task_positive(self):
        """UC-CT-001: Завершение задачи"""
        task = self.controller.create_task({'title': 'Task'})
        completed = self.controller.change_task_status(task.id, TaskStatus.COMPLETED)
        self.assertEqual(completed.status, TaskStatus.COMPLETED)
    
    # Use Case: Filter Tasks
    def test_uc_filter_tasks_by_status(self):
        """UC-FT-001: Фильтрация по статусу"""
        task1 = self.controller.create_task({'title': 'Task 1'})
        task2 = self.controller.create_task({'title': 'Task 2'})
        self.controller.change_task_status(task1.id, TaskStatus.COMPLETED)
        
        filtered = self.controller.apply_filters({'status': TaskStatus.COMPLETED})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].id, task1.id)
    
    # Use Case: Delete Task
    def test_uc_delete_task_positive(self):
        """UC-DT-001: Удаление задачи"""
        task = self.controller.create_task({'title': 'To Delete'})
        result = self.controller.delete_task(task.id)
        self.assertTrue(result)
        self.assertEqual(len(self.controller.tasks), 0)
    
    def test_uc_delete_task_negative_not_found(self):
        """UC-DT-002: Удаление несуществующей задачи"""
        result = self.controller.delete_task(999)
        self.assertFalse(result)