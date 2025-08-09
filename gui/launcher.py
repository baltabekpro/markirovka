#!/usr/bin/env python3
"""
Launcher для GUI приложения ЦРПТ Маркировка
Основная точка входа для графического интерфейса
"""

import sys
import os
import subprocess
from pathlib import Path

# Определяем пути
GUI_DIR = Path(__file__).parent
ROOT_DIR = GUI_DIR.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("Ошибка: Требуется Python 3.8 или выше")
        print(f"Текущая версия: {sys.version}")
        return False
    return True

def check_dependencies():
    """Проверка и установка зависимостей"""
    try:
        # Проверяем PyQt6
        import PyQt6
        print("✓ PyQt6 установлен")
    except ImportError:
        print("❌ PyQt6 не установлен")
        print("Установка PyQt6...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])
            print("✓ PyQt6 успешно установлен")
        except subprocess.CalledProcessError:
            print("❌ Ошибка установки PyQt6")
            return False
    
    # Проверяем основные зависимости GUI
    gui_requirements = GUI_DIR / "requirements.txt"
    if gui_requirements.exists():
        try:
            print("Проверка зависимостей GUI...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(gui_requirements)
            ])
            print("✓ Зависимости GUI установлены")
        except subprocess.CalledProcessError:
            print("⚠️ Некоторые зависимости GUI могут быть не установлены")
    
    # Проверяем зависимости основной системы
    scripts_requirements = SCRIPTS_DIR / "requirements.txt"
    if scripts_requirements.exists():
        try:
            print("Проверка зависимостей основной системы...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(scripts_requirements)
            ])
            print("✓ Зависимости основной системы установлены")
        except subprocess.CalledProcessError:
            print("⚠️ Некоторые зависимости основной системы могут быть не установлены")
    
    return True

def setup_environment():
    """Настройка окружения"""
    # Добавляем путь к scripts в sys.path
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    
    # Устанавливаем рабочую директорию
    os.chdir(str(SCRIPTS_DIR))

def create_desktop_shortcut():
    """Создание ярлыка на рабочем столе (только для Windows)"""
    if sys.platform == "win32":
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "ЦРПТ Маркировка.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{__file__}"'
            shortcut.WorkingDirectory = str(GUI_DIR)
            shortcut.IconLocation = sys.executable
            shortcut.save()
            
            print(f"✓ Ярлык создан на рабочем столе: {shortcut_path}")
        except ImportError:
            print("⚠️ Для создания ярлыка установите winshell: pip install winshell")
        except Exception as e:
            print(f"⚠️ Не удалось создать ярлык: {e}")

def main():
    """Главная функция launcher'а"""
    print("=" * 60)
    print("🚀 Запуск GUI приложения ЦРПТ Маркировка")
    print("=" * 60)
    
    # Проверяем версию Python
    if not check_python_version():
        input("Нажмите Enter для выхода...")
        return 1
    
    # Настраиваем окружение
    setup_environment()
    
    # Проверяем и устанавливаем зависимости
    if not check_dependencies():
        print("❌ Ошибка установки зависимостей")
        input("Нажмите Enter для выхода...")
        return 1
    
    try:
        # Импортируем и запускаем GUI
        print("🎨 Запуск графического интерфейса...")
        from main_window import main as gui_main
        return gui_main()
        
    except ImportError as e:
        print(f"❌ Ошибка импорта GUI модулей: {e}")
        print("\nВозможные причины:")
        print("1. PyQt6 не установлен корректно")
        print("2. Отсутствуют файлы GUI")
        print("3. Проблемы с зависимостями")
        print("\nПопробуйте переустановить зависимости:")
        print("pip install --force-reinstall PyQt6")
        input("Нажмите Enter для выхода...")
        return 1
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Выполнение прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)
