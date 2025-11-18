"""
Главное окно приложения
Соответствует мокапам и диаграммам состояний GUI
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Dict, Any
import datetime

# АБСОЛЮТНЫЕ ИМПОРТЫ
from models.task import Task, TaskStatus
from controllers.task_controller import TaskController
from utils.constants import STATUS_COLORS, DATE_FORMAT

# ОТНОСИТЕЛЬНЫЕ ИМПОРТЫ ВНУТРИ ПАКЕТА
from .dialogs import AddTaskDialog, EditTaskDialog, FilterDialog


class MainWindow:
    """Главное окно приложения - соответствует диаграмме состояний GUI"""

    def __init__(self, root: tk.Tk, controller: TaskController):
        self.root = root
        self.controller = controller
        self.current_sort = {'column': 'creation_date', 'reverse': False}
        self.setup_ui()
        self.refresh_task_list()
        self.setup_bindings()

    def setup_ui(self):
        """Настройка пользовательского интерфейса согласно мокапам"""
        self.root.title("To-Do List")
        self.root.geometry("900x700")

        # Основной контейнер
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовок и дата
        self.setup_header()

        # Панель управления
        self.setup_control_panel()

        # Список задач
        self.setup_task_list()

        # Статус бар
        self.setup_status_bar()

    def setup_header(self):
        """Заголовок приложения"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Заголовок
        self.title_label = tk.Label(
            header_frame,
            text="To-Do List",
            font=("Arial", 18, "bold"),
            fg="#2C3E50"
        )
        self.title_label.pack(side=tk.LEFT)

        # Текущая дата
        current_date = datetime.datetime.now().strftime("%A, %d %B %Y")
        self.date_label = tk.Label(
            header_frame,
            text=current_date,
            font=("Arial", 10),
            fg="#7F8C8D"
        )
        self.date_label.pack(side=tk.RIGHT)

    def setup_control_panel(self):
        """Панель управления задачами"""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Кнопки управления
        button_style = {"font": ("Arial", 10), "padx": 15, "pady": 8}

        self.add_btn = tk.Button(
            control_frame,
            text="➕ Добавить задачу",
            command=self.show_add_dialog,
            bg="#27AE60",
            fg="white",
            **button_style
        )
        self.add_btn.pack(side=tk.LEFT, padx=(0, 5))


        self.filter_btn = tk.Button(
            control_frame,
            text="🔍 Фильтры",
            command=self.show_filter_dialog,
            bg="#3498DB",
            fg="white",
            **button_style
        )
        self.filter_btn.pack(side=tk.LEFT, padx=5)

        self.sort_btn = tk.Button(
            control_frame,
            text="📊 Сортировка",
            command=self.show_sort_menu,
            bg="#9B59B6",
            fg="white",
            **button_style
        )
        self.sort_btn.pack(side=tk.LEFT, padx=5)

        # Статистика
        stats_frame = ttk.Frame(control_frame)
        stats_frame.pack(side=tk.RIGHT)

        self.stats_label = tk.Label(
            stats_frame,
            text="",
            font=("Arial", 9),
            fg="#7F8C8D"
        )
        self.stats_label.pack()

    def setup_task_list(self):
        """Настройка списка задач"""
        # Фрейм для таблицы
        table_frame = ttk.Frame(self.main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Создание Treeview с колонками (добавляем скрытую колонку ID)
        columns = ("id", "title", "category", "priority", "status", "due_date")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20,
            selectmode="browse"
        )

        # Скрываем колонку ID
        self.tree.column("id", width=0, stretch=False)
        
        # Настройка видимых колонок
        self.tree.heading("title", text="Задача", command=lambda: self.sort_by_column("title"))
        self.tree.heading("category", text="Категория", command=lambda: self.sort_by_column("category"))
        self.tree.heading("priority", text="Приоритет", command=lambda: self.sort_by_column("priority"))
        self.tree.heading("status", text="Статус", command=lambda: self.sort_by_column("status"))
        self.tree.heading("due_date", text="Срок выполнения", command=lambda: self.sort_by_column("due_date"))

        self.tree.column("title", width=300, anchor=tk.W)
        self.tree.column("category", width=120, anchor=tk.CENTER)
        self.tree.column("priority", width=100, anchor=tk.CENTER)
        self.tree.column("status", width=120, anchor=tk.CENTER)
        self.tree.column("due_date", width=120, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Контекстное меню
        self.setup_context_menu()

    def setup_context_menu(self):
        """Настройка контекстного меню для задач"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Редактировать", command=self.edit_selected_task)
        self.context_menu.add_separator()
        
        # Подменю для смены статуса
        status_menu = tk.Menu(self.context_menu, tearoff=0)
        status_menu.add_command(label="Не начата", command=lambda: self.change_task_status(TaskStatus.NOT_STARTED))
        status_menu.add_command(label="В процессе", command=lambda: self.change_task_status(TaskStatus.IN_PROGRESS))
        status_menu.add_command(label="Выполнена", command=lambda: self.change_task_status(TaskStatus.COMPLETED))
        status_menu.add_command(label="Отложена", command=lambda: self.change_task_status(TaskStatus.POSTPONED))
        
        self.context_menu.add_cascade(label="Изменить статус", menu=status_menu)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Удалить", command=self.delete_selected_task)
        self.context_menu.add_command(label="Свойства", command=self.show_task_details)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.edit_selected_task())

    def setup_status_bar(self):
        """Статус бар внизу окна"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = tk.Label(
            status_frame,
            text="Готово",
            font=("Arial", 9),
            fg="#7F8C8D",
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.task_count_label = tk.Label(
            status_frame,
            text="",
            font=("Arial", 9),
            fg="#7F8C8D"
        )
        self.task_count_label.pack(side=tk.RIGHT)

    def setup_bindings(self):
        """Настройка привязок клавиш"""
        self.root.bind("<Control-n>", lambda e: self.show_add_dialog())
        self.root.bind("<Control-f>", lambda e: self.show_filter_dialog())
        self.root.bind("<Delete>", lambda e: self.delete_selected_task())
        self.root.bind("<F5>", lambda e: self.refresh_task_list())

    def refresh_task_list(self):
        """Обновление списка задач"""
        # Очистка текущего списка
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Получение и отображение задач
        tasks = self.controller.get_filtered_tasks()

        for task in tasks:
            due_date_str = task.due_date.strftime(DATE_FORMAT) if task.due_date else ""

            item_id = self.tree.insert(
                "", tk.END,
                values=(
                    task.id,  # Добавляем ID в первую колонку
                    task.title,
                    task.category if task.category else "",
                    task.priority,
                    task.status.value,
                    due_date_str
                ),
                tags=(task.status.value,)
            )

            # Визуальное оформление по статусу
            if task.status == TaskStatus.COMPLETED:
                self.tree.set(item_id, "title", f"✓ {task.title}")
            elif task.is_overdue():
                self.tree.set(item_id, "title", f"⚠ {task.title}")

            # Цвета для статусов
            self.tree.tag_configure(
                task.status.value,
                background=STATUS_COLORS.get(task.status.value, "#FFFFFF")
            )

        # Обновление статистики
        self.update_statistics()

    def update_statistics(self):
        """Обновление статистики в статус баре"""
        total_tasks = len(self.controller.get_tasks())
        filtered_tasks = len(self.controller.get_filtered_tasks())
        completed_tasks = len([t for t in self.controller.get_tasks() if t.status == TaskStatus.COMPLETED])

        self.task_count_label.config(
            text=f"Задачи: {filtered_tasks}/{total_tasks} (Выполнено: {completed_tasks})"
        )

        # Обновление статистики в панели управления
        stats_text = f"Всего: {total_tasks} | Выполнено: {completed_tasks} | Активные: {total_tasks - completed_tasks}"
        self.stats_label.config(text=stats_text)

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def show_add_dialog(self):
        """Показать диалог добавления задачи"""
        dialog = AddTaskDialog(self.root, self.controller)
        self.root.wait_window(dialog.dialog)
        self.refresh_task_list()

    def edit_selected_task(self):
        """Редактирование выбранной задачи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу для редактирования")
            return

        item = selected[0]
        task_id = self.tree.item(item)['values'][0]  # Получаем ID из первой колонки

        task = self.controller.find_task(task_id)
        if task:
            dialog = EditTaskDialog(self.root, self.controller, task)
            self.root.wait_window(dialog.dialog)
            self.refresh_task_list()

    def complete_selected_task(self):
        """Отметить выбранную задачу как выполненную"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу для отметки")
            return

        item = selected[0]
        task_id = self.tree.item(item)['values'][0]  # Получаем ID из первой колонки

        try:
            self.controller.change_task_status(task_id, TaskStatus.COMPLETED)
            self.refresh_task_list()
            
            # Получаем задачу для сообщения
            task = self.controller.find_task(task_id)
            if task:
                messagebox.showinfo("Успех", f"Задача '{task.title}' отмечена как выполненная")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить задачу: {e}")

    def change_task_status(self, new_status: TaskStatus):
        """Изменить статус выбранной задачи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу")
            return

        item = selected[0]
        task_id = self.tree.item(item)['values'][0]  # Получаем ID из первой колонки

        try:
            self.controller.change_task_status(task_id, new_status)
            self.refresh_task_list()
            
            task = self.controller.find_task(task_id)
            if task:
                messagebox.showinfo("Успех", f"Статус задачи '{task.title}' изменен на '{new_status.value}'")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить статус: {e}")

    def delete_selected_task(self):
        """Удаление выбранной задачи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу для удаления")
            return

        item = selected[0]
        task_id = self.tree.item(item)['values'][0]  # Получаем ID из первой колонки

        task = self.controller.find_task(task_id)
        if task:
            result = messagebox.askyesno(
                "Подтверждение",
                f"Вы уверены, что хотите удалить задачу '{task.title}'?"
            )
            if result:
                try:
                    self.controller.delete_task(task_id)
                    self.refresh_task_list()
                    messagebox.showinfo("Успех", "Задача удалена")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить задачу: {e}")

    def show_task_details(self):
        """Показать детали выбранной задачи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу для просмотра")
            return

        item = selected[0]
        task_id = self.tree.item(item)['values'][0]  # Получаем ID из первой колонки

        task = self.controller.find_task(task_id)
        if task:
            details = f"""
