@echo off
REM
setlocal
set DJANGO_SETTINGS_MODULE=texnote256.settings
call .venv\Scripts\activate.bat
waitress-serve --port=8000 texnote256.wsgi:application
