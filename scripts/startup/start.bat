@echo off
echo 正在启动设备预定系统...
echo Starting Equipment Reservation System...

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python未安装，请先安装Python 3.8或更高版本。
    echo Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b
)

:: 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js未安装，请先安装Node.js 12或更高版本。
    echo Node.js is not installed. Please install Node.js 12 or higher.
    pause
    exit /b
)

:: 检查后端虚拟环境
if not exist backend\venv (
    echo 正在创建后端虚拟环境...
    echo Creating backend virtual environment...
    python -m venv backend\venv
)

:: 激活虚拟环境并安装依赖
echo 正在安装后端依赖...
echo Installing backend dependencies...
call backend\venv\Scripts\activate
pip install -r requirements.txt

:: 启动后端服务
echo 正在启动后端服务...
echo Starting backend service...
start cmd /k "call backend\venv\Scripts\activate && cd backend && uvicorn main:app --reload"

:: 安装前端依赖
echo 正在安装前端依赖...
echo Installing frontend dependencies...
cd frontend
if not exist node_modules (
    npm install
)

:: 启动前端服务
echo 正在启动前端服务...
echo Starting frontend service...
start cmd /k "cd frontend && npm run serve"

:: 等待服务启动
echo 正在等待服务启动...
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

:: 打开浏览器
echo 正在打开浏览器...
echo Opening browser...
start http://localhost:8080

echo 设备预定系统已启动！
echo Equipment Reservation System is running!
echo 后端API: http://localhost:8000
echo Backend API: http://localhost:8000
echo 前端界面: http://localhost:8080
echo Frontend UI: http://localhost:8080
echo.
echo 按任意键退出此窗口（服务将继续在后台运行）
echo Press any key to exit this window (services will continue running in the background)
pause >nul
