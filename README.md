# 🏫 设备预约管理系统 | Equipment Reservation System

<div align="center">

[![Vue.js](https://img.shields.io/badge/Vue.js-2.6-4FC08D?style=flat-square&logo=vue.js)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python)](https://python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite)](https://sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

**一个现代化的设备预约管理系统，专为学校和企业设计**

*A modern equipment reservation management system designed for schools and enterprises*


</div>

---

## 📖 项目简介 | Project Overview

设备预约管理系统是一个基于 Vue.js + FastAPI 的现代化 Web 应用，专为学校IT部门、实验室和企业设备管理而设计。系统提供直观的用户界面，支持设备预约、管理和监控，无需复杂的用户注册流程。

*Equipment Reservation System is a modern web application built with Vue.js + FastAPI, designed for school IT departments, laboratories, and enterprise equipment management. The system provides an intuitive user interface for equipment reservation, management, and monitoring without complex user registration processes.*

## ✨ 功能特性 | Key Features

### 🚀 核心功能 | Core Features

- **🔓 免登录预约** - 简化用户流程，仅需基本信息即可预约设备
- **📱 响应式设计** - 完美适配桌面端、平板和手机设备
- **🌍 多语言支持** - 内置中英文双语界面，支持语言扩展
- **🌙 暗色主题** - 支持亮色/暗色主题切换，保护视力
- **📅 智能日历** - 直观的日历视图，实时显示设备可用性

### 📋 预约管理 | Reservation Management

- **⚡ 快速预约** - 一键预约单个或多个设备
- **🔄 循环预约** - 支持周期性预约（每日/每周/每月）
- **🔍 冲突检测** - 智能检测时间冲突，避免重复预约
- **📧 邮件通知** - 自动发送预约确认、提醒和取消通知
- **🎫 预约码管理** - 使用唯一预约码查询、修改和取消预约

### 🛠️ 管理功能 | Administrative Features

- **📊 数据统计** - 实时统计面板，设备使用率分析
- **🏷️ 设备分类** - 灵活的设备分类和标签管理
- **📝 系统日志** - 完整的操作日志和错误追踪
- **📮 邮件管理** - 可自定义的邮件模板和发送配置
- **🗄️ 数据库管理** - 内置数据库查看和管理工具

## 🛠️ 技术栈 | Technology Stack

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


<table>
<tr>
<td width="50%">

## 🚀 快速开始 | Quick Start

### 📋 系统要求 | System Requirements

- **Python**: 3.8 或更高版本
- **Node.js**: 14.0 或更高版本
- **npm**: 6.0 或更高版本

### ⚡ 一键启动 | One-Click Start

```bash
# 1. 克隆项目
git clone https://github.com/chenchuanchao73/Equipment-Reservation-System.git
cd equipment-reservation-system

# 2. 安装后端依赖
pip install -r requirements.txt

# 3. 安装前端依赖
cd frontend
npm install
npm run serve

# 4. 启动系统
python start.py
```

🎉 **完成！** 系统将自动启动，浏览器会打开 `http://localhost:8080`

*🎉 **Done!** The system will start automatically and open `http://localhost:8080` in your browser*

## 📁 项目结构 | Project Structure

```
📦 Equipment-Reservation-System
├── 📄 README.md                   # 项目文档
├── 📄 requirements.txt            # Python依赖
├── 📄 config.py                   # 系统配置
├── 🗄️ equipment_reservation.db    # SQLite数据库
├── 🚀 start.py                    # 启动脚本
│
├── 📁 backend/                    # 后端代码
│   ├── 📄 main.py                 # FastAPI应用入口
│   ├── 📁 models/                 # 数据模型
│   ├── 📁 routes/                 # API路由
│   ├── 📁 schemas/                # 数据验证
│   ├── 📁 utils/                  # 工具函数
│   └── 📁 static/                 # 静态文件
│
└── 📁 frontend/                   # 前端代码
    ├── 📄 package.json            # 前端依赖
    ├── 📁 src/
    │   ├── 📁 views/              # 页面组件
    │   ├── 📁 components/         # 通用组件
    │   ├── 📁 api/                # API接口
    │   └── 📁 locales/            # 国际化
    └── 📁 public/                 # 公共资源
```

## 🎯 默认账户 | Default Account

系统首次启动时会创建默认管理员账户：

*The system will create a default admin account on first startup:*

- **用户名 | Username**: `admin`
- **密码 | Password**: `admin123`
- **角色 | Role**: `superadmin`

> ⚠️ **安全提醒 | Security Warning**: 首次登录后请立即修改默认密码！
>
> *Please change the default password immediately after first login!*

## 🎮 使用指南 | Usage Guide

### 👥 用户功能 | User Features

#### 📋 设备预约 | Equipment Reservation

1. **浏览设备** - 查看所有可用设备和详细信息
2. **选择时间** - 在日历中选择预约时间段
3. **填写信息** - 输入联系信息和使用目的
4. **获取预约码** - 系统生成唯一预约码用于管理

#### 🔍 预约管理 | Reservation Management

- **查询预约** - 使用预约码查询预约状态
- **修改预约** - 更改预约时间或设备
- **取消预约** - 取消不需要的预约
- **查看历史** - 查看预约历史记录

### 👨‍💼 管理员功能 | Admin Features

#### 🛠️ 设备管理 | Equipment Management

- **添加设备** - 录入新设备信息和图片
- **设备分类** - 创建和管理设备类别
- **状态管理** - 设置设备可用/维护状态
- **批量操作** - 支持批量导出、选择字段导出预定表

#### 📊 数据统计 | Data Analytics

- **预约报表** - 生成各类预约统计报表
- **系统监控** - 实时监控系统运行状态

## 🌐 演示 | Demo

### 📱 界面预览 | Interface Preview


![1](https://github.com/user-attachments/assets/e2c68aba-98f7-4897-835a-425958494853)
![2](https://github.com/user-attachments/assets/071522db-1f35-42b4-bea1-93c200a27f6b)
![3](https://github.com/user-attachments/assets/37340453-7269-4dbb-a45c-8b69f828f395)
![4](https://github.com/user-attachments/assets/f1dacaee-8163-426a-a189-cec7f6e37015)
![image](https://github.com/user-attachments/assets/272a5df8-b35f-4c80-9e2c-0cd180832ea9)
![image](https://github.com/user-attachments/assets/0a8a87e3-4d58-47ad-9b68-7830a9d638da)
![image](https://github.com/user-attachments/assets/08ef78cd-6aaa-4c1a-a9c2-abed2911537a)
![image](https://github.com/user-attachments/assets/209bdf66-e597-49af-b01a-9cc0b15666e4)
![image](https://github.com/user-attachments/assets/e8621514-49bb-48d7-af76-f7f3c32e057c)
![image](https://github.com/user-attachments/assets/9168431c-c036-4220-bdef-f2c09a3c38b6)
![image](https://github.com/user-attachments/assets/711c6d17-af35-4f73-bf2a-372f4dbdd17b)
![image](https://github.com/user-attachments/assets/93fa10b6-a02e-44c8-b113-1ec5bd03b460)
![image](https://github.com/user-attachments/assets/ac995b72-d37f-4794-9909-49a652eec80d)
![image](https://github.com/user-attachments/assets/c94e37be-aa19-4abe-ab15-585ef89fb7c7)
![image](https://github.com/user-attachments/assets/e04e3cb9-369b-42ff-9d0b-fe7447620041)
![image](https://github.com/user-attachments/assets/dce13a5c-8638-419a-b770-603811de7d84)



<table>
<tr>
<td width="50%">
<h4>🏠 用户界面 | User Interface</h4>
<ul>
<li>简洁直观的设备浏览界面</li>
<li>响应式日历预约系统</li>
<li>移动端友好的操作体验</li>
<li>多语言和主题切换</li>
</ul>
</td>
<td width="50%">
<h4>⚙️ 管理界面 | Admin Interface</h4>
<ul>
<li>功能完整的管理控制台</li>
<li>实时数据统计面板</li>
<li>设备和预约管理工具</li>
<li>系统配置和日志查看</li>
</ul>
</td>
</tr>
</table>

## 🤝 贡献指南 | Contributing

我们欢迎所有形式的贡献！无论是报告问题、提出功能建议还是提交代码。

*We welcome all forms of contributions! Whether it's reporting issues, suggesting features, or submitting code.*

### 🐛 报告问题 | Reporting Issues

在提交问题之前，请：

*Before submitting an issue, please:*

1. **搜索现有问题** - 确保问题尚未被报告
2. **提供详细信息** - 包括系统环境、错误信息和重现步骤
3. **使用问题模板** - 按照提供的模板填写问题详情

### 💡 功能建议 | Feature Requests

我们很乐意听取您的想法：

*We'd love to hear your ideas:*

- 描述您希望添加的功能
- 解释为什么这个功能有用
- 提供可能的实现方案

### 🔧 代码贡献 | Code Contributions

#### 开发环境设置 | Development Setup

```bash
# 1. Fork 项目并克隆
git clone https://github.com/chenchuanchao73/Equipment-Reservation-System.git

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 安装开发依赖
pip install -r requirements.txt
cd frontend && npm install

# 4. 启动开发服务器
python start.py
```

#### 提交规范 | Commit Guidelines

- 使用清晰的提交信息
- 遵循 [Conventional Commits](https://conventionalcommits.org/) 规范
- 每个提交只包含一个逻辑变更

```bash
# 提交示例
git commit -m "feat: 添加设备批量导入功能"
git commit -m "fix: 修复预约时间冲突检测问题"
git commit -m "docs: 更新API文档"
```

### 📋 Pull Request 流程 | Pull Request Process

1. **确保代码质量** - 运行测试并确保代码符合规范
2. **更新文档** - 如果需要，更新相关文档
3. **描述变更** - 在PR中详细描述您的变更
4. **等待审核** - 维护者会尽快审核您的PR

## 📄 许可证 | License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

*This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.*

### 🔓 开源声明 | Open Source Declaration

- ✅ **免费使用** - 个人和商业用途均可免费使用
- ✅ **修改自由** - 可以自由修改和定制
- ✅ **分发自由** - 可以自由分发和再分发
- ✅ **无担保** - 软件按"原样"提供，不提供任何担保

## 🆘 支持与帮助 | Support & Help

### 📞 获取帮助 | Getting Help

如果您遇到问题或需要帮助：

*If you encounter issues or need help:*

1. **查看文档** - 首先查看本README和项目文档
2. **搜索问题** - 在Issues中搜索类似问题
3. **提交问题** - 如果找不到解决方案，请提交新的Issue
4. **社区讨论** - 参与项目讨论和交流

### 🔗 相关链接 | Related Links

- **项目主页** | Project Home: [GitHub Repository](https://github.com/chenchuanchao73/Equipment-Reservation-System.git)
- **问题追踪** | Issue Tracker: [GitHub Issues](https://github.com/chenchuanchao73/Equipment-Reservation-System/issues)
- **功能请求** | Feature Requests: [GitHub Discussions](https://github.com/chenchuanchao73/Equipment-Reservation-System/discussions)

### 📊 项目状态 | Project Status

- **开发状态**: 🟢 活跃开发中
- **稳定性**: 🟡 Beta版本
- **维护状态**: 🟢 积极维护

## 🙏 致谢 | Acknowledgments

感谢所有为这个项目做出贡献的开发者和用户！

*Thanks to all developers and users who have contributed to this project!*

### 🛠️ 技术致谢 | Technical Acknowledgments

- [Cursor](https://cursor.com) - 代码的整体逻辑与计划
- [Augment Code](https://app.augmentcode.com) - 代码的完整书写与修改
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能Web框架
- [Element UI](https://element.eleme.io/) - 企业级UI组件库
- [FullCalendar](https://fullcalendar.io/) - 功能丰富的日历组件

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我一个星标！**

*⭐ If this project helps you, please give me a star!*

**📧 联系我吧 | Contact Us**: [chen.chuanchao@htschools.org]

---

*Made with ❤️ by the Equipment Reservation System Team*

</div>
