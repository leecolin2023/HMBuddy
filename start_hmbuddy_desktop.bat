@echo off
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [HMBuddy] 未找到 Python，请先安装 Python 3.10+ 并加入 PATH。
  pause
  exit /b 1
)

python -m desktop.app
if errorlevel 1 (
  echo.
  echo [HMBuddy] 启动失败。请先在本目录执行: pip install -e ".[dev]"
  pause
)
