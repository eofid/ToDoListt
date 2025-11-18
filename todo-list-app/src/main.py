"""
Главный модуль приложения To-Do List
Соответствует диаграмме развертывания и архитектуре MVC
"""
import tkinter as tk
import logging
from pathlib import Path
import os
import sys

# Добавляем текущую директорию в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.task_controller import TaskController
from views.main_window import MainWindow


def setup_logging() -> None:
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('todo_app.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Основная функция приложения"""
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting To-Do List Application")

    try:
        # Создание контроллера
        task_controller = TaskController()

        # Создание главного окна
        root = tk.Tk()
        root.title("To-Do List")
        root.geometry("800x600")

        # Создание главного окна приложения
        app = MainWindow(root, task_controller)

        # Обработка закрытия окна
        def on_closing():
            task_controller.final_save()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        # Запуск главного цикла
        logger.info("Application started successfully")
        root.mainloop()

    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()