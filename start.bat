@echo off
set "SD=%~dp0"
chcp 65001 >nul 2>&1
start "" pythonw "%SD%sticky-card.pyw"
python "%SD%chat.py"
