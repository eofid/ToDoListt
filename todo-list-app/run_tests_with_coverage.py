"""
Скрипт запуска тестов с измерением покрытия кода
"""
import coverage
import unittest
import sys
import os

def run_tests_with_coverage():
    """Запуск тестов с измерением покрытия кода"""
    
    # Добавляем src в путь для импортов
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    # Инициализируем coverage
    cov = coverage.Coverage(
        source=['src'],  # Папка с исходным кодом
        omit=[
            '*/tests/*',  # Исключаем тесты
            '*/__pycache__/*',  # Исключаем кэш
        ],
        branch=True  # Включаем измерение покрытия ветвей
    )
    
    # Начинаем измерение покрытия
    cov.start()
    
    # Запускаем тесты
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'src', 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Останавливаем измерение покрытия
    cov.stop()
    
    # Сохраняем данные покрытия
    cov.save()
    
    # Выводим отчет в консоль
    print("\n" + "="*70)
    print("ОТЧЕТ О ПОКРЫТИИ КОДА ТЕСТАМИ")
    print("="*70)
    
    # Детальный отчет по файлам
    print("\nДЕТАЛЬНЫЙ ОТЧЕТ ПО ФАЙЛАМ:")
    print("-" * 70)
    cov.report(show_missing=True, skip_covered=False)
    
    # Сводная статистика
    print("\n" + "="*70)
    print("СВОДНАЯ СТАТИСТИКА")
    print("="*70)
    
    # Получаем общую статистику
    total_stats = cov.report(show_missing=False, skip_covered=True)
    
    # Выводим HTML отчет (опционально)
    print("\nГенерация HTML отчета...")
    cov.html_report(directory='htmlcov')
    print(f"HTML отчет сохранен в папку: htmlcov/")
    print("Откройте файл htmlcov/index.html в браузере для детального просмотра")
    
    # Выводим результаты тестов
    print("\n" + "="*70)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*70)
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
    
    # Рассчитываем общий процент покрытия
    data = cov.get_data()
    total_lines = 0
    total_covered = 0
    
    for filename in cov.get_data().measured_files():
        analysis = cov.analysis(filename)
        total_lines += len(analysis[1])  # Все исполняемые строки
        total_covered += len(analysis[1]) - len(analysis[3])  # Покрытые строки
    
    if total_lines > 0:
        coverage_percent = (total_covered / total_lines) * 100
        print(f"\nОБЩЕЕ ПОКРЫТИЕ КОДА: {coverage_percent:.2f}%")
    else:
        print("\nОБЩЕЕ ПОКРЫТИЕ КОДА: 0%")
    
    # Рекомендации по улучшению покрытия
    print("\n" + "="*70)
    print("РЕКОМЕНДАЦИИ")
    print("="*70)
    
    # Находим файлы с низким покрытием
    low_coverage_files = []
    for filename in cov.get_data().measured_files():
        analysis = cov.analysis(filename)
        executable_lines = len(analysis[1])
        missing_lines = len(analysis[3])
        
        if executable_lines > 0:
            file_coverage = (executable_lines - missing_lines) / executable_lines * 100
            if file_coverage < 80:  # Порог 80%
                low_coverage_files.append((filename, file_coverage))
    
    if low_coverage_files:
        print("Файлы с низким покрытием (<80%):")
        for file_path, coverage_percent in sorted(low_coverage_files, key=lambda x: x[1]):
            file_name = os.path.basename(file_path)
            print(f"  - {file_name}: {coverage_percent:.1f}%")
    else:
        print("Все файлы имеют хорошее покрытие (>80%)!")
    
    # Закрываем coverage
    cov.erase()  # Очищаем данные для следующего запуска
    
    return result

if __name__ == '__main__':
    print("ЗАПУСК ТЕСТОВ С ИЗМЕРЕНИЕМ ПОКРЫТИЯ КОДА...")
    result = run_tests_with_coverage()
    
    # Возвращаем код выхода
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)