"""
Кастомные виджеты для GUI приложения
"""

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QFrame, QScrollArea, QTextEdit, QProgressBar, QGroupBox,
        QListWidget, QListWidgetItem, QSizePolicy, QSpacerItem
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QPropertyAnimation, QRect
    from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QLinearGradient, QBrush
except ImportError:
    print("PyQt6 не установлен. Установите его командой: pip install PyQt6")
    exit(1)

import sys
from datetime import datetime
from pathlib import Path

# Добавляем путь к scripts
scripts_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))

try:
    from logger_config import get_logger
except ImportError:
    # Заглушка для логгера, если модуль недоступен
    class DummyLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
    
    def get_logger(name):
        return DummyLogger()


class AnimatedCard(QFrame):
    """Анимированная карточка с эффектом наведения"""
    
    clicked = pyqtSignal()
    
    def __init__(self, title: str, value: str, description: str = "", color: str = "#2196F3"):
        super().__init__()
        self.color = color
        self.is_hovered = False
        self.setup_ui(title, value, description)
        self.setup_animation()
        
    def setup_ui(self, title: str, value: str, description: str):
        self.setFixedSize(200, 120)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"""
            AnimatedCard {{
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }}
            AnimatedCard:hover {{
                border-color: {self.color};
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: #757575; font-size: 10pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Значение
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {self.color}; font-size: 24pt; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Описание
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #9E9E9E; font-size: 8pt;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
            
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        self.setLayout(layout)
        
    def setup_animation(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        
    def enterEvent(self, event):
        self.is_hovered = True
        current_rect = self.geometry()
        hover_rect = QRect(
            current_rect.x() - 2,
            current_rect.y() - 2,
            current_rect.width() + 4,
            current_rect.height() + 4
        )
        self.animation.setStartValue(current_rect)
        self.animation.setEndValue(hover_rect)
        self.animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.is_hovered = False
        current_rect = self.geometry()
        normal_rect = QRect(
            current_rect.x() + 2,
            current_rect.y() + 2,
            current_rect.width() - 4,
            current_rect.height() - 4
        )
        self.animation.setStartValue(current_rect)
        self.animation.setEndValue(normal_rect)
        self.animation.start()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class LogViewer(QWidget):
    """Виджет для просмотра логов в реальном времени"""
    
    def __init__(self, log_file_path: str = None):
        super().__init__()
        self.log_file_path = log_file_path
        self.logger = get_logger("gui_log_viewer")
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        header = QHBoxLayout()
        self.title_label = QLabel("Журнал событий")
        self.title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2196F3;")
        
        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.setMaximumWidth(80)
        self.clear_btn.clicked.connect(self.clear_logs)
        
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.clear_btn)
        
        layout.addLayout(header)
        
        # Текстовое поле для логов
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #3E3E3E;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
            }
        """)
        
        layout.addWidget(self.log_text)
        self.setLayout(layout)
        
    def setup_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_logs)
        self.update_timer.start(2000)  # Обновление каждые 2 секунды
        
    def update_logs(self):
        """Обновление содержимого логов"""
        try:
            if self.log_file_path and Path(self.log_file_path).exists():
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Показываем только последние 50 строк
                    lines = content.split('\n')
                    recent_lines = lines[-50:] if len(lines) > 50 else lines
                    self.log_text.setPlainText('\n'.join(recent_lines))
                    
                    # Прокручиваем к концу
                    scrollbar = self.log_text.verticalScrollBar()
                    scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            self.logger.error(f"Ошибка обновления логов: {e}")
            
    def clear_logs(self):
        """Очистка отображаемых логов"""
        self.log_text.clear()
        
    def add_log_entry(self, message: str, level: str = "INFO"):
        """Добавление записи в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color_map = {
            "INFO": "#00FF00",
            "WARNING": "#FFFF00", 
            "ERROR": "#FF0000",
            "DEBUG": "#00FFFF"
        }
        color = color_map.get(level, "#FFFFFF")
        
        formatted_message = f'<span style="color: {color};">[{timestamp}] {level}: {message}</span>'
        self.log_text.append(formatted_message)
        
        # Ограничиваем количество строк
        if self.log_text.document().lineCount() > 100:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, 10)
            cursor.removeSelectedText()


class StatusIndicator(QWidget):
    """Индикатор статуса с цветовой индикацией"""
    
    def __init__(self, title: str, status: str = "unknown"):
        super().__init__()
        self.title = title
        self.status = status
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Индикатор
        self.indicator = QLabel("●")
        self.indicator.setFixedSize(16, 16)
        self.update_indicator()
        
        # Текст
        self.text_label = QLabel(self.title)
        self.text_label.setStyleSheet("font-weight: bold;")
        
        layout.addWidget(self.indicator)
        layout.addWidget(self.text_label)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def update_status(self, status: str):
        """Обновление статуса"""
        self.status = status
        self.update_indicator()
        
    def update_indicator(self):
        """Обновление цвета индикатора"""
        color_map = {
            "active": "#4CAF50",    # Зелёный
            "inactive": "#F44336",  # Красный
            "warning": "#FF9800",   # Оранжевый
            "unknown": "#9E9E9E"    # Серый
        }
        color = color_map.get(self.status, "#9E9E9E")
        self.indicator.setStyleSheet(f"color: {color}; font-size: 16pt;")


class ProgressWidget(QWidget):
    """Виджет прогресса с анимацией"""
    
    def __init__(self, title: str = "Выполнение операции"):
        super().__init__()
        self.title = title
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Заголовок
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 12pt; font-weight: bold; margin-bottom: 10px;")
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 4px;
            }
        """)
        
        # Статус
        self.status_label = QLabel("Готов к началу")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #757575; margin-top: 5px;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def update_progress(self, value: int, status: str = ""):
        """Обновление прогресса"""
        self.progress_bar.setValue(value)
        if status:
            self.status_label.setText(status)
            
    def set_indeterminate(self, enabled: bool):
        """Включение/выключение неопределённого прогресса"""
        if enabled:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 100)


