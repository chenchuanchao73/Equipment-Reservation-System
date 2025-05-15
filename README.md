# 学校IT设备预定系统 (School IT Equipment Reservation System)

## 项目概述 (Project Overview)

这是一个为学校IT部门设计的物品预定系统，用于管理和预订各种IT设备。系统采用前后端分离架构，前端使用Vue+Element UI，后端使用Python FastAPI，支持中英文双语界面，无需用户登录即可预定设备。系统同时支持PC端和移动端访问，提供流畅的跨平台体验。

This is an equipment reservation system designed for school IT departments, used to manage and reserve various IT equipment. The system adopts a front-end and back-end separation architecture, with Vue+Element UI for the front-end and Python FastAPI for the back-end, supporting both Chinese and English interfaces, allowing users to reserve equipment without logging in. The system supports both PC and mobile access, providing a smooth cross-platform experience.

## 系统特点 (System Features)

- **无需登录 (No Login Required)**: 简化用户使用流程，只需填写基本信息即可预定
- **双语支持 (Bilingual Support)**: 完整支持中英文切换，适合国际学校使用
- **前后端分离 (Front-end and Back-end Separation)**: 使用Vue+Element实现SPA应用，提供流畅用户体验
- **移动端适配 (Mobile Adaptation)**: 响应式设计，支持手机、平板等各种设备访问
- **设备管理 (Equipment Management)**: 全面管理IT设备信息，包括状态跟踪
- **预定管理 (Reservation Management)**: 直观的日历视图显示设备可用性及预定情况
- **公开查询 (Public Query)**: 无需验证即可查看设备预约情况，方便用户规划
- **简单管理界面 (Simple Admin Interface)**: 提供密码保护的管理界面
- **预定确认码 (Reservation Confirmation Code)**: 使用唯一代码方便查询/修改/取消预定
- **循环预约功能 (Recurring Reservation)**: 支持创建循环预约，如每周固定时间段的预约
- **日历视图 (Calendar View)**: 提供直观的日历视图，显示所有已确认和使用中的预约
- **设备筛选日历 (Equipment Filtered Calendar)**: 支持按设备筛选日历视图，直观查看特定设备的预定情况
- **邮件通知系统 (Email Notification System)**: 支持预约创建、修改、取消等场景的邮件通知

## 技术栈 (Technology Stack)

### 前端 (Frontend)

- **框架**: Vue.js 2.x
- **UI组件库**: Element UI
- **状态管理**: Vuex
- **路由**: Vue Router
- **HTTP客户端**: Axios
- **国际化**: vue-i18n
- **移动端适配**:
  - 响应式设计
  - 媒体查询

### 后端 (Backend)

- **框架**: Python 3.8+ 与 FastAPI
- **数据库**: SQLite
- **ORM**: SQLAlchemy
- **API文档**: Swagger UI (FastAPI内置)
- **国际化**: python-i18n
- **邮件支持**: aiosmtplib
- **日志系统**: concurrent-log-handler

## 系统架构 (System Architecture)

### 项目文件结构 (Project Structure)

