@echo off
set "SD=%~dp0"
chcp 65001 >nul 2>&1
title Sticky Card Chat
python "%SD%chat.py"