class QuickActionButton(QPushButton):
    """Кнопка быстрого действия с иконкой и описанием"""
    
    def __init__(self, title: str, description: str, icon: str = None):
        super().__init__()
        self.title = title
        self.description = description
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumHeight(80)
        self.setMaximumHeight(80)
        
        # Создаём layout для кнопки
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Заголовок
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Описание
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("color: #757575; font-size: 9pt;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        
        # Создаём виджет для содержимого
        widget = QWidget()
        widget.setLayout(layout)
        
        # Устанавливаем виджет как содержимое кнопки
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(widget)
        self.setLayout(button_layout)
        
        # Стили
        self.setStyleSheet("""
            QuickActionButton {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                text-align: left;
            }
            QuickActionButton:hover {
                border-color: #2196F3;
                background-color: #F5F5F5;
            }
            QuickActionButton:pressed {
                background-color: #EEEEEE;
            }
        """)


class NotificationWidget(QFrame):
    """Виджет уведомлений"""
    
    def __init__(self, message: str, notification_type: str = "info"):
        super().__init__()
        self.message = message
        self.notification_type = notification_type
        self.setup_ui()
        self.setup_auto_hide()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Иконка (символ)
        icon_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        color_map = {
            "info": "#2196F3",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "error": "#F44336"
        }
        
        icon = QLabel(icon_map.get(self.notification_type, "ℹ️"))
        icon.setStyleSheet(f"font-size: 16pt; color: {color_map.get(self.notification_type, '#2196F3')};")
        
        # Сообщение
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 10pt;")
        
        # Кнопка закрытия
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #757575;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #F44336;
            }
        """)
        close_btn.clicked.connect(self.close_notification)
        
        layout.addWidget(icon)
        layout.addWidget(message_label)
        layout.addStretch()
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Стили фрейма
        bg_color = color_map.get(self.notification_type, '#2196F3') + "20"  # 20% прозрачности
        border_color = color_map.get(self.notification_type, '#2196F3')
        
        self.setStyleSheet(f"""
            NotificationWidget {{
                background-color: {bg_color};
                border-left: 4px solid {border_color};
                border-radius: 4px;
                margin: 5px 0;
            }}
        """)
        
    def setup_auto_hide(self):
        """Автоматическое скрытие уведомления"""
        if self.notification_type in ["info", "success"]:
            QTimer.singleShot(5000, self.close_notification)  # Скрыть через 5 секунд
            
    def close_notification(self):
        """Закрытие уведомления"""
        self.setParent(None)
        self.deleteLater()


class DataTableWidget(QWidget):
    """Улучшенная таблица данных с поиском и фильтрацией"""
    
    def __init__(self, headers: list):
        super().__init__()
        self.headers = headers
        self.data = []
        self.filtered_data = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Панель поиска
        search_layout = QHBoxLayout()
        
        search_label = QLabel("Поиск:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.textChanged.connect(self.filter_data)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        
        layout.addLayout(search_layout)
        
        # Таблица (используем QListWidget для простоты)
        self.table_list = QListWidget()
        layout.addWidget(self.table_list)
        
        self.setLayout(layout)
        
    def set_data(self, data: list):
        """Установка данных в таблицу"""
        self.data = data
        self.filtered_data = data.copy()
        self.update_display()
        
    def filter_data(self, search_text: str):
        """Фильтрация данных по поисковому запросу"""
        if not search_text:
            self.filtered_data = self.data.copy()
        else:
            self.filtered_data = [
                item for item in self.data
                if any(search_text.lower() in str(value).lower() for value in item.values())
            ]
        self.update_display()
        
    def update_display(self):
        """Обновление отображения таблицы"""
        self.table_list.clear()
        
        for item in self.filtered_data:
            # Создаём строку для отображения
            display_text = " | ".join([f"{k}: {v}" for k, v in item.items()])
            list_item = QListWidgetItem(display_text)
            self.table_list.addItem(list_item)
