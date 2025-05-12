# 脚本目录 (Scripts Directory)

本目录包含设备预定系统的各种脚本文件，按功能分类整理。

## 目录结构 (Directory Structure)

### 1. 启动脚本 (Startup Scripts) - `/startup`

包含系统启动相关的脚本文件：

- `start.py` - Python启动脚本
- `start.bat` - Windows批处理启动脚本
- `start.sh` - Linux/Mac启动脚本
- `start_system.bat` - 增强版Windows启动脚本
- `start_system.ps1` - PowerShell启动脚本

### 2. 设置和初始化脚本 (Setup Scripts) - `/setup`

包含系统设置和初始化相关的脚本：

- `setup.py` - 后端初始化脚本
- `create_admin.py` - 创建管理员账户脚本

### 3. 数据库工具脚本 (Database Tool Scripts) - `/database`

包含数据库管理和维护相关的脚本：

- `check_db.py` - 检查数据库脚本
- `check_db_content.py` - 检查数据库内容脚本
- `update_db_schema.py` - 更新数据库架构脚本
- `check_reservation_table.py` - 检查预约表脚本
- `update_equipment_categories.py` - 更新设备类别脚本

### 4. 测试和开发脚本 (Test & Development Scripts) - `/test`

包含测试和开发相关的脚本：

- `create_test_data.py` - 创建测试数据脚本
- `test_reservation_api.py` - 测试预约API脚本
- `test_recurring_reservation_api.py` - 测试循环预约API脚本
- `normalize_datetime_format.py` - 规范化日期时间格式脚本

### 5. 邮件系统脚本 (Email System Scripts) - `/email`

包含邮件系统相关的脚本：

- `sync_email_templates_to_db.py` - 同步邮件模板到数据库脚本
- `clear_email_templates.py` - 清除邮件模板脚本
- `print_email_logs.py` - 打印邮件日志脚本
- `add_content_html_to_emaillog.py` - 添加HTML内容到邮件日志脚本

### 6. 预约管理脚本 (Reservation Management Scripts) - `/reservation`

包含预约管理相关的脚本：

- `check_recent_reservations.py` - 检查最近预约脚本
- `check_reservation_md.py` - 检查预约Markdown文件脚本
- `check_reservation_records.py` - 检查预约记录脚本
- `check_reservation_status_update.py` - 检查预约状态更新脚本
- `create_short_reservation.py` - 创建短时间预约脚本
- `update_reservation_status.py` - 更新预约状态脚本
- `reset_reservation_status.py` - 重置预约状态脚本
- `update_reservation_70_confirmed.py` - 更新70%预约为已确认状态脚本
- `update_reservation_70_in_use.py` - 更新70%预约为使用中状态脚本

## 使用说明 (Usage Instructions)

1. 所有脚本都应从项目根目录运行，例如：
   ```bash
   python scripts/setup/create_admin.py
   ```

2. 启动系统推荐使用根目录下的`Run_Equipment_Reservation.bat`文件（Windows）或直接运行：
   ```bash
   python start.py
   ```

3. 在使用修改数据的脚本前，建议先备份数据库文件。

4. 开发和测试脚本主要用于开发环境，不建议在生产环境中使用。

## 注意事项 (Notes)

1. 启动脚本（start.py, start.bat等）保留在根目录，方便直接启动系统。
2. 工具类脚本已经按功能分类整理到scripts目录下的相应子目录中。
3. 如果您需要使用这些工具脚本，请在scripts目录下的相应子目录中找到它们。