```
Equipment-Reservation-System/
├── README.md                      # 使用文档（双语）
├── README_Github.md               # GitHub展示文档
├── requirements.txt               # 后端依赖包列表
├── config.py                      # 后端全局配置文件
├── equipment_reservation.db       # SQLite数据库
├── start.py                       # Python启动脚本
├── log_config.py                  # 日志配置文件
│
├── backend/                       # 后端代码
│   ├── __init__.py
│   ├── main.py                    # FastAPI主应用入口
│   ├── database.py                # 数据库连接管理
│   ├── i18n.py                    # 国际化支持
│   ├── utils/                     # 工具函数
│   │   ├── __init__.py
│   │   ├── code_generator.py      # 预订码生成器
│   │   ├── date_utils.py          # 日期处理
│   │   ├── db_utils.py            # 数据库工具
│   │   ├── email_sender.py        # 邮件发送
│   │   └── status_updater.py      # 状态更新工具
│   ├── models/                    # 数据模型
│   │   ├── __init__.py
│   │   ├── equipment.py           # 设备模型
│   │   ├── equipment_category.py  # 设备类别模型
│   │   ├── reservation.py         # 预定模型
│   │   ├── recurring_reservation.py # 循环预约模型
│   │   ├── admin.py               # 管理员模型
│   │   ├── email.py               # 邮件模型
│   │   └── announcement.py        # 公告模型
│   ├── schemas/                   # API模式
│   │   ├── __init__.py
│   │   ├── equipment.py           # 设备模式
│   │   ├── equipment_category.py  # 设备类别模式
│   │   ├── reservation.py         # 预定模式
│   │   ├── recurring_reservation.py # 循环预约模式
│   │   ├── admin.py               # 管理员模式
│   │   └── statistics.py          # 统计数据模式
│   ├── routes/                    # API路由
│   │   ├── __init__.py
│   │   ├── equipment.py           # 设备路由
│   │   ├── equipment_category.py  # 设备类别路由
│   │   ├── reservation.py         # 预定路由
│   │   ├── recurring_reservation.py # 循环预约路由
│   │   ├── admin.py               # 管理员路由
│   │   ├── statistics.py          # 统计数据路由
│   │   ├── upload.py              # 文件上传路由
│   │   ├── calendar.py            # 日历视图路由
│   │   ├── db_admin.py            # 数据库查看路由
│   │   ├── auth.py                # 认证相关路由
│   │   └── announcements.py       # 公告路由
│   ├── templates/                 # 模板文件
│   │   └── emails/                # 邮件模板
│   ├── translations/              # 翻译文件
│   └── static/                    # 静态文件
│       ├── css/                   # CSS样式
│       ├── frontend/              # 前端构建输出
│       ├── images/                # 图片资源
│       ├── qrcodes/               # 二维码
│       └── uploads/               # 上传文件
│           └── equipment/         # 设备图片
│
├── frontend/                      # 前端Vue项目
│   ├── package.json               # 前端依赖包配置
│   ├── vue.config.js              # Vue配置
│   ├── public/                    # 静态资源
│   └── src/                       # 源代码
│       ├── main.js                # Vue应用入口
│       ├── App.vue                # 根组件
│       ├── api/                   # API调用模块
│   │   ├── index.js           # API汇总
│   │   ├── equipment.js       # 设备API
│   │   ├── reservation.js     # 预约API
│   │   └── admin.js           # 管理API
│   ├── assets/                # 静态资源
│   │   ├── locales/           # 国际化文件
│   │   │   ├── en.js              # 英文翻译
│   │   │   └── zh-CN.js           # 中文翻译
│   │   ├── router/                # 路由配置
│   │   │   └── index.js
│   │   ├── store/                 # Vuex状态管理
│   │   ├── utils/                 # 工具函数
│   │   │   ├── request.js         # Axios封装
│   │   └── views/                 # 页面组件
│   │       ├── Home.vue           # 首页
│   │       ├── NotFound.vue       # 404页面
│   │       ├── equipment/         # 设备相关页面
│   │       │   ├── EquipmentList.vue      # 设备列表
│   │       │   └── EquipmentDetail.vue    # 设备详情
│   │       ├── reservation/       # 预约相关页面
│   │       │   ├── ReservationForm.vue    # 预约表单
│   │       │   ├── RecurringReservationForm.vue # 循环预约表单
│   │       │   ├── ReservationDetail.vue  # 预约详情
│   │       │   └── RecurringReservationDetail.vue # 循环预约详情
│   │       ├── calendar/          # 日历相关页面
│   │       │   └── CalendarView.vue        # 日历视图
│   │       └── admin/             # 管理页面
│   │           ├── AdminLayout.vue         # 管理布局
│   │           ├── AdminLogin.vue          # 登录
│   │           ├── AdminDashboard.vue      # 仪表盘
│   │           ├── AdminEquipment.vue      # 设备管理
│   │           ├── AdminCategory.vue       # 类别管理
│   │           ├── AdminReservation.vue    # 预约管理
│   │           ├── AnnouncementManage.vue  # 公告管理
│   │           ├── EmailLayout.vue         # 邮件管理布局
│   │           ├── EmailSettings.vue       # 邮件设置
│   │           ├── EmailTemplates.vue      # 邮件模板
│   │           ├── EmailLogs.vue           # 邮件日志
│   │           ├── AdminSettings.vue       # 系统设置
│   │           └── DatabaseViewer.vue      # 数据库查看
│   ├── logs/                          # 日志目录
│   └── scripts/                       # 脚本目录
```

### 数据库设计 (Database Design)

系统使用SQLite数据库存储数据，包含以下主要表:

#### 设备表 (Equipment Table)

设备表存储系统中所有可预约的IT设备信息。

| 字段名         | 类型     | 说明                             |
| -------------- | -------- | -------------------------------- |
| id             | Integer  | 主键                             |
| name           | String   | 设备名称                         |
| model          | String   | 设备型号                         |
| location       | String   | 设备位置                         |
| status         | String   | 设备状态(available, maintenance) |
| description    | Text     | 设备描述                         |
| image_path     | String   | 设备图片路径                     |
| user_guide     | Text     | 使用指南                         |
| video_tutorial | String   | 视频教程链接                     |
| created_at     | DateTime | 创建时间                         |
| updated_at     | DateTime | 更新时间                         |
| category_id    | Integer  | 设备类别ID(外键)                 |

