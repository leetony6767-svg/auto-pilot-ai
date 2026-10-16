"""
FastAPI 後端服務 — Agent OS 的 API 入口

提供 REST API 供前端 Dashboard 調用，同時支持 WebSocket 實時狀態推送
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json
from datetime import datetime
from pathlib import Path

from agents.base import BusinessState
from agents.graph import workflow_graph
from agents.orchestrator import OrchestratorAgent
from config.settings import settings

app = FastAPI(
    title="MVP Agent OS",
    description="基於 Polsia 逆向分析的最小可行 AI Agent 營運系統",
    version="0.1.0",
)

# 靜態文件服務
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def root():
    """返回前端 Dashboard"""
    return FileResponse(str(STATIC_DIR / "index.html"))


# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 活跃的 WebSocket 連接
active_connections: List[WebSocket] = []


# ── API 數據模型 ────────────────────────────────────────────────
class BusinessInput(BaseModel):
    user_id: str
    business_idea: str
    dry_run: bool = False  # 乾跑模式：只生成草稿，不實際部署/發送


class ApprovalAction(BaseModel):
    approval_id: str
    approved: bool
    comment: str = ""


class WorkflowStatus(BaseModel):
    status: str
    metrics: dict
    pending_approvals: int
    audit_log_length: int


# ── WebSocket 實時推送 ──────────────────────────────────────────
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)


async def broadcast(state: BusinessState):
    """向所有連接的客戶端廣播狀態更新"""
    message = json.dumps({
        "user_id": state["user_id"],
        "timestamp": datetime.now().isoformat(),
        "pending_approvals": len(state.get("pending_approval", [])),
        "audit_entries": len(state.get("audit_log", [])),
    })
    for connection in active_connections[:]:
        if connection.client.host:
            try:
                await connection.send_text(message)
            except:
                if connection in active_connections:
                    active_connections.remove(connection)


# ── API 端點 ────────────────────────────────────────────────────
@app.get("/api/info")
async def root():
    return {
        "service": "MVP Agent OS",
        "version": "0.1.0",
        "description": "AI 在你睡覺時替你運營公司的最小可行原型",
        "endpoints": {
            "POST /api/run": "啟動自動化工作流",
            "GET /api/status/{user_id}": "查詢工作流狀態",
            "POST /api/approve": "處理人工審批",
            "GET /api/approvals/{user_id}": "獲取待審批列表",
            "WS /ws/{user_id}": "實時狀態推送",
            "GET /api/cost-summary": "獲取成本統計",
        }
    }


@app.post("/api/run", response_model=WorkflowStatus)
async def run_workflow(input_data: BusinessInput):
    """
    啟動自動化工作流

    流程：
    1. 初始化 BusinessState
    2. 通過 LangGraph 圖執行完整工作流
    3. 返回狀態摘要
    """
    initial_state: BusinessState = {
        "user_id": input_data.user_id,
        "business_idea": input_data.business_idea,
        "business_plan": {},
        "landing_page_code": "",
        "deployment_url": "",
        "content_queue": [],
        "outreach_emails": [],
        "leads": [],
        "pending_approval": [],
        "approved_items": [],
        "audit_log": [],
        "metrics": {},
    }

    try:
        if input_data.dry_run:
            result = await _dry_run_workflow(initial_state)
        else:
            result = await workflow_graph.ainvoke(initial_state)

        await broadcast(result)

        return WorkflowStatus(
            status=result["metrics"].get("workflow_status", "unknown"),
            metrics=result.get("metrics", {}),
            pending_approvals=len(result.get("pending_approval", [])),
            audit_log_length=len(result.get("audit_log", [])),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status/{user_id}")
async def get_workflow_status(user_id: str):
    """查詢指定用戶的工作流狀態（需接入持久化存儲）"""
    return {
        "user_id": user_id,
        "status": "not_found",
        "message": "狀態查詢接口（需接入 PostgreSQL 持久化存儲）"
    }


@app.post("/api/approve")
async def handle_approval(action: ApprovalAction):
    """處理人工審批決策"""
    return {
        "approval_id": action.approval_id,
        "approved": action.approved,
        "comment": action.comment,
        "processed_at": datetime.now().isoformat(),
    }


@app.get("/api/approvals/{user_id}")
async def get_pending_approvals(user_id: str):
    """獲取指定用戶的待審批列表（需接入持久化存儲）"""
    return {
        "user_id": user_id,
        "approvals": [],
        "message": "審批列表接口（需接入 PostgreSQL 持久化存儲）"
    }


@app.get("/api/cost-summary")
async def get_cost_summary():
    """獲取成本統計（從 cost_control 模塊讀取）"""
    from config.cost_control import budget, cost_tracker

    return {
        "agent_usage": dict(list(budget.agent_usage.items())[-5:]),
        "user_usage_sample": dict(list(budget.user_usage.items())[-3:]),
        "global_daily_usage": budget.global_daily_usage,
        "global_daily_limit": budget.global_daily,
        "usage_percentage": round(
            (budget.global_daily_usage / budget.global_daily) * 100, 2
        ) if budget.global_daily > 0 else 0,
        "estimated_cost_usd": round(
            cost_tracker.estimate_cost(budget.global_daily_usage, "deepseek-chat"), 4
        ),
    }


@app.get("/api/ideas")
async def get_business_ideas(count: int = 3, category: Optional[str] = None):
    """
    發現並推薦商業構想

    參數：
    - count: 推薦數量（1-6），默認 3
    - category: 可選分類篩選（如 "FinTech", "Media", "B2B"）
    """
    from agents.idea_discovery_agent import IdeaDiscoveryAgent

    agent = IdeaDiscoveryAgent()
    ideas = await agent.discover_ideas(count=count, category=category)
    stats = agent.get_stats()

    return {
        "ideas": ideas,
        "stats": stats,
        "total_available": stats["total_ideas_available"],
        "categories": stats["categories"],
    }


# ── AI 獵客引擎端點 ─────────────────────────────────────────────
class HuntRequest(BaseModel):
    keywords: List[str]
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    min_score: int = 60
    max_results: int = 50


@app.post("/api/hunt")
async def search_leads(request: HuntRequest):
    """
    AI 獵客引擎 — 搜索高價值线索

    從多個數據源聚合目標客戶信息，並進行智能評分
    """
    from agents.hunter_engine import AIHunterEngine, SearchQuery

    engine = AIHunterEngine()
    query = SearchQuery(
        keywords=request.keywords,
        industry=request.industry,
        company_size=request.company_size,
        location=request.location,
        min_score=request.min_score,
        max_results=request.max_results,
    )

    leads = await engine.search_leads(query)
    stats = engine.get_stats()

    return {
        "leads": [
            {
                "id": l.id,
                "name": l.name,
                "company": l.company,
                "title": l.title,
                "email": l.email,
                "industry": l.industry,
                "source": l.source,
                "score": l.score,
                "match_reason": l.match_reason,
            }
            for l in leads
        ],
        "stats": stats,
        "total_found": len(leads),
    }


@app.get("/api/hunt/stats")
async def get_hunt_stats():
    """獲取 AI 獵客引擎統計信息"""
    from agents.hunter_engine import AIHunterEngine

    engine = AIHunterEngine()
    return engine.get_stats()


@app.get("/api/hunt/export")
async def export_leads(format: str = "json"):
    """導出已搜索的线索數據"""
    from agents.hunter_engine import AIHunterEngine

    engine = AIHunterEngine()
    data = engine.export_leads(format=format)
    return {"format": format, "data": data}


# ── 逆向分析模組端點 ────────────────────────────────────────────
@app.post("/api/reverse/analyze")
async def analyze_target(url: str, depth: int = 1):
    """
    逆向分析指定網站

    識別技術棧、API 端點、商業模式、SEO、安全等
    """
    from agents.reverse_module import ReverseAnalysisModule

    module = ReverseAnalysisModule()
    result = await module.analyze_url(url, depth=depth)

    return {
        "target_url": result.target_url,
        "analyzed_at": result.analyzed_at,
        "confidence_score": result.confidence_score,
        "tech_stack": result.tech_stack,
        "api_endpoints": result.api_endpoints,
        "business_model": result.business_model,
        "seo_analysis": result.seo_analysis,
        "security_analysis": result.security_analysis,
        "performance_metrics": result.performance_metrics,
        "recommendations": result.recommendations,
    }


@app.get("/api/reverse/history")
async def get_reverse_history(limit: int = 10):
    """獲取逆向分析歷史記錄"""
    from agents.reverse_module import ReverseAnalysisModule

    module = ReverseAnalysisModule()
    history = module.get_history(limit=limit)
    stats = module.get_stats()

    return {"history": history, "stats": stats}


# ── 訂閱價格與收款資訊端點 ────────────────────────────────────────
@app.get("/api/pricing")
async def get_pricing():
    """獲取訂閱價格資訊（雙幣別）"""
    from config.settings import settings

    return {
        "currency": settings.currency,
        "prices": {
            "twd": {
                "currency": "TWD",
                "symbol": "NT$",
                "monthly": settings.price_twd_monthly,
                "yearly": settings.price_twd_yearly,
                "save_percentage": round((1 - settings.price_twd_yearly / (settings.price_twd_monthly * 12)) * 100, 1),
            },
            "usd": {
                "currency": "USD",
                "symbol": "$",
                "monthly": settings.price_usd_monthly,
                "yearly": settings.price_usd_yearly,
                "save_percentage": round((1 - settings.price_usd_yearly / (settings.price_usd_monthly * 12)) * 100, 1),
            },
        },
        "exchange_rate": settings.exchange_rate_twd_usd,
    }


@app.get("/api/bank-account")
async def get_bank_account():
    """獲取收款銀行帳戶資訊"""
    from config.settings import settings

    return {
        "bank_name": settings.bank_name,
        "bank_code": settings.bank_code,
        "account_number": settings.account_number,
        "account_name": settings.account_name,
    }


@app.get("/api/crypto-payment")
async def get_crypto_payment():
    """獲取加密貨幣收款資訊（OKX USDT）"""
    from config.settings import settings

    return {
        "supported": settings.usdt_supported,
        "currency": "USDT",
        "networks": settings.usdt_networks,
        "wallets": {
            "TRC20": settings.usdt_wallet_address,
            "Polygon": settings.usdt_wallet_polygon,
        },
        "price_monthly": settings.usdt_price_monthly,
        "price_yearly": settings.price_usd_yearly,
        "payment_note": settings.usdt_payment_note,
        "supported_exchanges": ["OKX", "Binance", "Bybit", "KuCoin"],
    }


# ── 內部輔助函數 ────────────────────────────────────────────────
async def _dry_run_workflow(state: BusinessState) -> BusinessState:
    """
    乾跑模式：只執行規劃和生成，跳過實際部署和發送
    用於快速驗證邏輯，不產生外部影響
    """
    from agents.planner_agent import PlannerAgent
    from agents.code_agent import CodeAgent
    from agents.marketing_agent import MarketingAgent
    from agents.outreach_agent import OutreachAgent

    # Phase 1: 規劃
    planner = PlannerAgent(state)
    plan_result = await planner.run()
    state.update(plan_result)

    if "error" in plan_result:
        state["metrics"] = {"workflow_status": "error", "error": plan_result["error"]}
        return state

    # Phase 2: 建站（生成代碼但不部署）
    coder = CodeAgent(state)
    code_result = await coder.run()
    if code_result.get("code_generated"):
        state["landing_page_code"] = "generated (dry-run)"
    state["deployment_url"] = "dry-run: not deployed"

    # Phase 3: 內容
    marketer = MarketingAgent(state)
    marketing_result = await marketer.run()
    state.update(marketing_result)

    # Phase 4: 獲客
    outreach = OutreachAgent(state)
    outreach_result = await outreach.run()
    state.update(outreach_result)

    # 完成報告
    total_tokens = sum(e.get("tokens", 0) for e in state["audit_log"])
    state["metrics"] = {
        "workflow_status": "dry_run_completed",
        "completed_at": datetime.now().isoformat(),
        "pending_approvals": len(state["pending_approval"]),
        "total_tokens_used": total_tokens,
        "note": "乾跑模式：所有輸出均已進入審批隊列，未實際部署或發送",
    }

    await broadcast(state)
    return state
