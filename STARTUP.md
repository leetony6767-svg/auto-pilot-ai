# MVP Agent OS — 啟動說明

## 快速開始（3 分鐘）

### 1. 安裝依賴
```bash
cd mvp-agent-os
pip install -r requirements.txt
```

### 2. 配置環境變量
```bash
cp .env.example .env
# 編輯 .env，至少填入 OPENROUTER_API_KEY
```

### 3. 運行乾跑模式（無需真實 API Key）
```bash
python start.py dry-run
```

### 4. 啟動 API 服務器
```bash
python start.py serve
# 訪問 http://localhost:8000/docs 查看 API 文檔
```

### 5. 運行測試
```bash
python start.py test
```

---

## 核心架構說明

### 專案結構
```
mvp-agent-os/
├── agents/
│   ├── base.py              # Agent 基類、權限模型、狀態定義
│   ├── planner_agent.py     # CEO Agent：商業計劃生成
│   ├── code_agent.py        # 技術 Agent：代碼生成 + 部署
│   ├── marketing_agent.py   # 營銷 Agent：社媒內容生成
│   ├── outreach_agent.py    # 獲客 Agent：開發郵件生成
│   ├── orchestrator.py      # 總指揮：工作流協調
│   └── graph.py             # LangGraph 狀態圖編排
├── config/
│   ├── settings.py          # 配置管理（模型路由、API Keys）
│   └── cost_control.py      # 成本控制（從 Polsia $120萬教訓學習）
├── templates/
│   └── content_templates.py # 社媒內容模板庫
├── tests/                   # 單元測試
├── app.py                   # FastAPI 後端
├── cli.py                   # CLI 工具
├── start.py                 # 啟動腳本
└── requirements.txt
```

### 四 Agent 協作流程

```
用戶輸入商業構想
       │
       ▼
┌─────────────────┐
│ Planner Agent   │  ← 生成商業執行計劃
│ (CEO/規劃)       │     使用 Claude Sonnet（強推理）
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌───────┐ ┌───────┐    ┌───────┐
│Code   │ │Market │    │Outreach│
│Agent  │ │Agent  │    │Agent  │
│(技術) │ │(營銷) │    │(獲客) │
└───┬───┘ └───┬───┘    └───┬───┘
    │         │            │
    └─────────┴────────────┘
              │
              ▼
      ┌───────────────┐
      │ 人工審批節點   │  ← 所有對外操作需確認
      │ (Dashboard)   │
      └───────┬───────┘
              │
              ▼
        部署 / 發送 / 發布
```

### 成本控制策略（關鍵！）

基於 Polsia 從 $120萬/月降至 $10萬/月的經驗：

| 策略 | 實現 |
|-----|------|
| **模型分級路由** | 簡單任務 → DeepSeek/Haiku，複雜推理 → Claude Sonnet |
| **Token 預算限制** | 每 Agent 每任務 ≤8,000 tokens，每用戶每日 ≤500K |
| **上下文裁剪** | 只保留最近 10 條對話，避免 Token 浪費 |
| **成本追蹤** | 每個 Agent 的每次調用都記錄 Token 消耗 |

---

## API 端點

| 方法 | 路徑 | 說明 |
|-----|------|------|
| `GET` | `/` | 服務信息 |
| `POST` | `/api/run` | 啟動工作流 |
| `GET` | `/api/status/{user_id}` | 查詢狀態 |
| `POST` | `/api/approve` | 處理審批 |
| `WS` | `/ws/{user_id}` | 實時推送 |
| `GET` | `/api/cost-summary` | 成本統計 |

### 請求示例

```bash
# 乾跑模式
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "business_idea": "一個幫助自由職業者自動管理客戶和發票的 AI SaaS",
    "dry_run": true
  }'

# 完整模式（需配置真實 API Keys）
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "business_idea": "一個幫助自由職業者自動管理客戶和發票的 AI SaaS",
    "dry_run": false
  }'
```

---

## 測試

```bash
# 運行所有測試
python -m pytest tests/ -v

# 帶覆盖率報告
python -m pytest tests/ -v --cov=agents --cov=config --cov-report=html
```

---

## 與 Polsia 的對照

| Polsia 特性 | MVP 實現 | 差距 |
|------------|---------|------|
| 9 Agent 協同 | 4 核心 Agent + 1 總指揮 | 缺少財務/人力/競爭分析 Agent |
| 跨公司學習知識庫 | 本地 ChromaDB | 無跨用戶數據共享 |
| Stripe 收入分成 | 佔位接口 | 未接入真實支付 |
| Meta Ads 投放 | 佔位接口 | 未接入真實廣告 API |
| 自建 GPU + 開源模型 | OpenRouter 聚合 | 未自建 GPU |
| Vercel 自動部署 | 乾跑模式模擬 | 未接入真實部署 API |

---

## 下一步擴展

1. **接入真實 Vercel API** — 實現自動部署
2. **集成 Stripe Connect** — 實現收入分成追蹤
3. **添加 Mem0** — 實現跨會話記憶
4. **構建 Next.js Dashboard** — 視覺化工作流和審批
5. **多用戶隔離** — PostgreSQL 持久化存儲
6. **添加更多 Agent** — 財務、人力、競爭分析

---

*基於 [Polsia 逆向分析報告](../polsia-reverse-engineering-v2.md)*
