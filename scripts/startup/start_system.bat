@echo off
echo 正在启动设备预约系统...

REM 终止可能正在运行的后端服务
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') DO (
    echo 终止后端服务进程: %%P
    taskkill /F /PID %%P 2>nul
)

REM 终止可能正在运行的前端服务
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') DO (
    echo 终止前端服务进程: %%P
    taskkill /F /PID %%P 2>nul
)

REM 启动后端服务
echo 启动后端服务...
start cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM 等待几秒钟，确保后端服务已经启动
echo 等待后端服务启动...
timeout /t 5

REM 启动前端服务
echo 启动前端服务...
start cmd /k "cd frontend && npm run serve"

echo 系统启动完成！
echo 前端地址: http://localhost:8080
echo 后端API: http://localhost:8000
echo.
echo 局域网访问:
echo 前端地址: http://[服务器IP]:8080
echo 后端API: http://[服务器IP]:8000
echo.
echo 按任意键退出...
pause > nul
