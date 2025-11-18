"""
Скрипт запуска всех тестов
"""
import unittest
import sys
import os

def run_tests():
    """Запуск всех тестов"""
    # Добавляем src в путь для импортов
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    # Находим все тесты в директории tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'src', 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим сводку
    print("\n" + "="*50)
    print("ТЕСТОВАЯ СВОДКА")
    print("="*50)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалены: {len(result.failures)}")
    print(f"Ошибки: {len(result.errors)}")
    
    if result.failures:
        print("\nПРОВАЛЕННЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nТЕСТЫ С ОШИБКАМИ:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result

if __name__ == '__main__':
    print("Запуск тестов системы управления задачами...")
    result = run_tests()
    
    # Возвращаем код выхода (0 - успех, 1 - есть ошибки)
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)