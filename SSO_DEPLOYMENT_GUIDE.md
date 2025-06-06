# 🔐 SSO单点登录部署指南

## 📋 概述

本系统已成功集成SSO（单点登录）功能，支持多种SSO协议：
- **OAuth2/OIDC**: 支持Azure AD、Google、Keycloak、Okta等
- **SAML**: 支持企业级SAML身份提供者
- **自动用户管理**: 自动创建和同步SSO用户

## 🚀 快速开始

### 1. 数据库迁移

首先运行数据库迁移脚本添加SSO支持：

```bash
# 升级数据库，添加SSO字段
python migrations/add_sso_fields.py upgrade

# 创建默认角色
python migrations/add_sso_fields.py roles

# 检查迁移状态
python migrations/add_sso_fields.py status
```

### 2. 环境配置

复制SSO配置示例文件：

```bash
cp .env.sso.example .env
```

根据您的SSO提供者编辑 `.env` 文件：

```bash
# 基础SSO配置
SSO_ENABLED=true
SSO_PROVIDER=oauth2
SSO_AUTO_CREATE_USER=true
SSO_DEFAULT_ROLE=user

# OAuth2配置（以Azure AD为例）
OAUTH2_CLIENT_ID=your_azure_app_id
OAUTH2_CLIENT_SECRET=your_azure_app_secret
OAUTH2_AUTHORIZATION_URL=https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize
OAUTH2_TOKEN_URL=https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token
OAUTH2_USERINFO_URL=https://graph.microsoft.com/v1.0/me
OAUTH2_REDIRECT_URI=http://localhost:5000/auth/sso/callback
```

### 3. 启动应用

```bash
python app.py
```

### 4. 测试SSO登录

1. 访问登录页面：`http://localhost:5000/auth/login`
2. 点击"使用SSO登录"按钮
3. 完成SSO提供者的认证流程
4. 自动创建用户并登录系统

## 🔧 详细配置

### OAuth2/OIDC配置

#### Azure AD配置

```bash
# Azure AD应用注册
OAUTH2_CLIENT_ID=your_azure_app_id
OAUTH2_CLIENT_SECRET=your_azure_app_secret
OAUTH2_AUTHORIZATION_URL=https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize
OAUTH2_TOKEN_URL=https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token
OAUTH2_USERINFO_URL=https://graph.microsoft.com/v1.0/me
OAUTH2_SCOPE=openid profile email User.Read

# 用户属性映射
SSO_ATTR_USERNAME=userPrincipalName
SSO_ATTR_EMAIL=mail
SSO_ATTR_FIRST_NAME=givenName
SSO_ATTR_LAST_NAME=surname
SSO_ATTR_DISPLAY_NAME=displayName
```

#### Google配置

```bash
OAUTH2_CLIENT_ID=your_google_client_id
OAUTH2_CLIENT_SECRET=your_google_client_secret
OAUTH2_AUTHORIZATION_URL=https://accounts.google.com/o/oauth2/v2/auth
OAUTH2_TOKEN_URL=https://oauth2.googleapis.com/token
OAUTH2_USERINFO_URL=https://www.googleapis.com/oauth2/v2/userinfo
OAUTH2_SCOPE=openid profile email

SSO_ATTR_USERNAME=email
SSO_ATTR_EMAIL=email
SSO_ATTR_FIRST_NAME=given_name
SSO_ATTR_LAST_NAME=family_name
SSO_ATTR_DISPLAY_NAME=name
```

#### Keycloak配置

```bash
OAUTH2_CLIENT_ID=your_keycloak_client_id
OAUTH2_CLIENT_SECRET=your_keycloak_client_secret
OAUTH2_AUTHORIZATION_URL=https://your-keycloak.com/auth/realms/{realm}/protocol/openid-connect/auth
OAUTH2_TOKEN_URL=https://your-keycloak.com/auth/realms/{realm}/protocol/openid-connect/token
OAUTH2_USERINFO_URL=https://your-keycloak.com/auth/realms/{realm}/protocol/openid-connect/userinfo
OAUTH2_SCOPE=openid profile email groups

SSO_ATTR_USERNAME=preferred_username
SSO_ATTR_EMAIL=email
SSO_ATTR_GROUPS=groups
```

### SAML配置