#### 设备类别表 (Equipment Category Table)

设备类别表用于对设备进行分类管理。

| 字段名      | 类型    | 说明     |
| ----------- | ------- | -------- |
| id          | Integer | 主键     |
| name        | String  | 类别名称 |
| description | Text    | 类别描述 |

#### 预定表 (Reservation Table)

预定表记录用户的设备预约信息。

| 字段名                   | 类型     | 说明                                        |
| ------------------------ | -------- | ------------------------------------------- |
| id                       | Integer  | 主键                                        |
| reservation_number       | String   | 预约序号(唯一)                              |
| equipment_id             | Integer  | 设备ID(外键)                                |
| reservation_code         | String   | 预定码                                      |
| user_name                | String   | 用户姓名                                    |
| user_department          | String   | 用户部门                                    |
| user_contact             | String   | 联系方式                                    |
| user_email               | String   | 用户邮箱                                    |
| start_datetime           | DateTime | 开始时间                                    |
| end_datetime             | DateTime | 结束时间                                    |
| purpose                  | Text     | 使用目的                                    |
| status                   | String   | 状态(confirmed, in_use, expired, cancelled) |
| created_at               | DateTime | 创建时间                                    |
| recurring_reservation_id | Integer  | 循环预约ID(外键)                            |
| is_exception             | Integer  | 是否为循环预约例外(0否,1是)                 |

#### 循环预约表 (Recurring Reservation Table)

循环预约表记录周期性的预约设置。

| 字段名           | 类型     | 说明                                     |
| ---------------- | -------- | ---------------------------------------- |
| id               | Integer  | 主键                                     |
| equipment_id     | Integer  | 设备ID(外键)                             |
| reservation_code | String   | 循环预约码                               |
| pattern_type     | String   | 重复模式(daily, weekly, monthly, custom) |
| days_of_week     | JSON     | 每周几(0-6, 0表示周日)                   |
| days_of_month    | JSON     | 每月几号                                 |
| start_date       | Date     | 循环开始日期                             |
| end_date         | Date     | 循环结束日期                             |
| start_time       | Time     | 每次预约开始时间                         |
| end_time         | Time     | 每次预约结束时间                         |
| user_name        | String   | 用户姓名                                 |
| user_department  | String   | 用户部门                                 |
| user_contact     | String   | 联系方式                                 |
| user_email       | String   | 用户邮箱                                 |
| purpose          | Text     | 使用目的                                 |
| status           | String   | 状态(active, cancelled)                  |
| created_at       | DateTime | 创建时间                                 |

#### 管理员表 (Admin Table)

管理员表存储系统管理员信息。

| 字段名        | 类型     | 说明                    |
| ------------- | -------- | ----------------------- |
| id            | Integer  | 主键                    |
| username      | String   | 用户名(唯一)            |
| password_hash | String   | 密码哈希                |
| name          | String   | 姓名                    |
| role          | String   | 角色(admin, superadmin) |
| is_active     | Boolean  | 是否激活                |
| created_at    | DateTime | 创建时间                |

#### 邮件设置表 (Email Settings Table)

邮件设置表存储邮件发送配置。

| 字段名        | 类型     | 说明       |
| ------------- | -------- | ---------- |
| id            | Integer  | 主键       |
| smtp_server   | String   | SMTP服务器 |
| smtp_port     | Integer  | SMTP端口   |
| sender_email  | String   | 发件人邮箱 |
| sender_name   | String   | 发件人名称 |
| smtp_username | String   | SMTP用户名 |
| smtp_password | String   | SMTP密码   |
| cc_list       | Text     | 抄送人列表 |
| bcc_list      | Text     | 密送人列表 |
| use_ssl       | Boolean  | 使用SSL    |
| enabled       | Boolean  | 是否启用   |
| created_at    | DateTime | 创建时间   |
| updated_at    | DateTime | 更新时间   |

#### 邮件模板表 (Email Template Table)

邮件模板表存储预定各种状态下的邮件模板。

| 字段名       | 类型     | 说明           |
| ------------ | -------- | -------------- |
| id           | Integer  | 主键           |
| name         | String   | 模板名称       |
| template_key | String   | 模板键名(唯一) |
| subject      | String   | 邮件主题       |
| content_html | Text     | HTML内容       |
| content_text | Text     | 纯文本内容     |
| variables    | JSON     | 可用变量       |
| language     | String   | 语言           |
| created_at   | DateTime | 创建时间       |
| updated_at   | DateTime | 更新时间       |

#### 邮件日志表 (Email Log Table)

邮件日志表记录系统发送的所有邮件。

