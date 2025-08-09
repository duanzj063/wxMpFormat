@echo off
chcp 65001 >nul
echo 微信文章格式化与海报生成系统
echo ================================

:: 检查uv是否安装
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到uv，请先安装uv
    echo 安装命令: pip install uv
    pause
    exit /b 1
)

:: 检查pyproject.toml是否存在
if not exist "pyproject.toml" (
    echo 错误: 未找到pyproject.toml文件
    pause
    exit /b 1
)

:: 同步依赖
echo 正在同步依赖...
uv sync
if %errorlevel% neq 0 (
    echo 错误: 依赖同步失败
    pause
    exit /b 1
)

echo 依赖同步完成
echo.
echo 正在启动应用...
echo 访问地址: http://127.0.0.1:5000
echo 按 Ctrl+C 停止服务
echo.

:: 启动应用
uv run python app.py

echo.
echo 应用已停止
pause