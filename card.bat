@echo off
set "SD=%~dp0"
chcp 65001 >nul 2>&1
python "%SD%card.py" %*
