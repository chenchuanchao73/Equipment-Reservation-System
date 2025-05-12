@echo off
echo === 启动设备预定系统前端 ===

cd frontend
echo 正在安装依赖...
call npm install

echo 正在启动前端应用程序...
call npm run serve
