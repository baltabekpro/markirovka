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

:: 🔧 Виртуальное окружение (создание/активация)
echo 🔧 Проверка виртуального окружения...
setlocal enableextensions
set "ROOT_DIR=%~dp0.."
set "VENV_DIR=%ROOT_DIR%\.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "VENV_ACT=%VENV_DIR%\Scripts\activate.bat"

if exist "%VENV_PY%" (
    echo ✅ Найдено виртуальное окружение: "%VENV_DIR%"
) else (
    echo 📂 Создаём виртуальное окружение в "%VENV_DIR%"...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ❌ Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
)

:: Активация окружения под Windows (cmd)
if exist "%VENV_ACT%" (
    call "%VENV_ACT%"
) else (
    echo ⚠️ Файл активации не найден, продолжу с прямым путём к интерпретатору
)

:: Используем python из окружения, при сбое активации — прямой путь
set "PYTHON=%VENV_PY%"
if not exist "%PYTHON%" set "PYTHON=python"

echo 🔍 Проверка зависимостей...

:: Проверяем PyQt6
%PYTHON% -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo 📦 Устанавливаем PyQt6...
    %PYTHON% -m pip install PyQt6
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
    %PYTHON% -m pip install -r requirements.txt >nul 2>&1
)

:: Устанавливаем зависимости основной системы
if exist "..\scripts\requirements.txt" (
    echo 📦 Устанавливаем зависимости системы...
    %PYTHON% -m pip install -r "..\scripts\requirements.txt" >nul 2>&1
)

echo.
echo 🎨 Запуск графического интерфейса...
echo.

:: Запускаем GUI
%PYTHON% launcher.py

:: Если произошла ошибка
if errorlevel 1 (
    echo.
    echo ❌ Произошла ошибка при запуске GUI
    echo 💡 Попробуйте запустить: %PYTHON% main_window.py
    echo.
    pause
)
