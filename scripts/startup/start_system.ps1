# 设备预约系统启动脚本

Write-Host "正在启动设备预约系统..." -ForegroundColor Green

# 终止可能正在运行的后端服务
$backendProcesses = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($backendProcesses) {
    Write-Host "终止后端服务进程..." -ForegroundColor Yellow
    foreach ($process in $backendProcesses) {
        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
    }
}

# 终止可能正在运行的前端服务
$frontendProcesses = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($frontendProcesses) {
    Write-Host "终止前端服务进程..." -ForegroundColor Yellow
    foreach ($process in $frontendProcesses) {
        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
    }
}

# 启动后端服务
Write-Host "启动后端服务..." -ForegroundColor Cyan
Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# 等待几秒钟，确保后端服务已经启动
Write-Host "等待后端服务启动..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# 启动前端服务
Write-Host "启动前端服务..." -ForegroundColor Cyan
Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd frontend && npm run serve"

# 获取本机IP地址
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Ethernet*,Wi-Fi* | Where-Object { $_.IPAddress -notmatch "^169" } | Select-Object -First 1).IPAddress
if (-not $ipAddress) {
    $ipAddress = "[服务器IP]"
}

Write-Host "`n系统启动完成！" -ForegroundColor Green
Write-Host "前端地址: http://localhost:8080" -ForegroundColor Green
Write-Host "后端API: http://localhost:8000" -ForegroundColor Green
Write-Host "`n局域网访问:" -ForegroundColor Green
Write-Host "前端地址: http://$ipAddress`:8080" -ForegroundColor Green
Write-Host "后端API: http://$ipAddress`:8000" -ForegroundColor Green

Write-Host "`n按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