```bash
SSO_PROVIDER=saml

# 服务提供者配置
SAML_SP_ENTITY_ID=http://your-domain.com
SAML_SP_ACS_URL=http://your-domain.com/auth/sso/saml/acs
SAML_SP_SLS_URL=http://your-domain.com/auth/sso/saml/sls

# 身份提供者配置
SAML_IDP_ENTITY_ID=https://your-idp.com/saml/metadata
SAML_IDP_SSO_URL=https://your-idp.com/saml/sso
SAML_IDP_SLS_URL=https://your-idp.com/saml/slo
SAML_IDP_X509_CERT="-----BEGIN CERTIFICATE-----
MIICXjCCAcegAwIBAgIBADANBgkqhkiG9w0BAQ0FADBLMQswCQYDVQQGEwJ1czEL
...
-----END CERTIFICATE-----"
```

## 👥 用户管理

### 自动用户创建

当 `SSO_AUTO_CREATE_USER=true` 时，系统会自动为新的SSO用户创建账户：

- **用户名**: 从SSO属性映射获取
- **邮箱**: 从SSO属性映射获取
- **角色**: 使用 `SSO_DEFAULT_ROLE` 设置的默认角色
- **状态**: 自动设置为 `approved`

### 用户属性同步

每次SSO登录时，系统会自动同步用户信息：

- 更新邮箱、姓名等基本信息
- 根据组映射更新用户角色
- 记录最后登录时间

### 组到角色映射

```bash
# 配置组到角色的映射
SSO_GROUP_ROLE_MAPPING={"admin": "admin", "administrators": "admin", "users": "user"}
```

## 🛡️ 安全配置

### 会话安全

```bash
# 会话配置
SESSION_TIMEOUT=3600
REMEMBER_COOKIE_DURATION=2592000
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

### 密钥管理

```bash
# 使用强密钥
SECRET_KEY=your_very_secure_secret_key_here

# OAuth2客户端密钥安全存储
OAUTH2_CLIENT_SECRET=your_secure_client_secret
```

## 📊 管理和监控

### SSO管理界面

管理员可以通过以下界面管理SSO：

1. **SSO管理页面**: `/sso_management`
   - 查看SSO状态和配置
   - 管理SSO用户
   - 测试SSO连接

2. **SSO状态API**: `/auth/sso/status`
   - 检查SSO是否启用
   - 查看配置的提供者类型

3. **SSO配置API**: `/auth/sso/config`
   - 查看详细配置信息（仅管理员）

### 用户管理

- **SSO用户列表**: 查看所有通过SSO注册的用户
- **用户同步**: 手动触发用户信息同步
- **权限管理**: 管理SSO用户的角色和权限

## 🔍 故障排除

### 常见问题

1. **"SSO登录未启用"**
   - 检查 `SSO_ENABLED=true`
   - 验证必需的配置参数

2. **"OAuth2 error: invalid_client"**
   - 检查客户端ID和密钥
   - 验证回调URL配置

3. **"用户不存在且不允许自动创建"**
   - 设置 `SSO_AUTO_CREATE_USER=true`
   - 或手动创建用户账户

4. **"Invalid state parameter"**
   - 检查会话配置
   - 确保cookies正常工作

### 调试模式

启用调试日志：

```bash
SSO_DEBUG=true
LOG_LEVEL=DEBUG
```

### 测试连接

使用内置的测试功能：

1. 访问SSO管理页面
2. 点击"测试SSO连接"
3. 查看详细的连接结果

## 📝 最佳实践

### 生产环境部署

1. **使用HTTPS**: 确保所有SSO通信使用HTTPS
2. **安全存储密钥**: 使用环境变量或密钥管理服务
3. **定期更新证书**: 监控SAML证书过期时间
4. **监控日志**: 设置SSO登录失败的告警

### 用户体验优化

1. **自定义登录页面**: 根据企业品牌定制SSO按钮
2. **错误处理**: 提供清晰的错误信息和帮助链接
3. **自动重定向**: 登录后重定向到用户原始请求的页面

### 安全建议

1. **最小权限原则**: 只请求必需的OAuth2权限范围
2. **定期审计**: 定期检查SSO用户权限
3. **会话管理**: 配置合适的会话超时时间
4. **日志记录**: 记录所有SSO认证事件

## 🎉 总结

SSO集成已完成，主要特性：

- ✅ **多协议支持**: OAuth2、SAML、OIDC
- ✅ **自动用户管理**: 创建、同步、权限管理
- ✅ **管理界面**: 完整的SSO管理和监控
- ✅ **安全性**: 完整的安全配置和最佳实践
- ✅ **可扩展性**: 支持多种SSO提供者

现在您可以为用户提供便捷、安全的单点登录体验！
