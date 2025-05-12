# 学校IT设备预定系统 (School IT Equipment Reservation System)

## 项目概述 (Project Overview)

这是一个为学校IT部门设计的物品预定系统，用于管理和预订各种IT设备。系统采用前后端分离架构，前端使用Vue+Element UI，后端使用Python FastAPI，支持中英文双语界面，无需用户登录即可预定设备。系统同时支持PC端和移动端访问，提供流畅的跨平台体验。

This is an equipment reservation system designed for school IT departments, used to manage and reserve various IT equipment. The system adopts a front-end and back-end separation architecture, with Vue+Element UI for the front-end and Python FastAPI for the back-end, supporting both Chinese and English interfaces, allowing users to reserve equipment without logging in. The system supports both PC and mobile access, providing a smooth cross-platform experience.

## 系统特点 (System Features)

- **无需登录 (No Login Required)**: 简化用户使用流程，只需填写基本信息即可预定
- **双语支持 (Bilingual Support)**: 完整支持中英文切换，适合国际学校使用
- **前后端分离 (Front-end and Back-end Separation)**: 使用Vue+Element实现SPA应用，提供流畅用户体验
- **移动端适配 (Mobile Adaptation)**: 完全响应式设计，支持手机、平板等各种设备访问
- **设备管理 (Equipment Management)**: 全面管理IT设备信息，包括状态跟踪
- **预定管理 (Reservation Management)**: 直观的日历视图显示设备可用性及预定情况
- **公开查询 (Public Query)**: 无需验证即可查看设备预约情况，方便用户规划
- **简单管理界面 (Simple Admin Interface)**: 提供简单密码保护的管理界面
- **预定确认码 (Reservation Confirmation Code)**: 使用唯一代码方便查询/修改/取消预定
- **Unsplash API集成**: 使用Unsplash API获取高质量设备图片
- **循环预约功能 (Recurring Reservation)**: 支持创建循环预约，如每周固定时间段的预约
- **日历视图 (Calendar View)**: 提供直观的日历视图，显示所有已确认和使用中的预约

## 技术栈 (Technology Stack)

### 前端 (Frontend)
- **框架**: Vue.js 2.x
- **UI组件库**: Element UI (非Element Plus)
- **状态管理**: Vuex
- **路由**: Vue Router
- **HTTP客户端**: Axios
- **图片资源**: Unsplash API
- **图标**: Element UI自带图标
- **国际化**: vue-i18n
- **移动端适配**:
  - 响应式设计
  - vw/vh单位
  - 媒体查询
  - 触摸事件优化

### 后端 (Backend)
- **框架**: Python 3.8+ 与 FastAPI
- **数据库**: SQLite
- **ORM**: SQLAlchemy
- **API文档**: Swagger UI (FastAPI内置)
- **国际化**: python-i18n

## 系统架构 (System Architecture)

### 项目文件结构 (Project Structure)

