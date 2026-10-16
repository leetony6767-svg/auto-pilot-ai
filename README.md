# MVP Agent OS

> 基於 Polsia 逆向分析的最小可行 AI Agent 營運系統原型
> 「AI 在你睡覺時替你運營公司」—— 但這次是你能控制的原型

## 快速開始

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 配置環境變量
cp .env.example .env
# 編輯 .env，填入你的 API Key

# 3. 運行乾跑模式（測試核心邏輯）
python start.py dry-run

# 4. 啟動 API 服務器
python start.py serve
# 訪問 http://localhost:8000/docs 查看 API 文檔
```

## 專案結構

```
mvp-agent-os/
├── agents/                 # Agent 模組
│   ├── __init__.py
│   ├── base.py            # Agent 基類與狀態定義
│   ├── planner_agent.py   # CEO/規劃 Agent
│   ├── code_agent.py      # 技術 Agent（代碼生成 + 部署）
│   ├── marketing_agent.py # 營銷 Agent（社媒內容）
│   ├── outreach_agent.py  # 獲客 Agent（開發郵件）
│   └── orchestrator.py    # 總指揮 Agent
├── config/
│   ├── __init__.py
│   ├── settings.py        # 配置管理
│   └── cost_control.py    # 成本控制策略
├── storage/               # 數據存儲（ChromaDB 等）
├── templates/             # 內容模板
├── tests/                 # 測試套件
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_cost_control.py
│   └── test_workflow.py
├── app.py                 # FastAPI 後端
├── cli.py                 # 命令行入口
├── start.py               # 啟動腳本
├── requirements.txt       # Python 依賴
└── .env.example           # 環境變量模板
```

## 核心設計原則

### 1. 成本控制（從 Polsia $120萬帳單危機學習）
- **模型分級路由**：簡單任務用小模型，複雜推理用大模型
- **Token 預算限制**：每 Agent 每任務、每用戶每日、全局每日三層預算
- **上下文裁剪**：只保留最近 10 條對話，避免 Token 浪費

### 2. 安全審批機制
- **三級權限模型**：L1 只讀 → L2 執行 → L3 外部影響（需人工審批）
- **所有對外操作**（發郵件、發布社媒、部署代碼）均經過審批節點
- **完整審計日誌**：每個 Agent 的每次調用都有記錄

### 3. LangGraph 狀態圖編排
- 將整個工作流建模為有向圖
- 支持條件路由（根據任務類型分發）
- 支持循環回退（審批不通過時重新生成）

## API 端點

| 方法 | 路徑 | 說明 |
|-----|------|------|
| GET | `/` | 服務信息 |
| POST | `/api/run` | 啟動自動化工作流 |
| GET | `/api/status/{user_id}` | 查詢工作流狀態 |
| POST | `/api/approve` | 處理人工審批 |
| GET | `/api/approvals/{user_id}` | 獲取待審批列表 |
| GET | `/api/cost-summary` | 獲取成本統計 |
| WS | `/ws/{user_id}` | 實時狀態推送 |

## 測試

```bash
# 運行所有測試
python -m pytest tests/ -v

# 運行特定測試
python -m pytest tests/test_cost_control.py -v
```

## 與 Polsia 的對照

| Polsia 特性 | MVP 實現 |
|------------|---------|
| 9 Agent 協同 | 4 核心 Agent + 1 總指揮 |
| AWS Bedrock → 自建 GPU | OpenRouter 聚合多模型 |
| 跨公司學習知識庫 | 本地 ChromaDB + Mem0 |
| Stripe 收入分成追蹤 | Stripe API 集成佔位 |
| Meta Ads 自動投放 | Twitter/LinkedIn API 集成佔位 |
| $50/月訂閱 + 20% 抽成 | MVP 免費，架構預留付費接口 |

## 下一步

- [ ] 接入真實 Vercel API 實現自動部署
- [ ] 集成 Stripe Connect 實現收入分成追蹤
- [ ] 添加 Mem0 實現跨會話記憶
- [ ] 構建 Next.js Dashboard 前端
- [ ] 添加多用戶隔離和數據庫持久化

## 許可證

MIT — 自由使用、修改和分發

---
*基於 [Polsia 逆向分析報告](../polsia-reverse-engineering-v2.md)*