Задача: {task.title}

Описание: {task.description or "Нет описания"}

Категория: {task.category if task.category else "Не указана"}
Приоритет: {task.priority}
Статус: {task.status.value}

Дата создания: {task.creation_date.strftime(DATE_FORMAT)}
Срок выполнения: {task.due_date.strftime(DATE_FORMAT) if task.due_date else "Не установлен"}

{'⚠ ЗАДАЧА ПРОСРОЧЕНА!' if task.is_overdue() else ''}
{'⏰ Срок истекает скоро!' if task.is_due_soon() else ''}
""".strip()

            messagebox.showinfo(f"Детали задачи", details)

    def show_filter_dialog(self):
        """Показать диалог фильтрации"""
        dialog = FilterDialog(self.root, self.controller)
        self.root.wait_window(dialog.dialog)
        self.refresh_task_list()

    def show_sort_menu(self):
        """Показать меню сортировки"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="По дате создания", command=lambda: self.apply_sort('creation_date'))
        menu.add_command(label="По сроку выполнения", command=lambda: self.apply_sort('due_date'))
        menu.add_command(label="По приоритету", command=lambda: self.apply_sort('priority'))
        menu.add_command(label="По названию", command=lambda: self.apply_sort('title'))
        menu.add_separator()
        menu.add_command(label="Сбросить сортировку", command=lambda: self.apply_sort('creation_date', False))

        menu.post(self.sort_btn.winfo_rootx(), self.sort_btn.winfo_rooty() + self.sort_btn.winfo_height())

    def apply_sort(self, column: str, reverse: bool = False):
        """Применить сортировку"""
        self.current_sort = {'column': column, 'reverse': reverse}
        sorted_tasks = self.controller.sort_tasks(column, reverse)
        self.controller.filtered_tasks = sorted_tasks
        self.refresh_task_list()

    def sort_by_column(self, column: str):
        """Сортировка по колонке таблицы"""
        column_map = {
            'title': 'title',
            'category': 'category',
            'priority': 'priority',
            'status': 'status',
            'due_date': 'due_date'
        }

        if column in column_map:
            self.apply_sort(column_map[column], not self.current_sort['reverse'])