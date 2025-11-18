"""
Константы приложения
"""

# Цвета для статусов задач
STATUS_COLORS = {
    'Не начата': '#FFFFFF',
    'В процессе': '#FFF9C4',  # светло-желтый
    'Выполнена': '#C8E6C9',   # светло-зеленый
    'Отложена': '#FFCCBC'     # светло-оранжевый
}

# Цвета для приоритетов
PRIORITY_COLORS = {
    'Высокий': '#FF5252',     # красный
    'Средний': '#FFB74D',     # оранжевый
    'Низкий': '#4CAF50'       # зеленый
}

# Размеры окон
MAIN_WINDOW_SIZE = "900x700"
DIALOG_SIZE = "400x300"

# Форматы дат
DATE_FORMAT = "%d.%m.%Y"
DATETIME_FORMAT = "%d.%m.%Y %H:%M"

# Пути к файлам
DATA_DIR = "data"
TASKS_FILE = "data/tasks.json"
CONFIG_FILE = "data/config.json"
LOG_FILE = "todo_app.log"