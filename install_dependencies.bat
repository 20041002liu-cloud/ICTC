@echo off
setlocal

echo [MARS KNOWLEDGE BASE] Checking environment...
echo.

set "BASE_DIR=%~dp0"
set "PYTHON_DIR=%BASE_DIR%python_env"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "PIP_EXE=%PYTHON_DIR%\Scripts\pip.exe"
set "GET_PIP=%BASE_DIR%get-pip.py"
set "PYTHON_ZIP=%BASE_DIR%python.zip"

if exist "%PYTHON_EXE%" (
    echo Found local Python environment.
    goto :INSTALL_DEPS
)

echo Local Python not found. Checking system Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Found system Python.
    set "PYTHON_EXE=python"
    goto :INSTALL_DEPS
)

echo No Python found. Downloading portable Python...
powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip -OutFile '%PYTHON_ZIP%'"

echo Extracting Python...
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
del "%PYTHON_ZIP%"

echo Configuring pip support...
echo import site>> "%PYTHON_DIR%\python311._pth"

echo Downloading pip installer...
powershell -Command "Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile '%GET_PIP%'"

echo Installing pip...
"%PYTHON_EXE%" "%GET_PIP%"
del "%GET_PIP%"

echo Python environment setup complete.

:INSTALL_DEPS
echo.
echo Installing project dependencies...
if "%PYTHON_EXE%"=="python" (
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    "%PYTHON_EXE%" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo.
echo Configuring Streamlit...
if not exist "%BASE_DIR%.streamlit" mkdir "%BASE_DIR%.streamlit"
(
echo [general]
echo email = ""
) > "%BASE_DIR%.streamlit\credentials.toml"

echo.
echo [SUCCESS] All dependencies ready!
pause
