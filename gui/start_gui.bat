@echo off
chcp 65001 >nul
title ЦРПТ Маркировка - Графический интерфейс

echo ================================================
echo 🚀 Запуск GUI для системы ЦРПТ Маркировка
echo ================================================
echo.

:: Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден в системе
    echo 📥 Установите Python с официального сайта: https://python.org
    pause
    exit /b 1
)

:: Переходим в директорию GUI
cd /d "%~dp0"

echo 🔍 Проверка зависимостей...

:: Проверяем PyQt6
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo 📦 Устанавливаем PyQt6...
    python -m pip install PyQt6
    if errorlevel 1 (
        echo ❌ Ошибка установки PyQt6
        pause
        exit /b 1
    )
    echo ✅ PyQt6 установлен
)

:: Устанавливаем остальные зависимости GUI
if exist requirements.txt (
    echo 📦 Устанавливаем зависимости GUI...
    python -m pip install -r requirements.txt >nul 2>&1
)

:: Устанавливаем зависимости основной системы
if exist "..\scripts\requirements.txt" (
    echo 📦 Устанавливаем зависимости системы...
    python -m pip install -r "..\scripts\requirements.txt" >nul 2>&1
)

echo.
echo 🎨 Запуск графического интерфейса...
echo.

:: Запускаем GUI
python launcher.py

:: Если произошла ошибка
if errorlevel 1 (
    echo.
    echo ❌ Произошла ошибка при запуске GUI
    echo 💡 Попробуйте запустить: python main_window.py
    echo.
    pause
)
