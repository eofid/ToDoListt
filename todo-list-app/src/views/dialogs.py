"""
Диалоговые окна приложения
Соответствуют Use Case сценариям и диаграммам последовательности
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Optional, Dict, Any

# АБСОЛЮТНЫЕ ИМПОРТЫ
from models.task import Task, TaskStatus
from controllers.task_controller import TaskController
from utils.validators import validate_task_data, validate_date_format
from utils.constants import DATE_FORMAT


class BaseDialog:
    """Базовый класс для диалоговых окон"""

    def __init__(self, parent, title: str, width: int = 400, height: int = 300):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Центрирование диалога
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self.result = None

    def validate_input(self) -> bool:
        """Валидация ввода - должен быть переопределен"""
        return True

    def get_result(self):
        """Получение результата - должен быть переопределен"""
        return None


class AddTaskDialog(BaseDialog):
    """Диалог добавления новой задачи"""

    def __init__(self, parent, controller: TaskController):
        self.controller = controller
        super().__init__(parent, "Добавить задачу", 500, 500)  # Увеличил размеры окна
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса диалога добавления"""
        # Основной фрейм с возможностью растяжения
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)  # Добавил expand=True

        # Заголовок
        title_label = tk.Label(
            main_frame,
            text="Новая задача",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20), anchor=tk.W)  # Увеличил отступ

        # Поле названия
        ttk.Label(main_frame, text="Название задачи*:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.title_entry = tk.Entry(main_frame, font=("Arial", 11))
        self.title_entry.pack(fill=tk.X, pady=(0, 15))  # Увеличил отступ и добавил fill=tk.X
        self.title_entry.focus()

        # Поле описания
        ttk.Label(main_frame, text="Описание:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.desc_text = tk.Text(main_frame, font=("Arial", 11), height=4)
        self.desc_text.pack(fill=tk.BOTH, pady=(0, 15), expand=True)  # Добавил fill=tk.BOTH и expand=True

        # Фрейм для категории и приоритета в одной строке
        cat_pri_frame = ttk.Frame(main_frame)
        cat_pri_frame.pack(fill=tk.X, pady=(0, 15))

        # Категория (левая сторона)
        category_frame = ttk.Frame(cat_pri_frame)
        category_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(category_frame, text="Категория:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.category_var,
            values=["Работа", "Личное", "Здоровье", "Обучение", "Дом", "Другое"],
            state="readonly",
            font=("Arial", 11)
        )
        category_combo.pack(fill=tk.X, pady=(0, 5))

        # Приоритет (правая сторона)
        priority_frame = ttk.Frame(cat_pri_frame)
        priority_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        ttk.Label(priority_frame, text="Приоритет:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.priority_var = tk.StringVar(value="Средний")
        priority_combo = ttk.Combobox(
            priority_frame,
            textvariable=self.priority_var,
            values=["Высокий", "Средний", "Низкий"],
            state="readonly",
            font=("Arial", 11)
        )
        priority_combo.pack(fill=tk.X, pady=(0, 5))

        # Срок выполнения
        due_date_frame = ttk.Frame(main_frame)
        due_date_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(due_date_frame, text="Срок выполнения (ДД.ММ.ГГГГ):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        
        date_input_frame = ttk.Frame(due_date_frame)
        date_input_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.due_date_entry = tk.Entry(date_input_frame, font=("Arial", 11), width=20)
        self.due_date_entry.pack(side=tk.LEFT)

        # Кнопка сегодня
        today_btn = ttk.Button(
            date_input_frame,
            text="Сегодня",
            command=self.set_today_date
        )
        today_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Фрейм для кнопок действий внизу
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))  # Увеличил отступ сверху

        # Конфигурация колонок для равномерного распределения кнопок
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ## Кнопка Сегодня
        #today_btn_bottom = tk.Button(
        #    button_frame,
        #    text="Сегодня",
        #    command=self.set_today_date,
        #    bg="#3498DB",
        #    fg="white",
        #    font=("Arial", 10),
        #    padx=20,
        #    pady=10
        #)
        #today_btn_bottom.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # Кнопка Отмена
        cancel_btn = tk.Button(
            button_frame,
            text="Отмена",
            command=self.on_cancel,
            bg="#95A5A6",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=10
        )
        cancel_btn.grid(row=0, column=1, padx=5, sticky="ew")

        # Кнопка Добавить
        ok_btn = tk.Button(
            button_frame,
            text="Добавить",
            command=self.on_ok,
            bg="#27AE60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=10
        )
        ok_btn.grid(row=0, column=2, padx=(5, 0), sticky="ew")

        # Принудительное обновление геометрии окна
        self.dialog.update_idletasks()

    def set_today_date(self):
        """Установить сегодняшнюю дату"""
        today = datetime.now().strftime(DATE_FORMAT)
        self.due_date_entry.delete(0, tk.END)
        self.due_date_entry.insert(0, today)

    def validate_input(self) -> bool:
        """Валидация введенных данных"""
        title = self.title_entry.get().strip()

        if not title:
            messagebox.showerror("Ошибка", "Название задачи обязательно для заполнения")
            self.title_entry.focus()
            return False

        due_date_str = self.due_date_entry.get().strip()

        # ЕДИНАЯ ПРОВЕРКА ДАТЫ
        if due_date_str:
            try:
                # Пробуем распарсить дату
                due_date_obj = datetime.strptime(due_date_str, DATE_FORMAT).date()

                # Проверка что дата не в прошлом
                if due_date_obj < date.today():
                    messagebox.showerror("Ошибка", "Дата не может быть в прошлом")
                    self.due_date_entry.focus()
                    return False

            except ValueError:
                # Если парсинг не удался - показываем ошибку
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ")
                self.due_date_entry.focus()
                return False

        return True

    def get_result(self) -> Dict[str, Any]:
        """Получение данных задачи"""
        due_date_str = self.due_date_entry.get().strip()
        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, DATE_FORMAT).date()

        return {
            'title': self.title_entry.get().strip(),
            'description': self.desc_text.get("1.0", tk.END).strip(),
            'category': self.category_var.get() or None,
            'priority': self.priority_var.get(),
            'due_date': due_date
        }

    def on_ok(self):
        """Обработка OK с созданием задачи"""
        if self.validate_input():
            try:
                task_data = self.get_result()
                self.controller.create_task(task_data)
                messagebox.showinfo("Успех", "Задача успешно создана")
                self.dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать задачу: {e}")

    def on_cancel(self):
        """Обработка отмены"""
        self.dialog.destroy()

class EditTaskDialog(AddTaskDialog):
    """Диалог редактирования задачи"""

    def __init__(self, parent, controller: TaskController, task: Task):
        self.task = task
        super().__init__(parent, controller)
        self.dialog.title("Редактировать задачу")
        self.fill_existing_data()

    def fill_existing_data(self):
        """Заполнение существующих данных задачи"""
        self.title_entry.insert(0, self.task.title)
        self.desc_text.insert("1.0", self.task.description or "")

        if self.task.category:
            self.category_var.set(self.task.category)

        self.priority_var.set(self.task.priority)

        if self.task.due_date:
            self.due_date_entry.insert(0, self.task.due_date.strftime(DATE_FORMAT))

    def on_ok(self):
        """Обработка OK с обновлением задачи"""
        if self.validate_input():
            try:
                task_data = self.get_result()
                self.controller.update_task(self.task.id, task_data)
                messagebox.showinfo("Успех", "Задача успешно обновлена")
                self.dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить задачу: {e}")


class FilterDialog(BaseDialog):
    """Диалог фильтрации задач"""

    def __init__(self, parent, controller: TaskController):
        self.controller = controller
        super().__init__(parent, "Фильтры задач", 400, 350)  # Увеличил размеры окна
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса фильтрации"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(
            main_frame,
            text="Фильтры задач",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Фильтр по статусу
        ttk.Label(main_frame, text="Статус:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(
            main_frame,
            textvariable=self.status_var,
            values=[""] + [status.value for status in TaskStatus],
            state="readonly",
            font=("Arial", 11)
        )
        status_combo.pack(fill=tk.X, pady=(0, 15))

        # Фильтр по категории
        ttk.Label(main_frame, text="Категория:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            main_frame,
            textvariable=self.category_var,
            values=[""] + ["Работа", "Личное", "Здоровье", "Обучение", "Дом", "Другое"],
            state="readonly",
            font=("Arial", 11)
        )
        category_combo.pack(fill=tk.X, pady=(0, 15))

        # Фильтр по приоритету
        ttk.Label(main_frame, text="Приоритет:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(
            main_frame,
            textvariable=self.priority_var,
            values=[""] + ["Высокий", "Средний", "Низкий"],
            state="readonly",
            font=("Arial", 11)
        )
        priority_combo.pack(fill=tk.X, pady=(0, 20))

        # Кнопки действий - используем grid для равномерного распределения
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        # Конфигурация колонок для равномерного распределения
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        # Кнопка Закрыть
        cancel_btn = tk.Button(
            button_frame,
            text="Закрыть",
            command=self.on_cancel,
            font=("Arial", 10),
            bg="#95A5A6",
            fg="white",
            padx=15,
            pady=10
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # Кнопка Сбросить
        reset_btn = tk.Button(
            button_frame,
            text="Сбросить",
            command=self.reset_filters,
            font=("Arial", 10),
            bg="#E74C3C",
            fg="white",
            padx=15,
            pady=10
        )
        reset_btn.grid(row=0, column=1, padx=5, sticky="ew")

        # Кнопка Применить
        apply_btn = tk.Button(
            button_frame,
            text="Применить",
            command=self.apply_filters,
            font=("Arial", 10, "bold"),
            bg="#27AE60",
            fg="white",
            padx=15,
            pady=10
        )
        apply_btn.grid(row=0, column=2, padx=(5, 0), sticky="ew")

        # Принудительное обновление геометрии окна
        self.dialog.update_idletasks()

    def apply_filters(self):
        """Применить выбранные фильтры"""
        filters = {}

        if self.status_var.get():
            status = next((s for s in TaskStatus if s.value == self.status_var.get()), None)
            if status:
                filters['status'] = status

        if self.category_var.get():
            filters['category'] = self.category_var.get()

        if self.priority_var.get():
            filters['priority'] = self.priority_var.get()

        self.controller.apply_filters(filters)
        self.dialog.destroy()

    def reset_filters(self):
        """Сбросить все фильтры"""
        self.controller.apply_filters({})
        self.dialog.destroy()

    def on_cancel(self):
        """Обработка закрытия"""
        self.dialog.destroy()