```
equipment-reservation-system/
├── README.md                      # 使用文档（双语）
├── requirements.txt               # 后端依赖包列表
├── config.py                      # 后端全局配置文件
├── equipment_reservation.db       # SQLite数据库
│
├── 启动脚本 (Startup Scripts)
│   ├── start.py                   # Python启动脚本
│   ├── start.bat                  # Windows批处理启动脚本
│   ├── start.sh                   # Linux/Mac启动脚本
│   ├── start_system.bat           # 增强版Windows启动脚本
│   ├── start_system.ps1           # PowerShell启动脚本
│   └── Run_Equipment_Reservation.bat # Windows快捷启动批处理
│
├── 设置和初始化脚本 (Setup Scripts)
│   ├── setup.py                   # 后端初始化脚本
│   └── create_admin.py            # 创建管理员账户脚本
│
├── 数据库工具脚本 (Database Tool Scripts)
│   ├── check_db.py                # 检查数据库脚本
│   ├── check_db_content.py        # 检查数据库内容脚本
│   ├── update_db_schema.py        # 更新数据库架构脚本
│   ├── check_reservation_table.py # 检查预约表脚本
│   └── update_equipment_categories.py # 更新设备类别脚本
│
├── 测试和开发脚本 (Test & Development Scripts)
│   ├── create_test_data.py        # 创建测试数据脚本
│   ├── create_short_reservation.py # 创建短时间预约脚本
│   ├── test_reservation_api.py    # 测试预约API脚本
│   ├── test_recurring_reservation_api.py # 测试循环预约API脚本
│   └── normalize_datetime_format.py # 规范化日期时间格式脚本
│
├── 邮件系统脚本 (Email System Scripts)
│   ├── sync_email_templates_to_db.py # 同步邮件模板到数据库脚本
│   ├── clear_email_templates.py   # 清除邮件模板脚本
│   ├── print_email_logs.py        # 打印邮件日志脚本
│   └── add_content_html_to_emaillog.py # 添加HTML内容到邮件日志脚本
│
├── backend/                       # 后端代码
│   ├── __init__.py
│   ├── main.py                    # FastAPI主应用入口
│   ├── database.py                # 数据库连接管理
│   ├── utils/                     # 工具函数
│   │   ├── __init__.py
│   │   ├── code_generator.py      # 预订码生成器
│   │   ├── date_utils.py          # 日期处理
│   │   ├── email_sender.py        # 邮件发送
│   │   ├── excel_handler.py       # Excel处理工具
│   │   └── status_updater.py      # 状态更新工具
│   ├── models/                    # 数据模型
│   │   ├── __init__.py
│   │   ├── equipment.py           # 设备模型
│   │   ├── equipment_category.py  # 设备类别模型
│   │   ├── reservation.py         # 预定模型
│   │   ├── recurring_reservation.py # 循环预约模型
│   │   ├── admin.py               # 管理员模型
│   │   └── email.py               # 邮件模型
│   ├── schemas/                   # API模式
│   │   ├── __init__.py
│   │   ├── equipment.py           # 设备模式
│   │   ├── equipment_category.py  # 设备类别模式
│   │   ├── reservation.py         # 预定模式
│   │   ├── recurring_reservation.py # 循环预约模式
│   │   ├── admin.py               # 管理员模式
│   │   ├── email.py               # 邮件模式
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
│   │   ├── db_admin.py            # 数据库管理路由
│   │   ├── auth.py                # 认证相关路由
│   │   └── crud/                  # CRUD操作路由
│   │       ├── equipment.py       # 设备CRUD
│   │       ├── reservation.py     # 预约CRUD
│   │       └── admin.py           # 管理员CRUD
│   ├── i18n/                      # 国际化
│   │   ├── __init__.py
│   │   ├── zh_CN/                 # 中文翻译
│   │   └── en/                    # 英文翻译
│   ├── templates/                 # 模板文件
│   │   ├── index.html             # 首页模板
│   │   ├── email/                 # 邮件模板
│   │   └── admin/                 # 管理页面模板
│   ├── static/                    # 静态文件
│   │   ├── css/                   # CSS样式
│   │   ├── js/                    # JavaScript文件
│   │   ├── images/                # 图片资源
│   │   └── frontend/              # 前端构建输出
│   └── tests/                     # 测试代码
│       ├── __init__.py
│       ├── test_equipment.py
│       └── test_reservation.py
├── frontend/                      # 前端Vue项目
│   ├── .gitignore
│   ├── babel.config.js
│   ├── package.json
│   ├── vue.config.js
│   ├── .env.development           # 开发环境配置
│   ├── .env.production            # 生产环境配置
│   ├── public/
│   │   ├── favicon.ico
│   │   └── index.html
│   └── src/
│       ├── main.js                # Vue应用入口
│       ├── App.vue                # 根组件
│       ├── api/                   # API调用模块
│       │   ├── index.js
│       │   ├── equipment.js
│       │   ├── reservation.js
│       │   ├── recurring.js       # 循环预约API
│       │   ├── calendar.js        # 日历API
│       │   └── admin.js
│       ├── assets/                # 静态资源
│       │   ├── logo.png
│       │   ├── css/
│       │   └── images/
│       ├── components/            # 公共组件
│       │   ├── LanguageSwitcher.vue
│       │   ├── EquipmentCard.vue
│       │   ├── ReservationForm.vue
│       │   ├── RecurringForm.vue  # 循环预约表单
│       │   ├── CalendarView.vue   # 日历视图组件
│       │   └── ...
│       ├── locales/               # 国际化文件
│       │   ├── en.js
│       │   └── zh.js
│       ├── router/                # 路由配置
│       │   └── index.js
│       ├── store/                 # Vuex状态管理
│       │   ├── index.js
│       │   ├── modules/
│       │   │   ├── equipment.js
│       │   │   ├── reservation.js
│       │   │   ├── recurring.js   # 循环预约状态
│       │   │   ├── calendar.js    # 日历状态
│       │   │   └── admin.js
│       ├── utils/                 # 工具函数
│       │   ├── request.js         # Axios封装
│       │   ├── unsplash.js        # Unsplash API封装
│       │   ├── date.js            # 日期处理
│       └── views/                 # 页面组件
│           ├── Home.vue
│           ├── EquipmentList.vue
│           ├── EquipmentDetail.vue
│           ├── ReservationNew.vue
│           ├── ReservationConfirm.vue
│           ├── ReservationQuery.vue
│           ├── RecurringReservation.vue # 循环预约页面
│           ├── CalendarView.vue    # 日历视图页面
│           └── admin/
│               ├── Login.vue
│               ├── Dashboard.vue
│               ├── EquipmentManage.vue
│               ├── ReservationManage.vue
│               ├── RecurringManage.vue # 循环预约管理
│               ├── EmailTemplates.vue  # 邮件模板管理
│               └── Statistics.vue      # 统计数据页面
├── logs/                          # 日志目录
│   └── app.log                     # 当前日志文件，按天轮转，历史日志格式为app.log.YYYY-MM-DD
└── temp/                          # 临时文件目录
```

### 数据库设计 (Database Design)

