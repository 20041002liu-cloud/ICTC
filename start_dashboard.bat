@echo off
setlocal

echo [MARS KNOWLEDGE BASE] Starting Dashboard...
echo.

set "BASE_DIR=%~dp0"
set "PYTHON_DIR=%BASE_DIR%python_env"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"

if exist "%PYTHON_EXE%" (
    echo Using local Python environment.
) else (
    echo Local Python not found. Using system Python.
    set "PYTHON_EXE=python"
)

echo Launching Streamlit...
"%PYTHON_EXE%" -m streamlit run app.py --server.headless=false --server.address=localhost

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start dashboard.
    echo Please run 'install_dependencies.bat' first.
    pause
)
