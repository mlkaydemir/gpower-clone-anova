@echo off
python -m src.cli %*
exit /b %ERRORLEVEL%