#### 设备表 (Equipment Table)
```sql
CREATE TABLE equipment (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,                -- 设备名称 / Equipment name
    category TEXT NOT NULL,            -- 类别 / Category
    model TEXT,                        -- 型号 / Model
    location TEXT,                     -- 位置 / Location
    status TEXT DEFAULT 'available',   -- 状态 / Status (available, maintenance)
    description TEXT,                  -- 描述 / Description
    image_path TEXT,                   -- 图片路径 / Image path
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 预定表 (Reservation Table)
```sql
CREATE TABLE reservation (
    id INTEGER PRIMARY KEY,
    equipment_id INTEGER NOT NULL,     -- 设备ID / Equipment ID
    reservation_code TEXT NOT NULL,    -- 预定码 / Reservation code
    user_name TEXT NOT NULL,           -- 用户姓名 / User name
    user_department TEXT NOT NULL,     -- 用户部门 / User department
    user_contact TEXT NOT NULL,        -- 联系方式 / Contact information
    start_datetime TIMESTAMP NOT NULL, -- 开始时间 / Start time
    end_datetime TIMESTAMP NOT NULL,   -- 结束时间 / End time
    purpose TEXT,                      -- 使用目的 / Purpose
    status TEXT DEFAULT 'confirmed',   -- 状态 / Status (confirmed, cancelled)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment (id)
);
```

#### 管理员表 (Admin Table)
```sql
CREATE TABLE admin (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,     -- 用户名 / Username
    password_hash TEXT NOT NULL,       -- 密码哈希 / Password hash
    is_active BOOLEAN DEFAULT 1,       -- 是否激活 / Is active
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API接口设计 (API Interface Design)

### 设备相关API (Equipment APIs)

#### 获取所有设备 (Get All Equipment)
- **URL**: `/api/equipment`
- **Method**: `GET`
- **Params**:
  - `category` (optional): 设备类别过滤
  - `status` (optional): 设备状态过滤
- **Response**: 设备列表数组

#### 获取设备详情 (Get Equipment Details)
- **URL**: `/api/equipment/{id}`
- **Method**: `GET`
- **Response**: 设备详细信息

#### 获取设备可用性 (Get Equipment Availability)
- **URL**: `/api/equipment/{id}/availability`
- **Method**: `GET`
- **Params**:
  - `start_date`: 开始日期
  - `end_date`: 结束日期
- **Response**: 日历格式的可用性数据

### 预定相关API (Reservation APIs)

#### 创建预定 (Create Reservation)
- **URL**: `/api/reservations`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "equipment_id": 1,
    "user_name": "张三",
    "user_department": "教学部",
    "user_contact": "zhangsan@example.com",
    "start_datetime": "2023-09-15T09:00:00",
    "end_datetime": "2023-09-15T12:00:00",
    "purpose": "课堂教学"
  }
  ```
- **Response**: 预定确认信息，包含预定码

#### 查询预定 (Query Reservation)
- **URL**: `/api/reservations/{code}`
- **Method**: `GET`
- **Response**: 预定详细信息

#### 查询公开预定列表 (Query Public Reservations)
- **URL**: `/api/reservations`
- **Method**: `GET`
- **Params**:
  - `equipment_id` (optional): 设备ID过滤
  - `category` (optional): 设备类别过滤
  - `from_date` (optional): 开始日期
  - `to_date` (optional): 结束日期
- **Response**: 预定列表数组

#### 修改预定 (Update Reservation)
- **URL**: `/api/reservations/{code}`
- **Method**: `PUT`
- **Body**: 更新的预定信息
- **Response**: 更新后的预定信息

#### 取消预定 (Cancel Reservation)
- **URL**: `/api/reservations/{code}`
- **Method**: `DELETE`
- **Response**: 取消确认

### 管理员API (Admin APIs)

#### 管理员登录 (Admin Login)
- **URL**: `/api/admin/login`
- **Method**: `POST`
- **Body**: 用户名和密码
- **Response**: 认证Token

#### 管理设备 (Manage Equipment)
- **URL**: `/api/admin/equipment`
- **Methods**: `GET`, `POST`, `PUT`, `DELETE`
- **Header**: Authorization Token
- **Response**: 根据操作返回相应数据

#### 管理预定 (Manage Reservations)
- **URL**: `/api/admin/reservations`
- **Methods**: `GET`, `POST`, `PUT`, `DELETE`
- **Header**: Authorization Token
- **Response**: 根据操作返回相应数据

## 前端页面及功能 (Frontend Pages and Features)

### 公共页面 (Public Pages)

#### 首页 (Home)
- 系统介绍
- 语言切换
- 设备类别导航
- 热门设备展示
- 预定查询入口

#### 设备列表页 (Equipment List)
- 设备类别筛选
- 设备卡片展示
- 可用状态标识
- 设备搜索

#### 设备详情页 (Equipment Detail)
- 设备详细信息和图片(Unsplash API)
- 设备可用性日历(Element UI日历组件)
- 预定按钮

#### 预定表单页 (Reservation Form)
- 设备信息概要
- 日期时间选择器(Element UI)
- 用户信息表单

#### 预定确认页 (Reservation Confirmation)
- 预定详情
- 预定码显示
- 打印/分享选项

#### 预定查询页 (Reservation Query)
- 公开查询功能：无需验证，直接查看设备预约情况
  - 按设备类别筛选
  - 按日期范围筛选
  - 表格形式展示预约情况，包含设备名称、预约人姓名、时间段和状态
- 个人预约管理：通过预定码或联系方式验证（二选一）
  - 预定码查询：直接进入对应预定详情
  - 联系方式查询：显示该联系方式的所有预定
  - 预定详情显示
  - 预定管理选项(修改/取消)

### 管理页面 (Admin Pages)

#### 登录页面 (Login)
- 管理员登录表单

#### 管理控制台 (Dashboard)
- 数据统计概览
- 快速导航菜单

#### 设备管理 (Equipment Management)
- 设备列表(Element UI表格组件)
- 添加/编辑/删除设备
- 批量操作

#### 预定管理 (Reservation Management)
- 预定列表
- 预定详情查看
- 预定状态修改
- 导出功能

## 移动端适配策略 (Mobile Adaptation Strategy)

系统将采用"移动优先"的设计理念，确保在各种设备上都能提供良好的用户体验：

### 1. 响应式布局 (Responsive Layout)
- 使用Element UI的栅格系统实现响应式布局
- 针对不同屏幕尺寸优化组件展示
- 自适应容器和弹性布局

### 2. 移动端特定UI优化 (Mobile-specific UI Optimization)
- 触摸友好的大按钮和输入控件
- 简化移动端的表单和交互流程
- 优化元素间距和字体大小

### 3. 触摸交互优化 (Touch Interaction Optimization)
- 支持滑动、点击等触摸手势
- 优化点击区域，提高触摸准确性
- 减少悬停依赖的交互

### 4. 性能优化 (Performance Optimization)
- 图片懒加载和尺寸优化
- 减少移动端网络请求
- 组件按需加载

### 5. 移动端测试 (Mobile Testing)
- 跨浏览器和设备测试
- 真机测试确保体验一致性
- 网络条件模拟测试

## 移动端UI调整 (Mobile UI Adjustments)

### 桌面端与移动端对比 (Desktop vs Mobile)

| 功能 | 桌面端 | 移动端 |
|------|--------|--------|
| 导航 | 水平顶部菜单 | 汉堡菜单或底部导航栏 |
| 设备列表 | 网格布局(3-4列) | 单列卡片列表 |
| 日历视图 | 月视图默认 | 日/周视图默认 |
| 表单 | 多列布局 | 单列堆叠布局 |
| 管理界面 | 完整功能 | 精简关键功能 |

### 移动端特定组件 (Mobile-specific Components)

- **MobileNav.vue**: 移动端导航组件
- **MobileEquipmentCard.vue**: 优化的移动端设备卡片
- **MobileCalendar.vue**: 触摸友好的预定日历
- **BottomActionBar.vue**: 移动端底部操作栏

## 实现计划 (Implementation Plan)

### 第一阶段: 后端API开发 (Phase 1: Backend API Development)
1. 设置FastAPI项目结构
2. 创建数据库模型和迁移
3. 实现核心API端点
4. API文档和测试

### 第二阶段: 前端框架搭建 (Phase 2: Frontend Framework Setup)
1. 创建Vue项目
2. 配置Element UI和必要依赖
3. 设置国际化(i18n)
4. 实现路由和状态管理

### 第三阶段: 核心功能实现 (Phase 3: Core Features Implementation)
1. 实现设备浏览和详情查看
2. 实现预定创建流程
3. 实现预定查询功能
4. 集成Unsplash API

### 第四阶段: 管理功能实现 (Phase 4: Admin Features Implementation)

## Vue组件详细设计 (Vue Component Design Details)

### 基础组件 (Base Components)
- **LanguageSwitcher.vue**: 语言切换组件
- **PageHeader.vue**: 页面标题组件
- **EquipmentCard.vue**: 设备卡片组件
- **UnsplashImage.vue**: Unsplash图片组件
- **ReservationForm.vue**: 预定表单组件
- **ResponsiveContainer.vue**: 响应式容器组件

### 页面组件 (Page Components)
- **Home.vue**: 首页
- **EquipmentList.vue**: 设备列表页
- **EquipmentDetail.vue**: 设备详情页
- **ReservationNew.vue**: 新建预定页
- **ReservationConfirm.vue**: 预定确认页
- **ReservationQuery.vue**: 预定查询页

### 移动端组件 (Mobile Components)
- **MobileNav.vue**: 移动端导航
- **MobileCalendar.vue**: 移动端优化日历
- **BottomActionBar.vue**: 底部操作栏
- **SwipeContainer.vue**: 滑动容器

### 管理组件 (Admin Components)
- **AdminLogin.vue**: 管理员登录页
- **AdminDashboard.vue**: 管理控制台
- **EquipmentTable.vue**: 设备管理表格
- **ReservationTable.vue**: 预定管理表格

## 技术实现要点 (Technical Implementation Points)

### 响应式设计实现 (Responsive Design Implementation)

1. **使用Element UI栅格系统**
```html
<el-row :gutter="20">
  <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4">
    <!-- 组件内容会根据屏幕尺寸自动调整布局 -->
  </el-col>