| 字段名             | 类型     | 说明                  |
| ------------------ | -------- | --------------------- |
| id                 | Integer  | 主键                  |
| recipient          | String   | 收件人                |
| subject            | String   | 邮件主题              |
| template_key       | String   | 使用的模板键名        |
| event_type         | String   | 事件类型              |
| status             | String   | 状态(success, failed) |
| error_message      | Text     | 错误信息              |
| reservation_code   | String   | 关联的预定码          |
| reservation_number | String   | 关联的预约序号        |
| created_at         | DateTime | 创建时间              |
| content_html       | Text     | 邮件内容HTML          |

#### 公告表 (Announcement Table)

公告表存储系统公告信息。

| 字段名     | 类型     | 说明     |
| ---------- | -------- | -------- |
| id         | Integer  | 主键     |
| title      | String   | 公告标题 |
| content    | Text     | 公告内容 |
| created_at | DateTime | 创建时间 |
| is_active  | Boolean  | 是否激活 |

## 主要功能 (Main Features)

### 用户端功能

1. **设备浏览与筛选**

   - 浏览所有可用设备
   - 按类别筛选设备
   - 查看设备详情
2. **预约管理**

   - 创建单次预约
   - 创建循环预约
   - 查询预约状态
   - 修改/取消预约
3. **日历视图**

   - 查看全部设备预约情况
   - 按设备筛选预约情况
   - 日/周/月视图切换
4. **公告查看**

   - 查看系统公告

### 管理端功能

1. **设备管理**

   - 添加/编辑/删除设备
   - 管理设备类别
   - 更改设备状态
2. **预约管理**

   - 查看所有预约
   - 筛选预约记录
   - 修改预约状态
   - 取消预约
3. **统计分析**

   - 设备使用率统计
   - 预约数量统计
   - 用户数据分析
4. **系统管理**

   - 邮件设置
   - 邮件模板管理
   - 邮件日志查看
   - 数据库表查看
5. **公告管理**

   - 发布/编辑/删除公告
   - 设置公告激活状态

## 系统启动方式 (System Startup)

### 后端服务启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python start.py
```

### 前端开发服务启动

```bash
# 切换到前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run serve
```

启动完成后，浏览器会自动打开系统首页，或者手动打开http://localhost:8080

## 未完成功能 (Incomplete Features)

以下功能在README中有描述，但尚未完全实现或需要进一步完善：

1. **批量导入/导出功能**：设备和预约记录的批量导入/导出功能尚未完全实现
2. **管理员账户管理**：管理员账户的创建和管理功能尚未完全实现
3. **移动端优化**：虽然基本的响应式设计已实现，但专门针对移动设备的优化功能（如触摸优化等）尚未全面实现

## 最近系统更新 (Recent System Updates)

### 1. 管理控制台菜单优化

- **系统管理标签恢复**: 修复了管理控制台顶部菜单栏缺失"系统管理"标签的问题，该标签包含邮箱设置和数据库查看功能
- **路由配置修复**: 恢复了路由配置中的系统管理功能路由
- **管理界面布局优化**: 更新了管理界面的布局设计，使功能区块更加清晰

### 2. 邮件功能重组

- **邮件管理集成**: 将原有的邮件设置、邮件模板和邮件日志功能整合为一个统一的"邮件管理"二级菜单
- **菜单位置优化**: 将邮件管理功能放置在公告管理和系统管理之间，提高功能的可发现性
- **新增组件**: 创建了独立的EmailSettings.vue、EmailTemplates.vue、EmailLogs.vue和EmailLayout.vue组件
- **界面图标优化**: 更新了邮件管理与公告管理的图标，提高视觉区分度
- **用户界面统一**: 保持了邮件管理各子功能的一致性设计风格

### 3. 日志系统重构

- **按天轮转日志**: 实现了按天自动轮转的日志系统，每天的日志保存为独立文件，格式为app.log.YYYYMMDD
- **Windows兼容性问题修复**: 解决了Windows环境下日志在午夜轮转时出现的文件锁定错误(Windows错误32)
- **并发日志处理**: 从TimedRotatingFileHandler切换到ConcurrentTimedRotatingFileHandler，解决文件锁定冲突
- **自动恢复机制**: 增加了日志文件丢失时的自动恢复功能，保障系统日志完整性
- **定期备份策略**: 实现了日志文件的定期备份功能，降低日志丢失风险
- **错误处理优化**: 改进了异常处理，提供更详细的错误日志记录
- **依赖更新**: 添加了Windows平台特定依赖pywin32，确保日志系统在Windows环境下稳定运行
- **维护任务**: 增加了周期性日志维护任务，负责日志检查、恢复和备份
