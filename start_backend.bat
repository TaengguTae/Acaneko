@echo off
echo Starting RAG Knowledge Base Management Backend...
echo.

cd /d "%~dp0"

if not exist "data" (
    echo Creating data directory...
    mkdir data
)

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Starting server...
python backend\main.py

pause