</el-row>
```

2. **CSS媒体查询**
```css
/* 基础样式适用于所有设备 */
.card {
  padding: 15px;
}

/* 针对移动设备的优化 */
@media (max-width: 768px) {
  .card {
    padding: 10px;
    margin-bottom: 10px;
  }
}
```

3. **条件渲染**
```html
<desktop-component v-if="!isMobile"></desktop-component>
<mobile-component v-else></mobile-component>
```

### Unsplash API实现 (Unsplash API Implementation)

```javascript
// unsplash.js
import axios from 'axios';

const unsplashAPI = axios.create({
  baseURL: 'https://api.unsplash.com',
  headers: {
    Authorization: `Client-ID ${process.env.VUE_APP_UNSPLASH_ACCESS_KEY}`
  }
});

export function getEquipmentImage(category, query) {
  return unsplashAPI.get('/photos/random', {
    params: {
      query: `${category} ${query}`,
      orientation: 'landscape'
    }
  });
}
```

## 项目启动指南 (Project Startup Guide)

系统提供了多种启动脚本，可以根据不同环境和需求选择使用：

### 快速启动 (Quick Start)

#### Windows系统 (Windows System)

双击根目录下的`Run_Equipment_Reservation.bat`文件即可快速启动系统。这是最简单的启动方式，适合日常使用。

#### Linux/Mac系统 (Linux/Mac System)

在终端中执行：
```bash
chmod +x start.sh  # 确保脚本有执行权限
./start.sh
```

### 高级启动选项 (Advanced Startup Options)

系统提供了多种启动脚本，适用于不同场景：

#### 1. Python启动脚本 (Python Startup Script)

```bash
python start.py
```

这个脚本会：
- 检查Python依赖是否安装
- 启动后端服务
- 自动打开浏览器访问应用

#### 2. Windows批处理启动脚本 (Windows Batch Startup Script)

```
start.bat
```

这个脚本会：
- 检查Python和Node.js是否安装
- 创建并激活虚拟环境
- 安装后端依赖
- 启动后端服务
- 安装前端依赖
- 启动前端服务
- 打开浏览器访问应用

#### 3. 增强版Windows启动脚本 (Enhanced Windows Startup Script)

```
start_system.bat
```

这个脚本提供了更完善的启动功能：
- 检查并终止可能正在运行的后端和前端服务
- 启动后端服务，确保它绑定到所有网络接口（0.0.0.0:8000）
- 等待几秒钟，确保后端服务已经启动
- 启动前端服务
- 显示本地和局域网访问地址

#### 4. PowerShell启动脚本 (PowerShell Startup Script)

```
.\start_system.ps1
```

这个PowerShell脚本提供了更现代化的启动方式：
- 功能与增强版Windows启动脚本相同
- 增加了彩色输出，提高可读性
- 自动检测并显示服务器IP地址
- 提供更详细的启动状态信息

### 启动脚本对比 (Startup Script Comparison)

| 脚本名称 | 适用系统 | 特点 | 推荐场景 |
|---------|---------|------|---------|
| Run_Equipment_Reservation.bat | Windows | 最简单，一键启动 | 日常使用 |
| start.sh | Linux/Mac | 简单，一键启动 | 日常使用 |
| start.py | 全平台 | 只启动后端服务 | 开发测试 |
| start.bat | Windows | 完整启动前后端 | 首次使用 |
| start_system.bat | Windows | 增强功能，终止已运行服务 | 服务异常重启 |
| start_system.ps1 | Windows | 现代界面，自动检测IP | 局域网部署 |

### 端口使用说明 (Port Usage)

系统默认使用以下端口：
- 后端API服务：8000端口
- 前端开发服务器：8080端口

如需修改端口，可以：
1. 修改后端端口：在启动脚本中修改`uvicorn`命令的`--port`参数
2. 修改前端端口：在`frontend/vue.config.js`文件中修改`devServer.port`配置

### 常见启动问题 (Common Startup Issues)

#### 1. 端口被占用 (Port Occupied)

**症状**：启动时报错"Address already in use"
**解决方案**：
- 使用`start_system.bat`或`start_system.ps1`脚本，它们会自动终止占用端口的进程
- 手动终止占用端口的进程，然后重新启动

#### 2. 依赖安装失败 (Dependency Installation Failed)

**症状**：启动时报错"ModuleNotFoundError"或"npm ERR!"
**解决方案**：
- 确保网络连接正常
- 手动执行`pip install -r requirements.txt`安装后端依赖
- 进入frontend目录，执行`npm install`安装前端依赖

#### 3. 数据库错误 (Database Error)

**症状**：启动后无法访问数据或报数据库错误
**解决方案**：
- 检查`equipment_reservation.db`文件是否存在且未损坏
- 如果数据库损坏，可以删除数据库文件，系统会自动创建新的数据库
- 使用`create_admin.py`脚本创建管理员账户

## 局域网使用指南 (LAN Usage Guide)

### 配置局域网访问 (Configure LAN Access)

#### 1. 修改后端配置 (Backend Configuration)

后端服务需要监听所有网络接口，而不仅仅是localhost：

```bash
# 使用提供的脚本启动后端
./start_backend.sh  # Linux/Mac
# 或
start_backend.bat   # Windows
```

这些脚本已配置为使用`--host 0.0.0.0`参数，允许从任何IP地址访问。

#### 2. 修改前端配置 (Frontend Configuration)

前端需要知道后端API的确切地址。编辑`frontend/.env`文件：

```
# 将此行修改为服务器的实际IP地址
VUE_APP_API_URL=http://192.168.1.100:8000
```

将`192.168.1.100`替换为运行后端服务的服务器的实际IP地址。

##### 如何查找服务器IP地址 (How to Find Server IP Address)

在Windows系统上：
1. 打开命令提示符（按 Win+R，输入 cmd，按回车）
2. 输入 `ipconfig` 命令并按回车
3. 查找 "IPv4 地址" 或 "IP Address" 字段，通常是 192.168.x.x 或 10.x.x.x 格式的地址

在Linux/Mac系统上：
1. 打开终端
2. 输入 `ifconfig` 或 `ip addr` 命令并按回车
3. 查找 "inet" 字段后面的地址，通常是 192.168.x.x 或 10.x.x.x 格式的地址

**重要提示**：不要使用 `127.0.0.1` 或 `0.0.0.0` 作为 API 地址，这些是特殊地址，不适用于局域网访问。

### 访问系统 (Access the System)

1. 在服务器上，可以通过以下地址访问：
   - 前端：http://localhost:8080
   - 后端API：http://localhost:8000

2. 在局域网中的其他计算机上，可以通过以下地址访问：
   - 前端：http://[服务器IP]:8080
   - 后端API：http://[服务器IP]:8000

例如，如果服务器的IP地址是192.168.1.100，则访问地址为：
   - 前端：http://192.168.1.100:8080
   - 后端API：http://192.168.1.100:8000

### 故障排除 (Troubleshooting)

如果在局域网中无法访问系统，请检查以下几点：

1. 确保服务器的防火墙允许8000和8080端口的访问
2. 确保后端服务使用`--host 0.0.0.0`参数启动
3. 确保前端配置中的`VUE_APP_API_URL`设置为正确的服务器IP地址
4. 尝试在服务器上使用`ipconfig`（Windows）或`ifconfig`（Linux/Mac）命令查看正确的IP地址

#### 常见问题 (Common Issues)

##### 问题：只有一个前端和一个后端服务运行时，系统不能正常显示数据

**解决方案**：
1. 确保使用提供的启动脚本（`start_system.bat`或`start_system.ps1`）启动系统
2. 这些脚本会确保后端服务正确绑定到所有网络接口（0.0.0.0:8000）
3. 如果手动启动服务，请确保使用`--host 0.0.0.0`参数启动后端服务

##### 问题：局域网中的其他电脑无法访问系统

**解决方案**：
1. 确保前端配置中的API地址设置为服务器的实际IP地址
2. 确保服务器的防火墙允许8000和8080端口的访问
3. 尝试使用`ping [服务器IP]`命令测试网络连接

如果仍然无法访问，请尝试重新启动服务器和服务。

## Vue+Element的优势 (Advantages of Vue+Element)

1. **丰富的UI组件**：Element UI提供的日历、表格和表单组件非常适合预定系统
2. **响应式数据流**：数据变化自动反映到UI，无需手动DOM操作
3. **单页应用体验**：无刷新页面切换，提供流畅用户体验
4. **组件化开发**：可重用组件提高开发效率
5. **集成Unsplash API**：轻松整合第三方服务
6. **更适合复杂交互**：预定日历、时间选择等复杂交互更易实现
7. **移动端支持**：通过响应式设计和移动端优化，提供出色的移动端体验

## 移动端设计考虑 (Mobile Design Considerations)

1. **网络连接**：考虑弱网环境下的使用体验，实现数据缓存和离线功能
2. **屏幕尺寸**：确保在小屏设备上关键信息和操作清晰可见
3. **触摸操作**：优化所有交互元素，确保触摸友好
4. **设备能力**：使用设备原生能力增强体验，如共享、添加到主屏等
5. **垂直布局**：移动端以垂直滚动为主的内容布局
6. **简化流程**：针对移动用户简化预订流程，减少步骤
7. **性能优化**：针对移动设备优化资源加载和渲染性能

## 最近更新 (Recent Updates)

### 2023年5月更新 (May 2023 Updates)

#### 系统架构优化 (System Architecture Optimization)
- 重构了项目文件结构，使其更加清晰和有组织
- 添加了详细的开发工具脚本指南，方便开发和维护
- 更新了项目启动指南，提供多种启动方式的详细说明
- 优化了日志系统，支持按天轮转，保留30天，格式更详细
  - 日志文件按天自动分割，当前日志保存在app.log，历史日志格式为app.log.YYYY-MM-DD
  - 系统自动保留最近30天的日志文件，超过30天的日志文件会被自动删除
  - 日志格式更加详细，包含时间、日志级别、模块名称和行号等信息
- 添加了数据库管理路由，方便查看和管理数据库表

#### 邮件系统实现 (Email System Implementation)
- 完成了邮件通知系统的基础实现
- 添加了邮件模板管理功能，支持HTML和纯文本格式
- 实现了邮件日志记录，方便追踪邮件发送状态
- 添加了邮件模板同步工具，方便更新邮件模板
- 支持预约确认、修改、取消等多种邮件通知场景
- 添加了抄送人和密送人功能，支持为所有发出的邮件添加多个抄送人和密送人
- 实现了邮件设置测试功能，方便管理员验证邮件配置

#### 循环预约功能增强 (Recurring Reservation Enhancement)
- 优化了循环预约的创建流程，提供更灵活的重复选项
- 改进了循环预约的管理界面，显示更详细的子预约信息
- 增强了循环预约的取消功能，支持批量取消或单个取消
- 添加了循环预约的导出功能，支持导出为Excel格式
- 优化了循环预约在日历视图中的显示效果

#### 日历视图优化 (Calendar View Optimization)
- 改进了日历视图的性能，支持显示大量预约数据
- 优化了短时间预约的显示效果，确保信息清晰可见
- 添加了日历视图的打印功能，支持打印日/周/月视图
- 增强了日历视图的交互功能，支持拖拽操作
- 添加了日历视图的筛选功能，可按设备类别或状态筛选

#### 移动端体验提升 (Mobile Experience Enhancement)
- 全面优化了移动端界面，提供更好的触摸体验
- 改进了移动端日历视图，适配小屏幕设备
- 优化了移动端表单，简化输入流程
- 添加了移动端特定的导航组件，方便单手操作
- 提升了移动端的加载性能，减少等待时间

### 问题修复 (Bug Fixes)

#### 数据库相关修复 (Database Related Fixes)
- 修复了数据库连接池溢出问题，提高系统稳定性
- 解决了日期时间格式不一致问题，统一使用ISO格式
- 修复了数据库查询性能问题，优化了复杂查询
- 解决了并发访问时的数据库锁定问题
- 修复了数据库迁移时的字段类型不匹配问题

#### 预约管理相关修复 (Reservation Management Fixes)
- 修复了预约状态更新不及时的问题，现在实时更新
- 解决了预约冲突检测的逻辑错误，提高准确性
- 修复了预约查询分页显示问题，优化了分页逻辑
- 解决了预约取消后状态不更新的问题
- 修复了循环预约子预约状态不同步的问题

#### 界面和交互修复 (UI and Interaction Fixes)
- 修复了表格表头国际化显示问题，正确显示中英文
- 解决了表单提交后数据不刷新的问题
- 修复了日历视图中事件重叠显示错误
- 解决了移动端触摸响应不灵敏的问题
- 修复了国际化文本在特定组件中不生效的问题

#### 性能和稳定性优化 (Performance and Stability Optimization)
- 优化了前端资源加载，减少首屏加载时间
- 改进了后端API响应速度，提高并发处理能力
- 增强了错误处理机制，提供更友好的错误提示
- 优化了内存使用，减少内存泄漏风险
- 提升了系统在弱网环境下的稳定性

### 新增工具和脚本 (New Tools and Scripts)

#### 数据管理工具 (Data Management Tools)
- 添加了数据库备份和恢复工具，提高数据安全性
- 新增了数据导出工具，支持多种格式导出
- 添加了数据清理工具，帮助清理过期数据
- 新增了数据验证工具，确保数据完整性
- 添加了数据迁移工具，方便版本升级

#### 开发辅助脚本 (Development Assistant Scripts)
- 添加了代码格式化脚本，统一代码风格
- 新增了自动测试脚本，提高测试效率
- 添加了性能分析脚本，帮助识别性能瓶颈
- 新增了日志分析工具，方便排查问题
- 添加了环境检查脚本，确保开发环境一致

## 邮件通知功能 (Email Notification Feature)

系统集成了完善的邮件通知功能，在预定流程的关键节点自动发送邮件通知，提升用户体验并减少遗忘和冲突。

### 邮件通知类型 (Email Notification Types)

#### 1. 预订确认邮件 (Reservation Confirmation Email)
- **触发时机**: 用户成功预订设备后
- **接收人**: 预订用户和管理员
- **内容**: 预订详情、预订码、设备信息、时间段、位置等
- **功能**: 确认预订成功，提供预订码以便后续查询/修改

#### 2. 预订提醒邮件 (Reservation Reminder Email)
- **触发时机**: 预订前24小时
- **接收人**: 预订用户
- **内容**: 预订详情、时间和地点提醒
- **功能**: 提醒用户即将到来的预订，减少遗忘

#### 3. 预订修改通知 (Reservation Modification Notification)
- **触发时机**: 用户修改预订信息后
- **接收人**: 预订用户和管理员
- **内容**: 更新后的预订详情，突出显示修改部分
- **功能**: 确认修改已生效，保持信息透明

#### 4. 预订取消确认 (Reservation Cancellation Confirmation)
- **触发时机**: 用户取消预订后
- **接收人**: 预订用户和管理员
- **内容**: 取消的预订详情
- **功能**: 确认取消成功，释放设备资源

#### 5. 设备归还提醒 (Equipment Return Reminder)
- **触发时机**: 预订结束前1小时
- **接收人**: 预订用户
- **内容**: 提醒归还设备的时间和位置
- **功能**: 确保按时归还，减少逾期

#### 6. 超时未归还提醒 (Overdue Return Reminder)
- **触发时机**: 预订结束后设备未被归还（默认超时30分钟）
- **接收人**: 预订用户和管理员
- **内容**: 提醒设备已超时未归还，请求立即归还
- **功能**: 及时发现并处理逾期情况，减少设备挂失或占用
- **升级机制**: 可配置多级提醒，如超时1小时、4小时、24小时等不同级别的提醒
- **管理特权**: 管理员可手动将设备标记为已归还，结束提醒流程

### 邮件模板设计 (Email Template Design)

系统使用响应式HTML邮件模板，支持中英文双语，确保在各种邮件客户端中正确显示：

- 统一的品牌设计风格
- 清晰醒目的预订码和关键信息
- 直观的表格式布局展示预订详情
- 包含直接链接到系统的操作按钮
- 适配移动端邮件客户端

### 技术实现 (Technical Implementation)

邮件发送功能基于以下技术实现：

```python
# backend/utils/email_sender.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import logging
from dotenv import load_dotenv

