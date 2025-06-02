# PPT翻译系统部署指南

## 📋 系统要求

### 硬件要求
- **CPU**: 4核心以上
- **内存**: 8GB以上（推荐16GB）
- **存储**: 50GB以上可用空间
- **GPU**: 可选，用于OCR加速

### 软件要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Windows 10+
- **Python**: 3.8+
- **MySQL**: 5.7+ 或 8.0+
- **Redis**: 6.0+（可选，用于缓存）

## 🚀 快速部署

### 1. 环境准备

#### 安装Python和pip
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip

# Windows
# 从 https://python.org 下载并安装Python 3.8+
```

#### 安装MySQL
```bash
# Ubuntu/Debian
sudo apt install mysql-server mysql-client

# CentOS/RHEL
sudo yum install mysql-server mysql

# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation
```

#### 安装Redis（可选）
```bash
# Ubuntu/Debian
sudo apt install redis-server

# CentOS/RHEL
sudo yum install redis

# 启动Redis服务
sudo systemctl start redis
sudo systemctl enable redis
```

### 2. 项目部署

#### 克隆项目
```bash
git clone <项目地址>
cd ppt-translation-system
```

#### 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 配置数据库
```bash
# 运行一键数据库创建脚本
python setup_database.py
```

#### 配置环境变量
编辑 `.env` 文件，修改以下配置：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=ppt_translate_db

# Flask配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# API配置
DASHSCOPE_API_KEY=your-dashscope-api-key

# 邮件配置（可选）
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
```

### 3. 启动应用

#### 开发模式
```bash
python app.py
```

#### 生产模式
```bash
# 使用Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 或使用uWSGI
uwsgi --http :5000 --module app:app --processes 4
```

## 🔧 详细配置

### 数据库配置

#### MySQL优化配置
在 `/etc/mysql/mysql.conf.d/mysqld.cnf` 中添加：
```ini
[mysqld]
# 字符集配置
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 性能优化
innodb_buffer_pool_size = 2G
innodb_log_file_size = 256M
max_connections = 200
query_cache_size = 64M
```

#### 创建数据库用户
```sql
CREATE USER 'ppt_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON ppt_translate_db.* TO 'ppt_user'@'localhost';
FLUSH PRIVILEGES;
```

### Web服务器配置

#### Nginx配置
创建 `/etc/nginx/sites-available/ppt-translation`：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/project/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /uploads {
        alias /path/to/your/project/uploads;
        expires 1d;
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/ppt-translation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 系统服务配置

#### 创建Systemd服务
创建 `/etc/systemd/system/ppt-translation.service`：
```ini
[Unit]
Description=PPT Translation System
After=network.target mysql.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
Environment=PATH=/path/to/your/project/venv/bin
ExecStart=/path/to/your/project/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable ppt-translation
sudo systemctl start ppt-translation
```

## 🔒 安全配置

### 防火墙设置
```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### SSL证书配置
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 文件权限设置
```bash
# 设置项目目录权限
sudo chown -R www-data:www-data /path/to/your/project
sudo chmod -R 755 /path/to/your/project
sudo chmod -R 777 /path/to/your/project/uploads
sudo chmod -R 777 /path/to/your/project/logs
```

## 📊 监控和日志

### 日志配置
系统日志位置：
- 应用日志: `logs/app.log`
- 数据库设置日志: `database_setup.log`
- Nginx日志: `/var/log/nginx/`
- 系统服务日志: `journalctl -u ppt-translation`

### 监控脚本
创建监控脚本 `monitor.sh`：
```bash
#!/bin/bash
# 检查服务状态
systemctl is-active ppt-translation
systemctl is-active mysql
systemctl is-active nginx

# 检查磁盘空间
df -h /

# 检查内存使用
free -h

# 检查进程
ps aux | grep gunicorn
```

## 🔄 备份和恢复

### 数据库备份
```bash
# 创建备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u root -p ppt_translate_db > backup_${DATE}.sql
```

### 文件备份
```bash
# 备份上传文件
tar -czf uploads_backup_${DATE}.tar.gz uploads/
```

## 🚨 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 检查数据库配置
mysql -u root -p -e "SHOW DATABASES;"
```

#### 2. 权限问题
```bash
# 检查文件权限
ls -la uploads/
sudo chown -R www-data:www-data uploads/
```

#### 3. 内存不足
```bash
# 检查内存使用
free -h
# 添加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. 端口占用
```bash
# 检查端口使用
sudo netstat -tlnp | grep :5000
sudo lsof -i :5000
```

## 📞 技术支持

如遇到部署问题，请：
1. 检查日志文件
2. 确认系统要求
3. 验证配置文件
4. 联系技术支持

---

**部署完成后，使用以下默认账户登录：**
- 用户名: `admin`
- 密码: `admin123`

**请立即修改默认密码！**
