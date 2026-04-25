@echo off
echo 🚀 OpenClaw高级专业Agent配置生成器 - 示例模式
echo ==============================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 创建输出目录
if not exist "example-output" mkdir "example-output"

REM 运行示例模式
python openclaw-config-generator.py ^
  --mode example ^
  --output-dir "example-output" ^
  --validation-level strict

echo.
echo ✅ 示例运行完成！
echo 📁 生成的文件保存在: example-output\
echo.
echo 📋 快速查看生成的文件：
dir example-output\
pause