# 使用Jinja2模板渲染邮件内容
# Using Jinja2 templates for email content
```

### 邮件配置 (Email Configuration)

在`.env`文件中配置邮件服务器信息：

```
# 邮件配置 / Email Configuration
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USER=reservation@example.com
EMAIL_PASSWORD=your_password
EMAIL_FROM=IT Equipment Reservation <reservation@example.com>
ADMIN_EMAIL=admin@example.com
SITE_URL=https://equipment.example.com
```

系统支持在管理员界面中配置邮件设置，包括：

- SMTP服务器和端口
- 发件人邮箱和名称
- SMTP用户名和密码
- 抄送人列表（多个邮箱用逗号分隔）
- 密送人列表（多个邮箱用逗号分隔）
- SSL/TLS加密选项
- 邮件功能启用/禁用

### 邮件触发机制 (Email Triggering Mechanism)

1. **实时触发**: 预订创建、修改、取消时立即发送
2. **定时任务**: 使用后台定时任务发送提醒邮件
   - 预订前24小时提醒
   - 预订结束前1小时归还提醒

### 邮件功能优势 (Email Feature Advantages)

1. **提高用户体验**: 用户全程了解预订状态
2. **减少预订遗忘**: 通过提醒减少无人使用的预订
3. **提高设备利用率**: 及时取消不需要的预订
4. **信息透明**: 管理员可及时了解预订变动
5. **减轻管理负担**: 自动化通知减少人工沟通
6. **信息同步**: 通过抄送和密送功能，确保相关人员同步获取信息

### 邮件服务扩展 (Email Service Extensions)

系统支持以下邮件服务扩展功能：

1. **邮件发送重试**: 邮件发送失败时自动重试
2. **邮件跟踪**: 记录邮件发送状态
3. **HTML/纯文本双版本**: 确保在所有邮件客户端正确显示
4. **自定义提醒时间**: 管理员可配置提醒时间
5. **批量邮件发送**: 系统状态变更等批量通知
6. **抄送和密送功能**: 支持为所有发出的邮件添加多个抄送人和密送人
7. **邮件测试功能**: 管理员可以在保存邮件设置前进行测试

## 开发工具脚本指南 (Development Tool Scripts Guide)

系统提供了多种开发和维护工具脚本，帮助开发者和管理员进行系统管理、测试和故障排除。

### 设置和初始化脚本 (Setup and Initialization Scripts)

#### 1. 后端初始化脚本 (Backend Initialization Script)
```bash
python setup.py
```
- 初始化后端环境
- 创建必要的目录结构
- 初始化数据库

#### 2. 创建管理员账户脚本 (Create Admin Account Script)
```bash
python create_admin.py
```
- 创建系统管理员账户
- 可以指定用户名和密码，或使用默认值

### 数据库工具脚本 (Database Tool Scripts)

#### 1. 检查数据库脚本 (Check Database Script)
```bash
python check_db.py
```
- 检查数据库连接是否正常
- 验证数据库表结构是否完整

#### 2. 检查数据库内容脚本 (Check Database Content Script)
```bash
python check_db_content.py
```
- 显示数据库中的关键数据
- 帮助诊断数据问题

#### 3. 更新数据库架构脚本 (Update Database Schema Script)
```bash
python update_db_schema.py
```
- 更新数据库表结构
- 添加新字段或修改现有字段

#### 4. 检查预约表脚本 (Check Reservation Table Script)
```bash
python check_reservation_table.py
```
- 检查预约表的完整性
- 显示预约记录统计信息

#### 5. 更新设备类别脚本 (Update Equipment Categories Script)
```bash
python update_equipment_categories.py
```
- 更新或添加设备类别
- 批量修改设备类别

### 测试和开发脚本 (Test and Development Scripts)

#### 1. 创建测试数据脚本 (Create Test Data Script)
```bash
python create_test_data.py
```
- 生成测试用的设备和预约数据
- 可以指定生成数据的数量和类型

#### 2. 创建短时间预约脚本 (Create Short Reservation Script)
```bash
python create_short_reservation.py
```
- 创建短时间（30分钟以内）的测试预约
- 用于测试日历视图中短时间预约的显示

#### 3. 测试预约API脚本 (Test Reservation API Script)
```bash
python test_reservation_api.py
```
- 测试预约相关的API接口
- 验证API功能是否正常

#### 4. 测试循环预约API脚本 (Test Recurring Reservation API Script)
```bash
python test_recurring_reservation_api.py
```
- 测试循环预约相关的API接口
- 验证循环预约功能是否正常

#### 5. 规范化日期时间格式脚本 (Normalize DateTime Format Script)
```bash
python normalize_datetime_format.py
```
- 统一数据库中的日期时间格式
- 修复格式不一致的问题

### 邮件系统脚本 (Email System Scripts)

#### 1. 同步邮件模板到数据库脚本 (Sync Email Templates to DB Script)
```bash
python sync_email_templates_to_db.py
```
- 将邮件模板文件同步到数据库
- 更新现有模板或添加新模板

#### 2. 清除邮件模板脚本 (Clear Email Templates Script)
```bash
python clear_email_templates.py
```
- 清除数据库中的邮件模板
- 用于重置邮件模板

#### 3. 打印邮件日志脚本 (Print Email Logs Script)
```bash
python print_email_logs.py
```
- 显示系统发送的邮件日志
- 帮助诊断邮件发送问题

#### 4. 添加HTML内容到邮件日志脚本 (Add HTML Content to Email Log Script)
```bash
python add_content_html_to_emaillog.py
```
- 为邮件日志添加HTML内容
- 完善邮件日志记录

#### 5. 更新邮件设置表脚本 (Update Email Settings Table Script)
```bash
python update_email_settings_table.py
```
- 更新邮件设置表结构
- 添加抄送人和密送人字段

### 预约状态管理脚本 (Reservation Status Management Scripts)

#### 1. 更新预约状态脚本 (Update Reservation Status Script)
```bash
python update_reservation_status.py
```
- 手动更新预约状态
- 根据当前时间更新预约为"已确认"、"使用中"或"已完成"状态

#### 2. 重置预约状态脚本 (Reset Reservation Status Script)
```bash
python reset_reservation_status.py
```
- 重置特定预约的状态
- 用于修复状态错误的预约

#### 3. 检查预约状态更新脚本 (Check Reservation Status Update Script)
```bash
python check_reservation_status_update.py
```
- 检查自动状态更新功能是否正常
- 显示状态更新日志

### 脚本使用建议 (Script Usage Recommendations)

1. **备份数据**：在使用修改数据的脚本前，先备份数据库文件
2. **测试环境**：优先在测试环境中使用脚本，验证效果后再在生产环境使用
3. **权限控制**：限制对脚本的访问权限，防止未授权使用
4. **日志记录**：脚本执行时记录日志，便于追踪问题
5. **定期维护**：定期使用检查脚本验证系统状态

## 待实现功能 (Features To Be Implemented)

以下是计划中但尚未完全实现的功能：

### 1. 邮件通知功能增强 (Email Notification Enhancement)
- 完善邮件通知系统，支持更多通知场景
- 优化邮件模板，提高邮件送达率
- 添加邮件跟踪功能，监控邮件发送状态
- 进一步完善抄送和密送功能，支持按预约类型设置不同的抄送人

### 2. 数据同步与备份机制 (Data Synchronization and Backup)
- 自动备份功能实现
- 数据导出功能（Excel、PDF）完善
- 数据恢复机制实现

### 3. 使用记录与统计分析 (Usage Records and Statistical Analysis)
- 设备使用率分析功能实现
- 报表生成系统完善
- 数据挖掘和预测分析功能实现


## 数据同步与备份机制 (Data Synchronization and Backup Mechanism)

系统将实现自动化的数据备份和同步策略，确保设备预定数据的安全性和可恢复性：

### 自动备份功能 (Automatic Backup)
- **定时备份**: 系统每日自动备份数据库到指定位置
- **增量备份**: 仅备份变化的数据，节省存储空间
- **备份轮换**: 保留最近7天、最近4周和最近12个月的备份
- **备份加密**: 对备份数据进行加密保护

### 数据导出功能 (Data Export)
- **Excel导出**: 支持将预定数据导出为Excel格式，便于报表生成
- **PDF报表**: 生成设备使用报表，包含统计图表和分析
- **历史记录**: 保存所有预定历史，便于追踪设备使用情况
- **跨系统同步**: 可与学校其他系统同步数据（如SchoolPal）

### 数据恢复机制 (Data Recovery)
- **一键恢复**: 管理员可通过简单操作从备份恢复数据
- **部分恢复**: 支持只恢复特定类型的数据
- **恢复日志**: 记录所有恢复操作，方便审计

## 使用记录与统计分析机制 (Usage Records and Statistical Analysis)

系统将自动记录并分析设备使用情况，为管理决策提供数据支持：

### 使用统计分析 (Usage Statistics)
- **设备使用率分析**: 统计各设备的使用频率、平均使用时长和空闲时间
- **高峰期分析**: 识别预定高峰时段，辅助资源调配决策
- **用户行为分析**: 分析不同部门/用户组的设备使用习惯
- **可视化仪表盘**: 直观展示关键指标和趋势

### 报表生成系统 (Report Generation)
- **定期报表**: 自动生成每日/每周/每月设备使用报表
- **自定义报表**: 管理员可根据需求生成特定条件的报表
- **使用效率评估**: 评估设备利用率和投资回报率
- **异常使用检测**: 识别不规律的使用模式或异常情况

### 数据挖掘功能 (Data Mining)
- **预测分析**: 基于历史数据预测未来设备需求
- **关联分析**: 识别设备使用之间的关联模式
- **决策支持**: 为设备购置、淘汰和维护提供数据支持

