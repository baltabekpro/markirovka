"""
Диалоги для управления токенами и сертификатами
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QCheckBox,
    QPushButton, QLabel, QDialogButtonBox, QMessageBox,
    QFileDialog, QGroupBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import json
from datetime import datetime
from pathlib import Path


class TokenDialog(QDialog):
    """Диалог для добавления/редактирования токена"""
    
    def __init__(self, parent=None, token_data=None):
        super().__init__(parent)
        self.token_data = token_data
        self.setWindowTitle("Управление токеном" if token_data else "Добавить токен")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Основная информация
        main_group = QGroupBox("Основная информация")
        main_layout = QFormLayout()
        
        self.inn_edit = QLineEdit()
        self.inn_edit.setPlaceholderText("Введите ИНН")
        main_layout.addRow("ИНН:", self.inn_edit)
        
        self.region_combo = QComboBox()
        self.region_combo.setEditable(True)
        self.region_combo.addItems([
            "Москва", "Санкт-Петербург", "Московская область",
            "Краснодарский край", "Республика Татарстан"
        ])
        main_layout.addRow("Регион:", self.region_combo)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Описание токена (необязательно)")
        main_layout.addRow("Описание:", self.description_edit)
        
        main_group.setLayout(main_layout)
        layout.addWidget(main_group)
        
        # Настройки токена
        token_group = QGroupBox("Настройки токена")
        token_layout = QFormLayout()
        
        self.auto_refresh = QCheckBox("Автоматическое обновление")
        self.auto_refresh.setChecked(True)
        token_layout.addRow("", self.auto_refresh)
        
        self.expires_date = QDateEdit()
        self.expires_date.setDate(QDate.currentDate().addDays(30))
        self.expires_date.setCalendarPopup(True)
        token_layout.addRow("Срок действия:", self.expires_date)
        
        token_group.setLayout(token_layout)
        layout.addWidget(token_group)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Заполнение данными при редактировании
        if self.token_data:
            self.load_token_data()
            
    def load_token_data(self):
        """Загрузка данных токена для редактирования"""
        if self.token_data:
            self.inn_edit.setText(self.token_data.get('inn', ''))
            self.region_combo.setCurrentText(self.token_data.get('region', ''))
            self.description_edit.setPlainText(self.token_data.get('description', ''))
            self.auto_refresh.setChecked(self.token_data.get('auto_refresh', True))
            
    def get_token_data(self):
        """Получение данных из формы"""
        return {
            'inn': self.inn_edit.text().strip(),
            'region': self.region_combo.currentText().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'auto_refresh': self.auto_refresh.isChecked(),
            'expires_date': self.expires_date.date().toString(Qt.DateFormat.ISODate),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def accept(self):
        """Валидация перед сохранением"""
        if not self.inn_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Поле ИНН обязательно для заполнения")
            return
            
        if not self.region_combo.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Поле Регион обязательно для заполнения")
            return
            
        super().accept()


class CertificateDialog(QDialog):
    """Диалог для добавления/редактирования сертификата"""
    
    def __init__(self, parent=None, cert_data=None):
        super().__init__(parent)
        self.cert_data = cert_data
        self.setWindowTitle("Управление сертификатом" if cert_data else "Добавить сертификат")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Информация о сертификате
        cert_group = QGroupBox("Информация о сертификате")
        cert_layout = QFormLayout()
        
        self.thumbprint_edit = QLineEdit()
        self.thumbprint_edit.setPlaceholderText("Введите отпечаток сертификата")
        cert_layout.addRow("Отпечаток:", self.thumbprint_edit)
        
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Субъект сертификата")
        cert_layout.addRow("Субъект:", self.subject_edit)
        
        self.issuer_edit = QLineEdit()
        self.issuer_edit.setPlaceholderText("Издатель сертификата")
        cert_layout.addRow("Издатель:", self.issuer_edit)
        
        self.valid_from = QDateEdit()
        self.valid_from.setDate(QDate.currentDate())
        self.valid_from.setCalendarPopup(True)
        cert_layout.addRow("Действителен с:", self.valid_from)
        
        self.valid_to = QDateEdit()
        self.valid_to.setDate(QDate.currentDate().addYears(1))
        self.valid_to.setCalendarPopup(True)
        cert_layout.addRow("Действителен до:", self.valid_to)
        
        cert_group.setLayout(cert_layout)
        layout.addWidget(cert_group)
        
        # ИНН список
        inn_group = QGroupBox("Список ИНН")
        inn_layout = QVBoxLayout()
        
        # Список ИНН
        self.inn_list = QListWidget()
        self.inn_list.setMaximumHeight(120)
        inn_layout.addWidget(self.inn_list)
        
        # Управление ИНН
        inn_controls = QHBoxLayout()
        self.new_inn_edit = QLineEdit()
        self.new_inn_edit.setPlaceholderText("Введите новый ИНН")
        add_inn_btn = QPushButton("Добавить")
        remove_inn_btn = QPushButton("Удалить")
        
        inn_controls.addWidget(self.new_inn_edit)
        inn_controls.addWidget(add_inn_btn)
        inn_controls.addWidget(remove_inn_btn)
        
        inn_layout.addLayout(inn_controls)
        inn_group.setLayout(inn_layout)
        layout.addWidget(inn_group)
        
        # Дополнительные настройки
        settings_group = QGroupBox("Настройки")
        settings_layout = QFormLayout()
        
        self.is_valid = QCheckBox("Сертификат действителен")
        self.is_valid.setChecked(True)
        settings_layout.addRow("", self.is_valid)
        
        self.auto_check = QCheckBox("Автоматическая проверка срока действия")
        self.auto_check.setChecked(True)
        settings_layout.addRow("", self.auto_check)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Подключение сигналов
        add_inn_btn.clicked.connect(self.add_inn)
        remove_inn_btn.clicked.connect(self.remove_inn)
        
        # Заполнение данными при редактировании
        if self.cert_data:
            self.load_cert_data()
            
    def add_inn(self):
        """Добавление ИНН в список"""
        inn = self.new_inn_edit.text().strip()
        if inn and inn not in [self.inn_list.item(i).text() for i in range(self.inn_list.count())]:
            self.inn_list.addItem(inn)
            self.new_inn_edit.clear()
        elif inn:
            QMessageBox.warning(self, "Предупреждение", "Такой ИНН уже добавлен")
            
    def remove_inn(self):
        """Удаление ИНН из списка"""
        current_row = self.inn_list.currentRow()
        if current_row >= 0:
            self.inn_list.takeItem(current_row)
            
    def load_cert_data(self):
        """Загрузка данных сертификата для редактирования"""
        if self.cert_data:
            self.thumbprint_edit.setText(self.cert_data.get('thumbprint', ''))
            self.subject_edit.setText(self.cert_data.get('subject', ''))
            self.issuer_edit.setText(self.cert_data.get('issuer', ''))
            self.is_valid.setChecked(self.cert_data.get('is_valid', True))
            self.auto_check.setChecked(self.cert_data.get('auto_check', True))
            
            # Загрузка ИНН
            inn_list = self.cert_data.get('inn', [])
            if isinstance(inn_list, list):
                for inn in inn_list:
                    self.inn_list.addItem(str(inn))
                    
    def get_cert_data(self):
        """Получение данных из формы"""
        inn_list = [self.inn_list.item(i).text() for i in range(self.inn_list.count())]
        
        return {
            'thumbprint': self.thumbprint_edit.text().strip(),
            'subject': self.subject_edit.text().strip(),
            'issuer': self.issuer_edit.text().strip(),
            'valid_from': self.valid_from.date().toString(Qt.DateFormat.ISODate),
            'valid_to': self.valid_to.date().toString(Qt.DateFormat.ISODate),
            'inn': inn_list,
            'is_valid': self.is_valid.isChecked(),
            'auto_check': self.auto_check.isChecked(),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def accept(self):
        """Валидация перед сохранением"""
        if not self.thumbprint_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Поле отпечаток обязательно для заполнения")
            return
            
        if self.inn_list.count() == 0:
            QMessageBox.warning(self, "Ошибка", "Необходимо добавить хотя бы один ИНН")
            return
            
        super().accept()


class InstallCertificateDialog(QDialog):
    """Диалог для установки сертификата из файла"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Установка сертификата из файла")
        self.setModal(True)
        self.resize(500, 300)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Инструкции
        instructions = QLabel(
            "Выберите файл сертификата для установки.\n"
            "Поддерживаются форматы: .cer, .crt, .der, .p7b, .p12, .pfx"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Выбор файла
        file_group = QGroupBox("Выбор файла")
        file_layout = QVBoxLayout()
        
        file_controls = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.file_path.setPlaceholderText("Путь к файлу сертификата")
        
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_file)
        
        file_controls.addWidget(self.file_path)
        file_controls.addWidget(browse_btn)
        file_layout.addLayout(file_controls)
        
        # Опции установки
        self.import_to_store = QCheckBox("Импортировать в хранилище Windows")
        self.import_to_store.setChecked(True)
        file_layout.addWidget(self.import_to_store)
        
        self.add_to_app = QCheckBox("Добавить в список сертификатов приложения")
        self.add_to_app.setChecked(True)
        file_layout.addWidget(self.add_to_app)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Информация о сертификате
        self.cert_info = QTextEdit()
        self.cert_info.setReadOnly(True)
        self.cert_info.setMaximumHeight(100)
        self.cert_info.setPlaceholderText("Информация о сертификате появится после выбора файла")
        layout.addWidget(self.cert_info)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def browse_file(self):
        """Выбор файла сертификата"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл сертификата",
            "",
            "Файлы сертификатов (*.cer *.crt *.der *.p7b *.p12 *.pfx);;Все файлы (*)"
        )
        
        if file_path:
            self.file_path.setText(file_path)
            self.analyze_certificate(file_path)
            
    def analyze_certificate(self, file_path):
        """Анализ выбранного сертификата"""
        try:
            # Здесь должна быть логика анализа сертификата
            # Пока просто показываем базовую информацию
            file_info = Path(file_path)
            info_text = f"Файл: {file_info.name}\n"
            info_text += f"Размер: {file_info.stat().st_size} байт\n"
            info_text += f"Расширение: {file_info.suffix}\n"
            
            self.cert_info.setPlainText(info_text)
            
        except Exception as e:
            self.cert_info.setPlainText(f"Ошибка анализа файла: {e}")
            
    def get_install_data(self):
        """Получение данных для установки"""
        return {
            'file_path': self.file_path.text(),
            'import_to_store': self.import_to_store.isChecked(),
            'add_to_app': self.add_to_app.isChecked()
        }
        
    def accept(self):
        """Валидация перед установкой"""
        if not self.file_path.text():
            QMessageBox.warning(self, "Ошибка", "Выберите файл сертификата")
            return
            
        if not Path(self.file_path.text()).exists():
            QMessageBox.warning(self, "Ошибка", "Выбранный файл не существует")
            return
            
        super().accept()
