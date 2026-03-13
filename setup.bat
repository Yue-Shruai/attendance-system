@echo off
echo ========================================
echo 考勤系统 - 一键初始化
echo ========================================

cd /d "%~dp0"

echo.
echo [1/3] 安装依赖...
python -m pip install streamlit lark-oapi python-dotenv

echo.
echo [2/3] 运行 bitable_setup.py 创建云端数据表...
set FEISHU_APP_ID=cli_a92fcafc2778dcd3
set FEISHU_APP_SECRET=sJWH8aRwIUZmCKbIhgBtXcqh3O4RQz7U
python bitable_setup.py

echo.
echo [3/3] 启动考勤系统...
echo.
echo 请把上一步显示的 BITABLE_APP_TOKEN、BITABLE_TABLE_ID、ATTENDANCE_TABLE_ID
echo 填入 .env 文件，然后运行: streamlit run app.py
echo.
pause
