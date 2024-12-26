@echo off
:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)

:: Install requirements
echo Installing Python packages from requirements.txt...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Failed to install packages. Please check your requirements.txt or pip configuration.
    pause
    exit /b
)

echo All packages installed successfully!
pause
