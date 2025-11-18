"""
Интеграционные тесты - полные сценарии работы
"""
import unittest
import tempfile
import os
import sys
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from controllers.task_controller import TaskController
from models.task import TaskStatus

class TestIntegrationScenarios(unittest.TestCase):
    """Интеграционные сценарии тестирования"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
    
    def test_complete_user_workflow(self):
        """Полный сценарий работы пользователя"""
        controller = TaskController(storage_path=self.temp_file.name)
        
        # 1. Создание задач
        work_task = controller.create_task({
            'title': 'Work Project',
            'category': 'Работа',
            'priority': 'Высокий'
        })
        
        personal_task = controller.create_task({
            'title': 'Gym',
            'category': 'Личное'
        })
        
        # 2. Редактирование
        updated_personal = controller.update_task(personal_task.id, {
            'title': 'Gym Training'
        })
        self.assertEqual(updated_personal.title, 'Gym Training')
        
        # 3. Фильтрация
        work_tasks = controller.apply_filters({'category': 'Работа'})
        self.assertEqual(len(work_tasks), 1)
        
        # 4. Изменение статуса
        completed_work = controller.change_task_status(
            work_task.id, TaskStatus.COMPLETED
        )
        self.assertEqual(completed_work.status, TaskStatus.COMPLETED)
        
        # 5. Удаление
        delete_result = controller.delete_task(personal_task.id)
        self.assertTrue(delete_result)
        
        # 6. Сохранение и загрузка
        controller.save_changes()
        new_controller = TaskController(storage_path=self.temp_file.name)
        
        self.assertEqual(len(new_controller.tasks), 1)
        self.assertEqual(new_controller.tasks[0].title, 'Work Project')
    
    def test_task_sorting_workflow(self):
        """Сценарий сортировки задач"""
        controller = TaskController(storage_path=self.temp_file.name)
        
        # Создаем задачи с разными приоритетами
        controller.create_task({'title': 'Low', 'priority': 'Низкий'})
        controller.create_task({'title': 'High', 'priority': 'Высокий'})
        controller.create_task({'title': 'Medium', 'priority': 'Средний'})
        
        # Сортировка по приоритету
        sorted_tasks = controller.sort_tasks('priority', reverse=True)
        
        self.assertEqual(sorted_tasks[0].priority, 'Высокий')
        self.assertEqual(sorted_tasks[1].priority, 'Средний')
        self.assertEqual(sorted_tasks[2].priority, 'Низкий')
    
    def test_error_handling_workflow(self):
        """Сценарии обработки ошибок"""
        controller = TaskController(storage_path=self.temp_file.name)
        
        # Операции с несуществующими задачами
        with self.assertRaises(ValueError):
            controller.update_task(999, {'title': 'Test'})
        
        with self.assertRaises(ValueError):
            controller.change_task_status(999, TaskStatus.COMPLETED)
        
        self.assertFalse(controller.delete_task(999))
        
        # Невалидные данные
        with self.assertRaises(ValueError):
            controller.create_task({'title': ''})