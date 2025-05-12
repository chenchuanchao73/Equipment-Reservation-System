#!/bin/bash

echo "正在启动设备预定系统..."
echo "Starting Equipment Reservation System..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "Python未安装，请先安装Python 3.8或更高版本。"
    echo "Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "Node.js未安装，请先安装Node.js 12或更高版本。"
    echo "Node.js is not installed. Please install Node.js 12 or higher."
    exit 1
fi

# 检查后端虚拟环境
if [ ! -d "backend/venv" ]; then
    echo "正在创建后端虚拟环境..."
    echo "Creating backend virtual environment..."
    python3 -m venv backend/venv
fi

# 激活虚拟环境并安装依赖
echo "正在安装后端依赖..."
echo "Installing backend dependencies..."
source backend/venv/bin/activate
pip install -r requirements.txt

# 启动后端服务
echo "正在启动后端服务..."
echo "Starting backend service..."
gnome-terminal -- bash -c "source backend/venv/bin/activate && cd backend && uvicorn main:app --reload"

# 安装前端依赖
echo "正在安装前端依赖..."
echo "Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

# 启动前端服务
echo "正在启动前端服务..."
echo "Starting frontend service..."
gnome-terminal -- bash -c "cd frontend && npm run serve"

# 等待服务启动
echo "正在等待服务启动..."
echo "Waiting for services to start..."
sleep 5

# 打开浏览器
echo "正在打开浏览器..."
echo "Opening browser..."
xdg-open http://localhost:8080

echo "设备预定系统已启动！"
echo "Equipment Reservation System is running!"
echo "后端API: http://localhost:8000"
echo "Backend API: http://localhost:8000"
echo "前端界面: http://localhost:8080"
echo "Frontend UI: http://localhost:8080"
echo ""
echo "按Ctrl+C退出此窗口（服务将继续在后台运行）"
echo "Press Ctrl+C to exit this window (services will continue running in the background)"
read -n 1 -s
