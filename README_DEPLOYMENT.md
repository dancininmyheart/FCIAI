# PPT翻译系统 - 部署文档

## 📁 部署文件说明

本项目提供了完整的部署解决方案，包含以下文件：

### 🔧 核心部署文件

| 文件名 | 说明 | 用途 |
|--------|------|------|
| `requirements.txt` | Python依赖包列表 | 安装所有必需的Python包 |
| `setup_database.py` | 一键数据库创建脚本 | 自动创建数据库、表结构和初始数据 |
| `DEPLOYMENT_GUIDE.md` | 详细部署指南 | 完整的部署步骤和配置说明 |
| `test_deployment.py` | 部署环境测试脚本 | 验证部署环境是否正确配置 |

### 🚀 快速安装脚本

| 文件名 | 平台 | 说明 |
|--------|------|------|
| `quick_install.sh` | Linux/Ubuntu | 一键安装脚本，自动配置整个系统 |
| `quick_install.bat` | Windows | Windows批处理安装脚本 |

### 📋 生成的配置文件

| 文件名 | 说明 | 自动生成 |
|--------|------|----------|
| `.env` | 环境变量配置文件 | ✅ |
| `database_setup.log` | 数据库创建日志 | ✅ |
| `deployment_test_report.txt` | 部署测试报告 | ✅ |

## 🚀 快速开始

### 方法一：使用快速安装脚本（推荐）

#### Linux/Ubuntu:
```bash
chmod +x quick_install.sh
sudo ./quick_install.sh
```

#### Windows:
```cmd
# 以管理员身份运行
quick_install.bat
```

### 方法二：手动部署

#### 1. 安装Python依赖
```bash
pip install -r requirements.txt
```

#### 2. 创建数据库
```bash
python setup_database.py
```

#### 3. 测试部署环境
```bash
python test_deployment.py
```

#### 4. 启动应用
```bash
python app.py
```

## 📦 依赖包说明

### 核心Web框架
- **Flask 3.0.3**: Web应用框架
- **Flask-SQLAlchemy 3.1.1**: 数据库ORM
- **Flask-Login 0.6.3**: 用户认证
- **Flask-CORS 4.0.0**: 跨域支持
- **Flask-Mail 0.9.1**: 邮件发送

### 数据库驱动
- **PyMySQL 1.1.0**: MySQL数据库驱动
- **mysqlclient 2.2.0**: MySQL客户端库

### 异步和并发
- **aiohttp 3.9.1**: 异步HTTP客户端
- **aiofiles 23.2.0**: 异步文件操作
- **gunicorn 21.2.0**: WSGI服务器

### AI和翻译
- **dashscope 1.17.0**: 阿里云大模型SDK
- **openai 1.6.1**: OpenAI API客户端

### 文档处理
- **python-pptx 0.6.23**: PPT文件处理
- **PyMuPDF 1.23.8**: PDF文件处理
- **easyocr 1.7.2**: OCR文字识别

### 图像处理
- **Pillow 10.1.0**: 图像处理库
- **opencv-python 4.8.1.78**: 计算机视觉库
- **numpy 1.24.4**: 数值计算库

### 网络爬虫
- **requests 2.31.0**: HTTP请求库
- **beautifulsoup4 4.12.2**: HTML解析
- **selenium 4.16.0**: 浏览器自动化

## 🗄️ 数据库结构

### 核心表结构

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `users` | 用户表 | id, username, password, role_id, status |
| `role` | 角色表 | id, name |
| `permission` | 权限表 | id, name, description |
| `upload_records` | 上传记录表 | id, user_id, filename, file_path, upload_time |
| `translation` | 翻译记录表 | id, english, chinese, user_id |
| `stop_words` | 停止词表 | id, word, user_id |
| `ingredient` | 成分表 | id, food_name, ingredient, path |

### 默认数据

#### 角色和权限
- **admin**: 管理员角色，拥有所有权限
- **user**: 普通用户角色，拥有基础功能权限

#### 默认管理员账户
- **用户名**: admin
- **密码**: admin123
- **状态**: 已激活

## 🔧 配置说明

### 环境变量 (.env)

```env
# 数据库配置
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ppt_translate_db

# Flask配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False

# 上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800

# API配置
DASHSCOPE_API_KEY=your-dashscope-api-key

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
```

### 目录结构

```
project/
├── app/                    # 应用主目录
│   ├── function/          # 功能模块
│   ├── models/            # 数据模型
│   ├── templates/         # 模板文件
│   ├── utils/             # 工具函数
│   └── views/             # 视图函数
├── uploads/               # 上传文件目录
│   ├── ppt/              # PPT文件
│   ├── pdf/              # PDF文件
│   ├── annotation/       # 注释文件
│   └── temp/             # 临时文件
├── logs/                  # 日志目录
├── static/                # 静态文件
└── venv/                  # Python虚拟环境
```

## 🔒 安全配置

### 生产环境安全建议

1. **修改默认密码**: 立即修改admin账户密码
2. **配置HTTPS**: 使用SSL证书加密传输
3. **防火墙设置**: 只开放必要端口
4. **定期备份**: 备份数据库和上传文件
5. **日志监控**: 监控系统日志和错误

### 文件权限

```bash
# 设置适当的文件权限
chmod 755 /path/to/project
chmod 777 /path/to/project/uploads
chmod 777 /path/to/project/logs
```

## 📊 性能优化

### 生产环境配置

#### Gunicorn配置
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 app:app
```

#### Nginx配置
```nginx
server {
    listen 80;
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 数据库优化

```sql
-- MySQL配置优化
SET GLOBAL innodb_buffer_pool_size = 2147483648;  -- 2GB
SET GLOBAL max_connections = 200;
SET GLOBAL query_cache_size = 67108864;  -- 64MB
```

## 🚨 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 数据库连接失败 | MySQL未启动或配置错误 | 检查MySQL服务和配置 |
| 依赖包安装失败 | 网络问题或版本冲突 | 使用国内镜像源 |
| 文件上传失败 | 权限不足或磁盘空间不足 | 检查目录权限和磁盘空间 |
| OCR功能异常 | EasyOCR初始化失败 | 检查GPU驱动和内存 |

### 日志查看

```bash
# 应用日志
tail -f logs/app.log

# 数据库设置日志
cat database_setup.log

# 系统服务日志（Linux）
journalctl -u ppt-translation -f
```

## 📞 技术支持

### 获取帮助

1. **查看日志**: 检查相关日志文件
2. **运行测试**: 执行 `python test_deployment.py`
3. **检查配置**: 验证 `.env` 文件配置
4. **查看文档**: 参考 `DEPLOYMENT_GUIDE.md`

### 联系方式

如需技术支持，请提供：
- 操作系统版本
- Python版本
- 错误日志
- 部署测试报告

---

## 🎉 部署成功

部署完成后，您可以：

1. **访问系统**: http://localhost:5000
2. **管理员登录**: admin / admin123
3. **开始使用**: 上传PPT文件进行翻译
4. **配置API**: 设置阿里云API密钥

**祝您使用愉快！** 🚀
