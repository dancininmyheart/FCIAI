# 🔐 FCI AI翻译助手 Authing SSO部署指南

## 📋 概述

本指南详细说明如何为FCI AI翻译助手UAT环境配置Authing身份云SSO登录。

### 🎯 配置信息

- **应用ID**: `683ebc2889ae4d4c1ff7e111`
- **应用Secret**: `082339b43a8da9636332e1f4d11111`
- **用户池域名**: `https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111`
- **回调URL**: `https://fci-ai-agent-uat.rfc-friso.com/auth/sso/callback`

## 🚀 快速部署

### 1. 配置环境变量

复制Authing配置文件：

```bash
cp .env.authing.example .env
```

配置文件内容已预设为FCI AI翻译助手UAT环境：

```bash
# 基础配置
SSO_ENABLED=true
SSO_PROVIDER=oauth2
SSO_AUTO_CREATE_USER=true
SSO_DEFAULT_ROLE=user

# Authing配置
OAUTH2_CLIENT_ID=683ebc2889ae4d4c1ff7e111
OAUTH2_CLIENT_SECRET=082339b43a8da9636332e1f4d11111
OAUTH2_AUTHORIZATION_URL=https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/auth
OAUTH2_TOKEN_URL=https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/token
OAUTH2_USERINFO_URL=https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/me
OAUTH2_LOGOUT_URL=https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/session/end
OAUTH2_SCOPE=openid profile email phone
OAUTH2_REDIRECT_URI=https://fci-ai-agent-uat.rfc-friso.com/auth/sso/callback
```

### 2. 运行数据库迁移

```bash
python migrations/add_sso_fields.py upgrade
```

### 3. 验证配置

```bash
python test_authing_config.py
```

### 4. 启动应用

```bash
python app.py
```

## 🔧 详细配置说明

### Authing端点配置

| 端点类型 | URL |
|---------|-----|
| 授权端点 | `https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/auth` |
| 令牌端点 | `https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/token` |
| 用户信息端点 | `https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/me` |
| 登出端点 | `https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/session/end` |
| OIDC配置 | `https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/.well-known/openid_configuration` |

### 用户属性映射

Authing返回的用户信息字段映射：

```bash
SSO_ATTR_USERNAME=username      # 用户名
SSO_ATTR_EMAIL=email           # 邮箱
SSO_ATTR_FIRST_NAME=given_name # 名字
SSO_ATTR_LAST_NAME=family_name # 姓氏
SSO_ATTR_DISPLAY_NAME=name     # 显示名称
SSO_ATTR_PHONE=phone_number    # 手机号
SSO_ATTR_PICTURE=picture       # 头像URL
```

### 权限范围

```bash
OAUTH2_SCOPE=openid profile email phone
```

- `openid`: 基础OIDC标识
- `profile`: 用户基本信息
- `email`: 邮箱信息
- `phone`: 手机号信息

## 🔄 SSO登录流程

### 1. 用户发起登录

用户访问：`https://fci-ai-agent-uat.rfc-friso.com/auth/login`

点击"使用SSO登录"按钮

### 2. 重定向到Authing

系统重定向到：
```
https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/auth?
client_id=683ebc2889ae4d4c1ff7e111&
response_type=code&
scope=openid+profile+email+phone&
redirect_uri=https://fci-ai-agent-uat.rfc-friso.com/auth/sso/callback&
state=random_state
```

### 3. 用户在Authing完成认证

用户在Authing登录页面输入凭据

### 4. Authing回调

认证成功后，Authing重定向到：
```
https://fci-ai-agent-uat.rfc-friso.com/auth/sso/callback?
code=authorization_code&
state=random_state
```

### 5. 系统处理回调

- 验证state参数
- 用authorization_code换取access_token
- 用access_token获取用户信息
- 创建/更新用户账户
- 登录用户

## 🛠️ 开发环境配置

### 本地开发

如需在本地测试，修改回调URL：

```bash
# 注释掉生产环境配置
# OAUTH2_REDIRECT_URI=https://fci-ai-agent-uat.rfc-friso.com/auth/sso/callback

# 启用本地开发配置
OAUTH2_REDIRECT_URI=http://localhost:5000/auth/sso/callback
```

**注意**: 需要在Authing应用配置中添加本地回调URL。

### 测试环境

测试环境可以使用不同的回调URL：

```bash
OAUTH2_REDIRECT_URI=https://test.your-domain.com/auth/sso/callback
```

## 🔍 故障排除

### 常见错误

#### 1. "invalid_client"
- **原因**: 客户端ID或密钥错误
- **解决**: 检查`OAUTH2_CLIENT_ID`和`OAUTH2_CLIENT_SECRET`

#### 2. "redirect_uri_mismatch"
- **原因**: 回调URL不匹配
- **解决**: 确保`OAUTH2_REDIRECT_URI`与Authing应用配置一致

#### 3. "invalid_scope"
- **原因**: 权限范围配置错误
- **解决**: 检查`OAUTH2_SCOPE`配置

#### 4. "access_denied"
- **原因**: 用户拒绝授权或权限不足
- **解决**: 检查用户权限和应用配置

### 调试步骤

1. **启用调试日志**:
```bash
SSO_DEBUG=true
LOG_LEVEL=DEBUG
```

2. **检查端点连通性**:
```bash
python test_authing_config.py
```

3. **验证OIDC配置**:
访问：`https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/.well-known/openid_configuration`

4. **检查应用日志**:
查看应用启动日志中的SSO初始化信息

## 📊 管理和监控

### SSO管理界面

管理员可以访问：`https://fci-ai-agent-uat.rfc-friso.com/sso_management`

功能包括：
- 查看SSO状态和配置
- 管理SSO用户
- 测试SSO连接
- 查看用户登录记录

### API端点

- **SSO状态**: `GET /auth/sso/status`
- **SSO配置**: `GET /auth/sso/config` (管理员)
- **SSO用户**: `GET /api/users/sso` (管理员)

## 🔒 安全配置

### 生产环境安全

1. **使用HTTPS**: 确保所有通信使用HTTPS
2. **安全存储密钥**: 使用环境变量或密钥管理服务
3. **会话安全**:
```bash
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

### 用户权限管理

```bash
# 组到角色映射
SSO_GROUP_ROLE_MAPPING={"admin": "admin", "users": "user", "translators": "user"}
```

## 📝 Authing API参考

### 主要接口

根据Authing API文档 (https://api-explorer.authing.cn/)：

1. **登录**: `/oidc/auth`
2. **获取token**: `/oidc/token`
3. **获取用户资料**: `/oidc/me`
4. **登出**: `/oidc/session/end`
5. **校验token**: `/api/v2/oidc/validate_token`

### 调用顺序

1. 重定向到授权端点
2. 用户完成认证
3. 获取authorization code
4. 交换access token
5. 获取用户信息
6. 创建用户会话

## ✅ 验证清单

部署前请确认：

- [ ] 配置文件已正确设置
- [ ] 数据库迁移已完成
- [ ] Authing应用回调URL已配置
- [ ] 端点连通性测试通过
- [ ] SSO登录流程测试成功
- [ ] 用户信息正确映射
- [ ] 权限和角色配置正确

## 🎉 完成

配置完成后，用户可以：

1. 访问登录页面
2. 点击"使用SSO登录"
3. 在Authing完成认证
4. 自动登录到FCI AI翻译助手

现在您的FCI AI翻译助手已成功集成Authing SSO！🎉
