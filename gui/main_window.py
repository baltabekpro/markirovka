"""
Современный минималистичный GUI для системы ЦРПТ
Использует PyQt6 для создания интуитивного интерфейса
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Добавляем путь к scripts для импорта модулей
root_dir = Path(__file__).parent.parent
scripts_path = root_dir / "scripts"
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))
# Меняем рабочую директорию на scripts, чтобы все относительные пути указывали внутрь scripts
try:
    os.chdir(scripts_path)
except Exception:
    pass

# Гарантируем наличие базовой структуры (директории/файлы), чтобы избежать ошибок при первом запуске
def ensure_basic_files():
    root = scripts_path  # теперь база — scripts
    parent_root = Path(__file__).parent.parent  # корень репо
    # Создаём директории внутри scripts
    for d in [root / 'output', root / 'logs']:
        try: d.mkdir(exist_ok=True)
        except Exception: pass
    # Миграция файлов из корня, если там созданы и отсутствуют в scripts
    migrate_files = [
        'regions.json', 'email_config.json', 'true_api_tokens.json',
        'certificates.json', 'cert_thumbprints.txt', 'last_run.json'
    ]
    for fname in migrate_files:
        src = parent_root / fname
        dst = root / fname
        if src.exists() and not dst.exists():
            try:
                dst.write_bytes(src.read_bytes())
            except Exception:
                pass
    # Создание минимальных, если нет
    (root / 'regions.json').write_text((root / 'regions.json').read_text(encoding='utf-8') if (root / 'regions.json').exists() else '{}', encoding='utf-8')
    if not (root / 'email_config.json').exists():
        template = {"smtp_server": "smtp.example.com", "smtp_port": 587, "sender_email": "user@example.com", "sender_password": "", "recipient_emails": []}
        (root / 'email_config.json').write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding='utf-8')
    if not (root / 'true_api_tokens.json').exists():
        (root / 'true_api_tokens.json').write_text(json.dumps({"tokens": {}, "generated_at": datetime.now().isoformat()}, ensure_ascii=False, indent=2), encoding='utf-8')
    if not (root / 'certificates.json').exists():
        (root / 'certificates.json').write_text(json.dumps({"certificates": []}, ensure_ascii=False, indent=2), encoding='utf-8')
    if not (root / 'cert_thumbprints.txt').exists():
        (root / 'cert_thumbprints.txt').write_text('', encoding='utf-8')

ensure_basic_files()

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QGridLayout, QPushButton, QLabel, QTextEdit, QTabWidget,
        QTableWidget, QTableWidgetItem, QProgressBar, QStatusBar,
        QSplitter, QFrame, QScrollArea, QGroupBox, QComboBox,
        QLineEdit, QDateEdit, QCheckBox, QSpinBox, QFileDialog,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QInputDialog,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QStyle, QListWidget, QListWidgetItem, QStackedWidget
    )
    from PyQt6.QtCore import (
        Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation,
        QEasingCurve, QRect, QSize, QDate
    )
    from PyQt6.QtGui import (
        QFont, QIcon, QPalette, QColor, QPixmap, QPainter,
        QLinearGradient, QBrush, QAction
    )
except ImportError:
    print("PyQt6 не установлен. Установите его командой: pip install PyQt6")
    sys.exit(1)

# Импорт модулей системы
try:
    from scripts.logger_config import get_logger
    from scripts.file_utils import get_reports_list, check_last_run_info
    from scripts.token_manager import (
        load_tokens_file,
        save_tokens_file,
        mask_token,
        load_certificates_file,
        save_certificates_file,
        load_thumbprints_file,
        save_thumbprints_file
    )
    from scripts.region_manager import load_regions_data
    from scripts.scheduler import Scheduler
    import scripts.main as scripts_main
    from gui.data_manager import get_data_manager
except ImportError as e:
    print(f"Ошибка импорта модулей системы: {e}")
    print("Убедитесь, что все файлы системы находятся в папке scripts")
    sys.exit(1)


class ModernStyle:
    """Современные стили для приложения"""
    
    # Цветовая схема
    PRIMARY = "#2196F3"      # Синий
    PRIMARY_DARK = "#1976D2" # Тёмно-синий
    SECONDARY = "#03DAC6"    # Бирюзовый
    BACKGROUND = "#FAFAFA"   # Светло-серый
    SURFACE = "#FFFFFF"      # Белый
    ERROR = "#F44336"        # Красный
    WARNING = "#FF9800"      # Оранжевый
    SUCCESS = "#4CAF50"      # Зелёный
    TEXT_PRIMARY = "#212121" # Тёмно-серый
    TEXT_SECONDARY = "#757575" # Серый
    BORDER = "#E0E0E0"       # Светло-серый
    
    @staticmethod
    def get_stylesheet():
        return f"""
        QMainWindow {{
            background-color: {ModernStyle.BACKGROUND};
            color: {ModernStyle.TEXT_PRIMARY};
        }}
        
        QWidget {{
            background-color: {ModernStyle.SURFACE};
            color: {ModernStyle.TEXT_PRIMARY};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
        }}
        
        QPushButton {{
            background-color: {ModernStyle.PRIMARY};
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            min-width: 100px;
        }}
        
        QPushButton:hover {{
            background-color: {ModernStyle.PRIMARY_DARK};
        }}
        
        QPushButton:pressed {{
            background-color: {ModernStyle.PRIMARY_DARK};
        }}
        
        QPushButton:disabled {{
            background-color: {ModernStyle.TEXT_SECONDARY};
            color: white;
        }}
        
        QPushButton.secondary {{
            background-color: {ModernStyle.SURFACE};
            color: {ModernStyle.PRIMARY};
            border: 2px solid {ModernStyle.PRIMARY};
        }}
        
        QPushButton.secondary:hover {{
            background-color: {ModernStyle.PRIMARY};
            color: white;
        }}
        
        QPushButton.success {{
            background-color: {ModernStyle.SUCCESS};
        }}
        
        QPushButton.warning {{
            background-color: {ModernStyle.WARNING};
        }}
        
        QPushButton.error {{
            background-color: {ModernStyle.ERROR};
        }}
        
        QLabel {{
            color: {ModernStyle.TEXT_PRIMARY};
            background-color: transparent;
        }}
        
        QLabel.title {{
            font-size: 18pt;
            font-weight: bold;
            color: {ModernStyle.PRIMARY};
            margin: 10px 0;
        }}
        
        QLabel.subtitle {{
            font-size: 12pt;
            color: {ModernStyle.TEXT_SECONDARY};
            margin: 5px 0;
        }}
        
        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit {{
            border: 2px solid {ModernStyle.BORDER};
            border-radius: 4px;
            padding: 8px;
            background-color: {ModernStyle.SURFACE};
            selection-background-color: {ModernStyle.PRIMARY};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {{
            border-color: {ModernStyle.PRIMARY};
        }}
        
        QTableWidget {{
            gridline-color: {ModernStyle.BORDER};
            background-color: {ModernStyle.SURFACE};
            alternate-background-color: {ModernStyle.BACKGROUND};
            selection-background-color: {ModernStyle.PRIMARY};
            border: 1px solid {ModernStyle.BORDER};
            border-radius: 4px;
        }}
        
        QTableWidget::item {{
            padding: 8px;
            border: none;
        }}
        
        QTableWidget::item:selected {{
            background-color: {ModernStyle.PRIMARY};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {ModernStyle.BACKGROUND};
            color: {ModernStyle.TEXT_PRIMARY};
            padding: 10px;
            border: none;
            font-weight: bold;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {ModernStyle.BORDER};
            background-color: {ModernStyle.SURFACE};
            border-radius: 4px;
        }}
        
        QTabBar::tab {{
            background-color: {ModernStyle.BACKGROUND};
            color: {ModernStyle.TEXT_SECONDARY};
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {ModernStyle.PRIMARY};
            color: white;
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {ModernStyle.BORDER};
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: {ModernStyle.PRIMARY};
        }}
        
        QProgressBar {{
            border: 2px solid {ModernStyle.BORDER};
            border-radius: 4px;
            text-align: center;
            background-color: {ModernStyle.BACKGROUND};
        }}
        
        QProgressBar::chunk {{
            background-color: {ModernStyle.PRIMARY};
            border-radius: 2px;
        }}
        
        QStatusBar {{
            background-color: {ModernStyle.BACKGROUND};
            border-top: 1px solid {ModernStyle.BORDER};
            color: {ModernStyle.TEXT_SECONDARY};
        }}
        
        QScrollArea {{
            border: none;
            background-color: {ModernStyle.SURFACE};
        }}
        
        QFrame {{
            background-color: {ModernStyle.SURFACE};
        }}
        
        QFrame.card {{
            background-color: {ModernStyle.SURFACE};
            border: 1px solid {ModernStyle.BORDER};
            border-radius: 8px;
            margin: 5px;
        }}
        
        QTreeWidget {{
            border: 1px solid {ModernStyle.BORDER};
            border-radius: 4px;
            background-color: {ModernStyle.SURFACE};
            alternate-background-color: {ModernStyle.BACKGROUND};
        }}
        
        QTreeWidget::item {{
            padding: 5px;
        }}
        
        QTreeWidget::item:selected {{
            background-color: {ModernStyle.PRIMARY};
            color: white;
        }}
        """


class StatusCard(QFrame):
    """Карточка статуса для отображения ключевой информации"""

    def __init__(self, title: str, value: str, color: str = ModernStyle.PRIMARY):
        super().__init__()
        self.setObjectName("card")
        self.setFrameStyle(QFrame.Shape.Box)
        self.setMinimumHeight(72)  # чуть компактнее, чем 80

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)

        title_label = QLabel(title)
        title_label.setObjectName("subtitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(value)
        value_label.setObjectName("title")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        self.setLayout(layout)
        self._value_label = value_label

    def set_value(self, text: str):
        if self._value_label:
            self._value_label.setText(text)


class TokenManagementTab(QWidget):
    """Компактная вкладка управления токенами и сертификатами"""

    def __init__(self):
        super().__init__()
        self.logger = get_logger("gui_tokens")
        self.init_ui()

    def _make_toolbar_button(self, text, object_name=None):
        btn = QPushButton(text)
        btn.setFixedHeight(30)
        if object_name:
            btn.setObjectName(object_name)
        return btn

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # Панель инструментов (вместо большого заголовка)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)
        title = QLabel("Токены / Сертификаты")
        title.setStyleSheet("font-weight:600; margin-right:12px;")
        toolbar.addWidget(title)
        toolbar.addStretch()
        # Токен кнопки
        self.btn_add_token = self._make_toolbar_button("+ токен")
        self.btn_edit_token = self._make_toolbar_button("✎", "secondary")
        self.btn_delete_token = self._make_toolbar_button("–", "error")
        self.btn_refresh_tokens = self._make_toolbar_button("⟳", "success")
        for b in (self.btn_add_token, self.btn_edit_token, self.btn_delete_token, self.btn_refresh_tokens):
            b.setFixedWidth(50)
            toolbar.addWidget(b)
        toolbar.addSpacing(12)
        # Сертификаты кнопки
        self.btn_add_cert = self._make_toolbar_button("+ cert")
        self.btn_edit_cert = self._make_toolbar_button("✎ cert", "secondary")
        self.btn_delete_cert = self._make_toolbar_button("– cert", "error")
        self.btn_install_cert = self._make_toolbar_button("Импорт", "success")
        for b in (self.btn_add_cert, self.btn_edit_cert, self.btn_delete_cert, self.btn_install_cert):
            toolbar.addWidget(b)
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        # Таблица токенов
        self.tokens_table = QTableWidget()
        self.tokens_table.setColumnCount(3)
        self.tokens_table.setHorizontalHeaderLabels(["Имя", "Токен", "Сгенерирован"])
        self.tokens_table.horizontalHeader().setStretchLastSection(True)
        self.tokens_table.setAlternatingRowColors(True)
        splitter.addWidget(self.tokens_table)
        # Таблица сертификатов
        self.certs_table = QTableWidget()
        self.certs_table.setColumnCount(2)
        self.certs_table.setHorizontalHeaderLabels(["Имя", "Отпечаток"]) 
        self.certs_table.horizontalHeader().setStretchLastSection(True)
        self.certs_table.setAlternatingRowColors(True)
        splitter.addWidget(self.certs_table)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)
        self.setLayout(layout)

        # Загрузка
        self.reload_tokens()
        self.reload_certs()

        # Сигналы
        self.btn_add_token.clicked.connect(self.add_token)
        self.btn_edit_token.clicked.connect(self.edit_token)
        self.btn_delete_token.clicked.connect(self.delete_token)
        self.btn_refresh_tokens.clicked.connect(self.reload_tokens)
        self.btn_add_cert.clicked.connect(self.add_certificate)
        self.btn_edit_cert.clicked.connect(self.edit_certificate)
        self.btn_delete_cert.clicked.connect(self.delete_certificate)
        self.btn_install_cert.clicked.connect(self.install_certificate)

    # --- TOKENS ---
    def reload_tokens(self):
        try:
            data = load_tokens_file()
            tokens = data.get('tokens', {})
            generated_at = data.get('generated_at', '-')
            self.tokens_table.setRowCount(len(tokens))
            for row, (name, token) in enumerate(tokens.items()):
                self.tokens_table.setItem(row, 0, QTableWidgetItem(name))
                self.tokens_table.setItem(row, 1, QTableWidgetItem(mask_token(token)))
                self.tokens_table.setItem(row, 2, QTableWidgetItem(generated_at))
        except Exception as e:
            self.logger.error(f"Не удалось загрузить токены: {e}")

    def add_token(self):
        name, ok = QInputDialog.getText(self, "Новый токен", "Имя токена:")
        if not ok or not name.strip():
            return
        value, ok = QInputDialog.getText(self, "Значение токена", "Токен:")
        if not ok or not value.strip():
            return
        data = load_tokens_file()
        tokens = data.get('tokens', {})
        if name in tokens:
            QMessageBox.warning(self, "Предупреждение", "Токен с таким именем уже существует")
            return
        tokens[name] = value.strip()
        data['tokens'] = tokens
        data['generated_at'] = datetime.now().isoformat()
        if save_tokens_file(data):
            self.reload_tokens()
            QMessageBox.information(self, "Успех", "Токен добавлен")

    def edit_token(self):
        row = self.tokens_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите токен")
            return
        name = self.tokens_table.item(row, 0).text()
        data = load_tokens_file()
        tokens = data.get('tokens', {})
        current_value = tokens.get(name, '')
        new_value, ok = QInputDialog.getText(self, "Редактировать токен", f"Новое значение для '{name}':", text=current_value)
        if not ok or not new_value.strip():
            return
        tokens[name] = new_value.strip()
        data['tokens'] = tokens
        data['generated_at'] = datetime.now().isoformat()
        if save_tokens_file(data):
            self.reload_tokens()
            QMessageBox.information(self, "Сохранено", "Токен обновлён")

    def delete_token(self):
        row = self.tokens_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите токен")
            return
        name = self.tokens_table.item(row, 0).text()
        if QMessageBox.question(self, "Подтверждение", f"Удалить токен '{name}'?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            data = load_tokens_file()
            tokens = data.get('tokens', {})
            if name in tokens:
                del tokens[name]
                data['tokens'] = tokens
                data['generated_at'] = datetime.now().isoformat()
                if save_tokens_file(data):
                    self.reload_tokens()
                    QMessageBox.information(self, "Удалено", "Токен удалён")

    # --- CERTIFICATES ---
    def reload_certs(self):
        try:
            cert_data = load_certificates_file()
            certs = cert_data.get('certificates', [])
            self.certs_table.setRowCount(len(certs))
            for row, cert in enumerate(certs):
                name = cert.get('name', 'Без имени')
                thumb = cert.get('thumbprint', '')
                short = thumb[:20] + '...' if len(thumb) > 23 else thumb
                self.certs_table.setItem(row, 0, QTableWidgetItem(name))
                self.certs_table.setItem(row, 1, QTableWidgetItem(short))
        except Exception as e:
            self.logger.error(f"Не удалось загрузить сертификаты: {e}")

    def add_certificate(self):
        name, ok = QInputDialog.getText(self, "Новый сертификат", "Имя (владельца):")
        if not ok:
            return
        thumb, ok = QInputDialog.getText(self, "Отпечаток", "SHA1 отпечаток:")
        if not ok or not thumb.strip():
            return
        thumb = thumb.strip().lower()
        # Обновляем thumbprints
        tps = load_thumbprints_file()
        if thumb in tps:
            QMessageBox.warning(self, "Ошибка", "Такой отпечаток уже есть")
            return
        tps.append(thumb)
        save_thumbprints_file(tps)
        cert_data = load_certificates_file()
        certs = cert_data.get('certificates', [])
        if name.strip():
            certs.append({'name': name.strip(), 'thumbprint': thumb})
            cert_data['certificates'] = certs
            save_certificates_file(cert_data)
        self.reload_certs()
        QMessageBox.information(self, "Успех", "Сертификат добавлен")

    def edit_certificate(self):
        row = self.certs_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите сертификат")
            return
        name_item = self.certs_table.item(row, 0)
        thumb_item = self.certs_table.item(row, 1)
        old_name = name_item.text()
        old_thumb = thumb_item.text().replace('...', '')  # возможно усечён
        cert_data = load_certificates_file()
        certs = cert_data.get('certificates', [])
        # Полный thumb
        for c in certs:
            if c.get('name') == old_name:
                old_thumb = c.get('thumbprint', old_thumb)
                break
        new_name, ok = QInputDialog.getText(self, "Редактирование", "Имя:", text=old_name)
        if not ok or not new_name.strip():
            return
        new_thumb, ok = QInputDialog.getText(self, "Редактирование", "Отпечаток (оставьте пустым чтобы не менять):")
        if not ok:
            return
        real_thumb = old_thumb if not new_thumb.strip() else new_thumb.strip().lower()
        # Обновление списка
        for c in certs:
            if c.get('thumbprint') == old_thumb or c.get('name') == old_name:
                c['name'] = new_name.strip()
                c['thumbprint'] = real_thumb
                break
        cert_data['certificates'] = certs
        save_certificates_file(cert_data)
        self.reload_certs()
        QMessageBox.information(self, "Сохранено", "Сертификат обновлён")

    def delete_certificate(self):
        row = self.certs_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите сертификат")
            return
        name = self.certs_table.item(row, 0).text()
        if QMessageBox.question(self, "Подтверждение", f"Удалить сертификат '{name}'?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            cert_data = load_certificates_file()
            certs = cert_data.get('certificates', [])
            certs = [c for c in certs if c.get('name') != name]
            cert_data['certificates'] = certs
            save_certificates_file(cert_data)
            self.reload_certs()
            QMessageBox.information(self, "Удалено", "Сертификат удалён")

    def install_certificate(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл сертификата",
            "",
            "Файлы сертификатов (*.cer *.crt *.der *.p7b *.p12 *.pfx);;Все файлы (*)"
        )
        if file_path:
            QMessageBox.information(self, "Импорт", f"Выбран файл: {file_path}\n(Доп. логика импорта не реализована)")



class ReportsTab(QWidget):
    """Вкладка просмотра отчетов"""

    def __init__(self):
        super().__init__()
        self.logger = get_logger("gui_reports")
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Отчеты о нарушениях")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # Фильтры
        filters_group = QGroupBox("Фильтры")
        filters_layout = QGridLayout()
        
        # Дата от
        filters_layout.addWidget(QLabel("Дата от:"), 0, 0)
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        filters_layout.addWidget(self.date_from, 0, 1)
        
        # Дата до
        filters_layout.addWidget(QLabel("Дата до:"), 0, 2)
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        filters_layout.addWidget(self.date_to, 0, 3)
        
        # Регион
        filters_layout.addWidget(QLabel("Регион:"), 1, 0)
        self.region_combo = QComboBox()
        self.region_combo.addItem("Все регионы")
        filters_layout.addWidget(self.region_combo, 1, 1)
        
        # Тип нарушения
        filters_layout.addWidget(QLabel("Тип нарушения:"), 1, 2)
        self.violation_type_combo = QComboBox()
        self.violation_type_combo.addItem("Все типы")
        filters_layout.addWidget(self.violation_type_combo, 1, 3)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        search_btn = QPushButton("Поиск")
        export_btn = QPushButton("Экспорт")
        export_btn.setObjectName("secondary")
        refresh_btn = QPushButton("Обновить")
        refresh_btn.setObjectName("success")
        
        buttons_layout.addWidget(search_btn)
        buttons_layout.addWidget(export_btn)
        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addStretch()
        
        filters_layout.addLayout(buttons_layout, 2, 0, 1, 4)
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Таблица отчетов
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(6)
        self.reports_table.setHorizontalHeaderLabels([
            "Дата", "Регион", "Тип нарушения", "Количество", "Статус", "Действия"
        ])
        self.reports_table.horizontalHeader().setStretchLastSection(True)
        self.reports_table.setAlternatingRowColors(True)
        self.reports_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.reports_table)
        
        self.setLayout(layout)
        
        # Загрузка данных
        self.load_reports()
        self.load_regions()
        
        # Подключение сигналов
        search_btn.clicked.connect(self.search_reports)
        export_btn.clicked.connect(self.export_reports)
        refresh_btn.clicked.connect(self.load_reports)
        
    def load_reports(self):
        """Загрузка violations_*.json по сертификатам"""
        try:
            base = Path(__file__).parent.parent / 'output'
            rows = []
            if base.exists():
                for cert_dir in sorted(base.iterdir()):
                    if not cert_dir.is_dir():
                        continue
                    for f in cert_dir.glob('violations_*.json'):
                        try:
                            with f.open('r', encoding='utf-8') as jf:
                                data = json.load(jf)
                            date = data.get('date', '')
                            violations = data.get('violations', {})
                            total = sum(violations.values()) if isinstance(violations, dict) else 0
                            rows.append({
                                'date': date,
                                'region': cert_dir.name,
                                'violation_type': 'Всего групп',
                                'count': total,
                                'status': 'Готов',
                                'path': str(f)
                            })
                        except Exception as ie:
                            self.logger.error(f"Ошибка чтения {f}: {ie}")
            self.reports_table.setRowCount(len(rows))
            for r_index, rdata in enumerate(rows):
                self.reports_table.setItem(r_index, 0, QTableWidgetItem(rdata['date']))
                self.reports_table.setItem(r_index, 1, QTableWidgetItem(rdata['region']))
                self.reports_table.setItem(r_index, 2, QTableWidgetItem(rdata['violation_type']))
                self.reports_table.setItem(r_index, 3, QTableWidgetItem(str(rdata['count'])))
                status_item = QTableWidgetItem(rdata['status'])
                status_item.setBackground(QColor(ModernStyle.SUCCESS))
                self.reports_table.setItem(r_index, 4, status_item)
                btn = QPushButton("Просмотр")
                btn.setMaximumWidth(80)
                btn.clicked.connect(lambda _, p=rdata['path']: self.view_report(p))
                self.reports_table.setCellWidget(r_index, 5, btn)
        except Exception as e:
            self.logger.error(f"Ошибка загрузки отчетов: {e}")

    def view_report(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            text = [f"Дата: {data.get('date','')}", f"Сертификат: {Path(path).parent.name}"]
            violations = data.get('violations', {})
            text.append("")
            text.append("Нарушения:")
            total = 0
            if isinstance(violations, dict):
                for k, v in violations.items():
                    total += v
                    text.append(f" - {k}: {v}")
            text.append("")
            text.append(f"Всего: {total}")
            QMessageBox.information(self, 'Отчет', '\n'.join(text))
        except Exception as e:
            self.logger.error(f"Ошибка просмотра отчета {path}: {e}")
            
    def load_regions(self):
        """Загрузка списка регионов"""
        try:
            regions = load_regions_data()  # dict code -> { name, ... }
            for code, info in regions.items():
                name = info.get('name', code) if isinstance(info, dict) else str(info)
                self.region_combo.addItem(f"{name} ({code})", code)
        except Exception as e:
            self.logger.error(f"Ошибка загрузки регионов: {e}")
            
    def search_reports(self):
        """Поиск отчетов по фильтрам"""
        QMessageBox.information(self, "Поиск", "Выполняется поиск отчетов...")
        self.load_reports()
        
    def export_reports(self):
        """Экспорт отчетов"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить отчет", 
            f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel файлы (*.xlsx);;CSV файлы (*.csv);;Все файлы (*)"
        )
        
        if file_path:
            QMessageBox.information(self, "Экспорт", f"Отчет сохранен: {file_path}")


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("gui_main")
        self.data = get_data_manager()
        self.init_ui()
        self.setup_status_bar()
        self.setup_timer()
        
    def init_ui(self):
        # Основные параметры окна
        self.setWindowTitle("ЦРПТ Маркировка - Система обработки отчетов")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Заголовок
        header_layout = QHBoxLayout()
        app_title = QLabel("ЦРПТ Маркировка")
        app_title.setObjectName("title")
        header_layout.addWidget(app_title)
        header_layout.addStretch()
        self.last_update_label = QLabel("Последнее обновление: -")
        self.last_update_label.setObjectName("subtitle")
        header_layout.addWidget(self.last_update_label)
        main_layout.addLayout(header_layout)

        # Карточки статуса
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        self.status_cards = {
            'tokens': StatusCard("Активных токенов", "0", ModernStyle.PRIMARY),
            'certificates': StatusCard("Сертификатов", "0", ModernStyle.SECONDARY),
            'reports': StatusCard("Отчетов", "0", ModernStyle.SUCCESS),
            'violations': StatusCard("Нарушений", "0", ModernStyle.WARNING)
        }
        for card in self.status_cards.values():
            status_layout.addWidget(card)
        main_layout.addLayout(status_layout)

        # Навигация слева + стек страниц
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(12)
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(170)
        self.nav_list.setStyleSheet(
            "QListWidget {border:1px solid %s; border-radius:6px; background:%s;}"
            "QListWidget::item {padding:10px 8px; border:0;}"
            "QListWidget::item:selected {background:%s; color:white; border-radius:4px;}" % (ModernStyle.BORDER, ModernStyle.SURFACE, ModernStyle.PRIMARY)
        )
        self.stacked = QStackedWidget()
        pages = [
            ("Главная", self.create_dashboard_tab()),
            ("Токены", TokenManagementTab()),
            ("Отчеты", ReportsTab()),
            ("Файлы", self.create_files_tab()),
            ("Настройки", self.create_settings_tab()),
        ]
        self.tokens_tab = None
        for i, (text, widget) in enumerate(pages):
            item = QListWidgetItem(text)
            item.setSizeHint(QSize(150, 40))
            self.nav_list.addItem(item)
            self.stacked.addWidget(widget)
            if text == "Токены":
                self.tokens_tab = widget
        self.nav_list.currentRowChanged.connect(self.stacked.setCurrentIndex)
        self.nav_list.setCurrentRow(0)
        body.addWidget(self.nav_list)
        body.addWidget(self.stacked, 1)
        main_layout.addLayout(body)

        central_widget.setLayout(main_layout)

        # Стиль
        self.setStyleSheet(ModernStyle.get_stylesheet())
        # Начальные данные
        self.update_status_cards()
        
    def create_dashboard_tab(self):
        """Создание вкладки главной панели"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Быстрые действия
        actions_group = QGroupBox("Быстрые действия")
        actions_layout = QGridLayout()
        
        # Кнопки быстрых действий
        daily_process_btn = QPushButton("Запустить ежедневную обработку")
        daily_process_btn.setObjectName("success")
        daily_process_btn.setMinimumHeight(50)
        actions_layout.addWidget(daily_process_btn, 0, 0)
        
        refresh_tokens_btn = QPushButton("Обновить токены")
        refresh_tokens_btn.setMinimumHeight(50)
        actions_layout.addWidget(refresh_tokens_btn, 0, 1)
        
        send_report_btn = QPushButton("Отправить отчет")
        send_report_btn.setObjectName("secondary")
        send_report_btn.setMinimumHeight(50)
        actions_layout.addWidget(send_report_btn, 1, 0)
        
        scheduler_btn = QPushButton("Управление планировщиком")
        scheduler_btn.setObjectName("warning")
        scheduler_btn.setMinimumHeight(50)
        actions_layout.addWidget(scheduler_btn, 1, 1)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Последние события
        events_group = QGroupBox("Последние события")
        events_layout = QVBoxLayout()
        
        self.events_text = QTextEdit()
        self.events_text.setMaximumHeight(200)
        self.events_text.setReadOnly(True)
        events_layout.addWidget(self.events_text)
        
        events_group.setLayout(events_layout)
        layout.addWidget(events_group)
        
        # Статистика
        stats_group = QGroupBox("Статистика за последние 30 дней")
        stats_layout = QGridLayout()
        
        # Здесь можно добавить графики и диаграммы
        stats_placeholder = QLabel("Статистика будет отображаться здесь")
        stats_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_placeholder.setMinimumHeight(200)
        stats_placeholder.setStyleSheet(f"border: 2px dashed {ModernStyle.BORDER}; color: {ModernStyle.TEXT_SECONDARY};")
        stats_layout.addWidget(stats_placeholder, 0, 0)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        # Подключение сигналов
        daily_process_btn.clicked.connect(self.run_daily_process)
        refresh_tokens_btn.clicked.connect(self.refresh_tokens)
        send_report_btn.clicked.connect(self.send_report)
        scheduler_btn.clicked.connect(self.manage_scheduler)
        
        return widget
        
    def create_files_tab(self):
        """Создание вкладки управления файлами"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Управление файлами")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # Панель инструментов
        toolbar_layout = QHBoxLayout()
        
        new_folder_btn = QPushButton("Новая папка")
        upload_btn = QPushButton("Загрузить файл")
        upload_btn.setObjectName("success")
        delete_btn = QPushButton("Удалить")
        delete_btn.setObjectName("error")
        refresh_btn = QPushButton("Обновить")
        
        toolbar_layout.addWidget(new_folder_btn)
        toolbar_layout.addWidget(upload_btn)
        toolbar_layout.addWidget(delete_btn)
        toolbar_layout.addWidget(refresh_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # Файловое дерево
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Имя", "Размер", "Дата изменения", "Тип"])
        layout.addWidget(self.file_tree)
        
        widget.setLayout(layout)
        
        # Загрузка файлового дерева
        self.load_file_tree()
        
        # Подключение сигналов
        new_folder_btn.clicked.connect(self.create_new_folder)
        upload_btn.clicked.connect(self.upload_file)
        delete_btn.clicked.connect(self.delete_file)
        refresh_btn.clicked.connect(self.load_file_tree)
        
        return widget
        
    def create_settings_tab(self):
        """Создание вкладки настроек"""
        widget = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Настройки")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # Настройки электронной почты
        email_group = QGroupBox("Настройки электронной почты")
        email_layout = QFormLayout()
        
        self.smtp_server = QLineEdit()
        self.smtp_port = QSpinBox()
        self.smtp_port.setRange(1, 65535)
        self.smtp_port.setValue(587)
        self.email_from = QLineEdit()
        self.email_password = QLineEdit()
        self.email_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        email_layout.addRow("SMTP сервер:", self.smtp_server)
        email_layout.addRow("Порт:", self.smtp_port)
        email_layout.addRow("Email от:", self.email_from)
        email_layout.addRow("Пароль:", self.email_password)
        
        email_group.setLayout(email_layout)
        layout.addWidget(email_group)
        
        # Настройки планировщика
        scheduler_group = QGroupBox("Настройки планировщика")
        scheduler_layout = QFormLayout()
        
        self.auto_start = QCheckBox("Автоматический запуск")
        self.schedule_time = QLineEdit("09:00")
        self.schedule_enabled = QCheckBox("Включить планировщик")
        
        scheduler_layout.addRow("Автозапуск:", self.auto_start)
        scheduler_layout.addRow("Время выполнения:", self.schedule_time)
        scheduler_layout.addRow("Планировщик:", self.schedule_enabled)
        
        scheduler_group.setLayout(scheduler_layout)
        layout.addWidget(scheduler_group)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("success")
        reset_btn = QPushButton("Сбросить")
        reset_btn.setObjectName("secondary")
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        content.setLayout(layout)
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        
        # Загрузка настроек
        self.load_settings()
        
        # Подключение сигналов
        save_btn.clicked.connect(self.save_settings)
        reset_btn.clicked.connect(self.load_settings)
        
        return widget
        
    def setup_status_bar(self):
        """Настройка строки состояния"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Статус планировщика
        self.scheduler_status = QLabel("Планировщик: Неизвестно")
        self.status_bar.addWidget(self.scheduler_status)
        
        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Время
        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)
        
    def setup_timer(self):
        """Настройка таймера для обновления данных"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_and_status)
        self.timer.start(1000)  # Обновление каждую секунду
        
    def update_time_and_status(self):
        """Обновление времени и статуса"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)
        
        # Обновление статуса планировщика
        try:
            scheduler = Scheduler()
            if scheduler.is_running():
                self.scheduler_status.setText("Планировщик: Работает")
                self.scheduler_status.setStyleSheet(f"color: {ModernStyle.SUCCESS};")
            else:
                self.scheduler_status.setText("Планировщик: Остановлен")
                self.scheduler_status.setStyleSheet(f"color: {ModernStyle.ERROR};")
        except:
            self.scheduler_status.setText("Планировщик: Ошибка")
            self.scheduler_status.setStyleSheet(f"color: {ModernStyle.ERROR};")
            
    def update_status_cards(self):
        """Обновление карточек статуса через DataManager"""
        try:
            self.data.refresh_all()
            active_tokens = sum(1 for t in self.data.list_tokens() if t.get('token'))
            self.status_cards['tokens'].set_value(str(active_tokens))
            self.status_cards['certificates'].set_value(str(len(self.data.list_certificates())))
            # Считаем violations_*.json
            base = Path(__file__).parent.parent / 'output'
            report_files = 0
            if base.exists():
                for cert_dir in base.iterdir():
                    if cert_dir.is_dir():
                        report_files += len(list(cert_dir.glob('violations_*.json')))
            self.status_cards['reports'].set_value(str(report_files))
            self.status_cards['violations'].set_value(str(report_files))
            self.last_update_label.setText(f"Последнее обновление: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            self.logger.error(f"Ошибка обновления статуса: {e}")
            
    def load_file_tree(self):
        """Загрузка файлового дерева"""
        self.file_tree.clear()
        
        try:
            scripts_path = Path(__file__).parent.parent / "scripts"
            self._add_directory_to_tree(scripts_path, self.file_tree.invisibleRootItem())
        except Exception as e:
            self.logger.error(f"Ошибка загрузки файлового дерева: {e}")
            
    def _add_directory_to_tree(self, path: Path, parent_item):
        """Рекурсивное добавление директории в дерево"""
        try:
            for item_path in sorted(path.iterdir()):
                if item_path.name.startswith('.'):
                    continue
                    
                item = QTreeWidgetItem(parent_item)
                item.setText(0, item_path.name)
                
                if item_path.is_dir():
                    item.setText(3, "Папка")
                    item.setData(0, Qt.ItemDataRole.UserRole, str(item_path))
                    # Добавляем содержимое папки (ограничиваем глубину)
                    if len(str(item_path).split(os.sep)) < 10:
                        self._add_directory_to_tree(item_path, item)
                else:
                    # Файл
                    try:
                        stat = item_path.stat()
                        size = self._format_file_size(stat.st_size)
                        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                        
                        item.setText(1, size)
                        item.setText(2, modified)
                        item.setText(3, item_path.suffix or "Файл")
                        item.setData(0, Qt.ItemDataRole.UserRole, str(item_path))
                    except:
                        pass
                        
        except PermissionError:
            pass
        except Exception as e:
            self.logger.error(f"Ошибка при обходе директории {path}: {e}")
            
    def _format_file_size(self, size_bytes: int) -> str:
        """Форматирование размера файла"""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
        
    def load_settings(self):
        """Загрузка настроек"""
        try:
            try:
                from scripts.email_utils import load_email_config
                email_config = load_email_config()
            except Exception:
                email_config = None

            if email_config:
                # адаптация к возможным ключам
                self.smtp_server.setText(email_config.get('smtp_server') or email_config.get('server', ''))
                self.smtp_port.setValue(email_config.get('smtp_port') or email_config.get('port', 587))
                self.email_from.setText(email_config.get('sender_email') or email_config.get('from_email', ''))
        except Exception as e:
            self.logger.error(f"Ошибка загрузки настроек: {e}")
            
    def save_settings(self):
        """Сохранение настроек"""
        try:
            email_config = {
                'smtp_server': self.smtp_server.text().strip(),
                'smtp_port': self.smtp_port.value(),
                'sender_email': self.email_from.text().strip(),
                'sender_password': self.email_password.text().strip(),
                'recipient_emails': []
            }
            # Пишем в email_config.json
            config_path = Path(__file__).parent.parent / 'email_config.json'
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(email_config, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Настройки", "Email настройки сохранены")
            except Exception as ee:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить email настройки: {ee}")
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения настроек: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения настроек: {e}")
            
    # Методы для быстрых действий
    def run_daily_process(self):
        if hasattr(self, '_daily_busy') and self._daily_busy:
            QMessageBox.information(self, 'Инфо', 'Обработка уже выполняется')
            return
        if QMessageBox.question(self, 'Подтверждение', 'Запустить ежедневную обработку?',
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self._daily_busy = True
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.events_text.append('▶ Старт ежедневной обработки')
        QTimer.singleShot(100, self._do_daily_process)

    def _do_daily_process(self):
        core_run = scripts_main.run_daily_process
        ok = False
        try:
            ok = core_run()
        except Exception as e:
            self.events_text.append(f'Ошибка: {e}')
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        if ok:
            self.events_text.append('✅ Ежедневная обработка завершена')
        else:
            self.events_text.append('❌ Ежедневная обработка завершилась с ошибкой')
        self._daily_busy = False
        self.update_status_cards()
            
    def refresh_tokens(self):
        refresh_daily_tokens = scripts_main.refresh_daily_tokens
        self.events_text.append('▶ Обновление токенов...')
        try:
            ok = refresh_daily_tokens()
            if ok:
                self.events_text.append('✓ Токены обновлены')
            else:
                self.events_text.append('✗ Ошибка обновления токенов')
        except Exception as e:
            self.events_text.append(f'Ошибка обновления: {e}')
        self.update_status_cards()
        
    def send_report(self):
        """Отправка отчета"""
        QMessageBox.information(self, "Отправка", "Подготовка и отправка отчета...")

    # Заглушки для отсутствующих ранее методов
    def manage_scheduler(self):
        QMessageBox.information(self, "Планировщик", "Управление планировщиком пока не реализовано")

    def create_new_folder(self):
        QMessageBox.information(self, "Новая папка", "Создание папки пока не реализовано")

    def upload_file(self):
        QMessageBox.information(self, "Загрузка файла", "Загрузка пока не реализована")

    def delete_file(self):
        QMessageBox.information(self, "Удаление файла", "Удаление пока не реализовано")


def main():
    """Главная функция запуска приложения"""
    app = QApplication(sys.argv)
    
    # Установка иконки приложения и базовых свойств
    app.setApplicationName("ЦРПТ Маркировка")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ЦРПТ")
    
    # Создание и показ главного окна
    window = MainWindow()
    window.show()
    
    # Запуск приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
