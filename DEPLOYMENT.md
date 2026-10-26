# StorePilot AI 云端部署指南

## GitHub 仓库（已完成）

✅ 代码已推送至：https://github.com/leetony6767-svg/auto-pilot-ai

---

## 方案一：Railway 部署（推荐）

### 步骤 1：登录 Railway
打开 https://railway.app/
使用 GitHub 账号登录（选择 `leetony6767-svg`）

### 步骤 2：创建项目
1. 点击 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. 找到并选择 `auto-pilot-ai` 仓库

### 步骤 3：配置环境变量
在 Railway Dashboard → Settings → Variables 中添加：

```
OPENROUTER_API_KEY=sk-or-v1-你的密钥
ANTHROPIC_API_KEY=sk-ant-你的密钥
OPENAI_API_KEY=sk-你的密钥

DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://localhost:6379/0

CHROMA_PATH=./storage/chroma_db
DEPLOYMENT_BASE_URL=https://your-app.onrailway.app

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@storepilot.ai
```

**注意**：LLM API Key 是必须的，否则 AI 功能无法工作。

### 步骤 4：启用 PostgreSQL（可选）
1. 在 Railway Dashboard 点击 **"New"** → **"PostgreSQL"**
2. 等待数据库创建完成
3. 复制 `DATABASE_URL` 环境变量值
4. 粘贴到上方的 Variables 中

### 步骤 5：部署
1. Railway 会自动检测 `Procfile` 和 `Dockerfile`
2. 点击 **"Deploy"**
3. 等待构建完成（约 2-3 分钟）
4. 获取公开 URL：`https://your-app-name-xxx.rajayan.railway.app`

---

## 方案二：Render 部署

### 步骤 1：登录 Render
打开 https://dashboard.render.com/
使用 GitHub 账号登录

### 步骤 2：创建 Web Service
1. 点击 **"New +"** → **"Blueprint"**
2. 连接 GitHub 仓库 `leetony6767-svg/auto-pilot-ai`
3. Render 会自动读取 `render.yaml` 配置

### 步骤 3：配置服务
在 `render.yaml` 中已预配置：
- ✅ Web Service（Free tier）
- ✅ PostgreSQL Database（Free tier，256MB）
- ✅ 健康检查端点 `/api/info`
- ✅ 自动 HTTPS

### 步骤 4：添加环境变量
在 Render Dashboard → Environment 中添加：
```
OPENROUTER_API_KEY=sk-or-v1-你的密钥
ANTHROPIC_API_KEY=sk-ant-你的密钥
OPENAI_API_KEY=sk-你的密钥
```

### 步骤 5：部署
1. 点击 **"Apply"**
2. 等待构建完成
3. 获取公开 URL：`https://storepilot-ai.onrender.com`

---

## 本地测试云端配置

### Docker 本地测试
```bash
cd "C:/Users/master/WorkBuddy AI/rea逆向的特定功能/mvp-agent-os"
docker build -t storepilot-ai .
docker run -p 8000:8000 --env-file .env storepilot-ai
```

### 验证健康检查
```bash
curl http://localhost:8000/api/info
```

---

## 部署后检查清单

- [ ] API 端点正常响应：`GET /api/info`
- [ ] 支付信息正确：`GET /api/crypto-payment`
- [ ] 银行账户正确：`GET /api/bank-account`
- [ ] 价格信息正确：`GET /api/pricing`
- [ ] 前端页面加载正常：`GET /`
- [ ] WebSocket 连接正常：`WS /ws/{user_id}`

---

## 故障排除

### 问题：部署后 502 Bad Gateway
- 检查日志：Railway Dashboard → Your Service → Logs
- 确认 `Procfile` 存在且格式正确
- 确认所有环境变量已设置

### 问题：数据库连接失败
- 确认 `DATABASE_URL` 格式正确
- Railway 免费 PostgreSQL 每 90 天清理一次，需设置备份

### 问题：LLM 功能无法使用
- 检查 API Key 是否正确配置
- 确认 API Key 未过期
- 检查网络是否能访问 OpenRouter/Anthropic/OpenAI

---

## 成本估算

### Railway Free Tier
- **Web Service**: 免费（$5/month 额度）
- **PostgreSQL**: 免费（500MB 存储）
- **Redis**: 免费（100MB 存储）
- **实际运行成本**: 主要为 LLM API 调用费用

### Render Free Tier
- **Web Service**: 免费（会休眠，首次访问需等待 30 秒唤醒）
- **PostgreSQL**: 免费（5 MB 存储，仅限测试）
- **建议**: 生产环境使用付费层

---

## 推荐方案

| 需求 | 推荐平台 | 理由 |
|------|----------|------|
| 快速上线 | Railway | 部署简单，日志清晰 |
| 长期稳定 | Railway Pro | $5/月起，不休眠 |
| 免费测试 | Render | 免费层够用，但有休眠 |
| 生产环境 | Railway + PostgreSQL | 稳定可靠，自动备份 |

**建议**：先用 Railway 免费层测试，确认稳定后再升级到 Pro 计划。
