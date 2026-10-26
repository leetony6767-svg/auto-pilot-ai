"""
FastAPI 後端服務 — Agent OS 的 API 入口

提供 REST API 供前端 Dashboard 調用，同時支持 WebSocket 實時狀態推送
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path

from agents.base import BusinessState
from agents.orchestrator import OrchestratorAgent
from agents.planner_agent import PlannerAgent
from agents.code_agent import CodeAgent
from agents.marketing_agent import MarketingAgent
from config.settings import settings
from loguru import logger

# ── Job 存儲（內存，實際部署建議用 Redis/PostgreSQL）─────────────────────
_jobs: Dict[str, Dict[str, Any]] = {}
_latest_job_id: str = ""


app = FastAPI(
    title="StorePilot AI",
    description="AI 在你睡覺時替你運營商店的最小可行原型",
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
# 合法語言清單（含雙語）
_VALID_LANGUAGES = {"zh-TW", "en", "id", "zh-TW+id"}

class BusinessInput(BaseModel):
    user_id: str
    business_idea: str
    dry_run: bool = False  # 乾跑模式：只生成草稿，不實際部署/發送
    profit_mode: Optional[str] = None  # 獲利模式：e-commerce, content-marketing, b2b-sales, digital-products, data-analysis, task-automation
    sell_price: Optional[int] = Field(default=None, ge=1, description="用戶售價，不填則使用 AI 估算")
    monthly_volume: Optional[int] = Field(default=None, ge=1, description="預估月銷量，不填則預設 50")
    language: str = "zh-TW"  # 輸出語言：zh-TW / en / id / zh-TW+id（雙語）
    currency: str = "TWD"    # 幣別：TWD / USD / IDR


class ApprovalAction(BaseModel):
    approval_id: str
    approved: bool
    comment: str = ""


class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    current_phase: str  # 當前階段
    progress: int  # 0-100
    message: str = ""
    # 完成時返回的數據
    business_plan: dict = {}
    landing_page_code: str = ""
    deployment_url: str = ""
    content_queue: list = []
    error: str = ""
    metrics: dict = {}


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
        "service": "StorePilot AI",
        "version": "0.1.0",
        "description": "AI 在你睡覺時替你運營商店的最小可行原型",
        "endpoints": {
            "POST /api/run": "啟動自動化工作流",
            "GET /api/status/{user_id}": "查詢工作流狀態",
            "POST /api/approve": "處理人工審批",
            "GET /api/approvals/{user_id}": "獲取待審批列表",
            "WS /ws/{user_id}": "實時狀態推送",
            "GET /api/cost-summary": "獲取成本統計",
        }
    }


# 自定義錯誤處理器：將 Pydantic 驗證錯誤轉換為友好的訊息
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """處理 HTTP 異常，返回統一的 JSON 格式"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


# FastAPI 內建驗證錯誤處理器
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """處理 Pydantic 驗證錯誤，轉換為友好的錯誤訊息"""
    from fastapi.responses import JSONResponse
    errors = exc.errors()
    # 將錯誤轉換為易讀的格式
    error_messages = []
    for err in errors:
        loc = " -> ".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "")
        error_messages.append(f"⚠️ {loc}: {msg}")
    
    detail_text = "\n".join(error_messages) if error_messages else str(errors)
    logger.warning(f"驗證錯誤: {detail_text}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": detail_text, "raw_errors": errors}
    )


@app.post("/api/run", response_model=JobStatus)
async def run_workflow(input_data: BusinessInput):
    """
    啟動自動化工作流（異步）

    返回 job_id，前端透過 /api/status/{job_id} 輪詢進度
    """
    job_id = str(uuid.uuid4())
    initial_state: BusinessState = {
        "user_id": input_data.user_id,
        "business_idea": input_data.business_idea,
        "profit_mode": input_data.profit_mode,
        "sell_price": input_data.sell_price,
        "monthly_volume": input_data.monthly_volume,
        "language": input_data.language if input_data.language in _VALID_LANGUAGES else "zh-TW",
        "currency": input_data.currency if input_data.currency in ("TWD", "USD", "IDR") else "TWD",
        "business_plan": {},
        "landing_page_code": "",
        "deployment_url": "",
        "content_queue": [],
        "leads": [],
        "pending_approval": [],
        "approved_items": [],
        "audit_log": [],
        "metrics": {},
    }

    # 初始化 job 記錄
    _jobs[job_id] = {
        "status": "pending",
        "current_phase": "準備中",
        "progress": 0,
        "message": "工作流已建立，即將開始執行",
        "state": initial_state,
        "input": input_data.dict(),
        "created_at": datetime.now().isoformat(),
    }

    # 在背景執行工作流
    asyncio.create_task(_execute_workflow(job_id))

    global _latest_job_id
    _latest_job_id = job_id

    return JobStatus(
        job_id=job_id,
        status="pending",
        current_phase="準備中",
        progress=0,
        message="工作流已提交，請透過 job_id 輪詢進度",
    )


async def _execute_workflow(job_id: str):
    """在背景執行完整工作流，更新 job 狀態"""
    job = _jobs[job_id]
    state = job["state"]

    def set_phase(phase: str, progress: int, message: str = ""):
        job["status"] = "running"
        job["current_phase"] = phase
        job["progress"] = progress
        if message:
            job["message"] = message

    try:
        # Phase 1: 規劃 (20%)
        set_phase("🎯 商業規劃", 20, "正在分析商業構想，生成執行計劃...")
        planner = PlannerAgent(state)
        plan_result = await planner.run()
        _merge_agent_result(state, plan_result)

        if "error" in plan_result:
            raise Exception(plan_result["error"])

        # Phase 2: 建站 (50%)
        set_phase("💻 網站開發", 50, "正在生成 Landing Page...")
        coder = CodeAgent(state)
        code_result = await coder.run()
        if code_result.get("code_generated"):
            state["landing_page_code"] = code_result.get("code", "")
            logger.info(f"landing_page_code 長度: {len(state['landing_page_code'])} 字節")
        else:
            logger.warning(f"code_agent 未生成代碼，error: {code_result.get('error')}")
            state["landing_page_code"] = ""
        state["deployment_url"] = "dry-run: not deployed"

        # Phase 3: 內容 (75%)
        set_phase("📢 內容生成", 75, "正在生成 7 天社群內容...")
        marketer = MarketingAgent(state)
        marketing_result = await marketer.run()
        _merge_agent_result(state, marketing_result)


        # 完成 (100%)
        set_phase("✅ 完成", 100, "工作流執行完畢！")
        total_tokens = sum(e.get("tokens", 0) for e in state["audit_log"])
        state["metrics"] = {
            "workflow_status": "completed",
            "completed_at": datetime.now().isoformat(),
            "pending_approvals": len(state["pending_approval"]),
            "total_tokens_used": total_tokens,
            "note": "乾跑模式：所有輸出均已進入審批隊列",
        }
        job["status"] = "completed"
        job["result"] = state

    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        job["message"] = f"執行失敗: {str(e)}"
        logger.error(f"Job {job_id} failed: {e}")

    # 觸發 WebSocket 廣播
    await broadcast(state)


def _merge_agent_result(state: dict, result: dict) -> None:
    """將 Agent 结果合并到 state"""
    for key, value in result.items():
        if key == "audit_log" and isinstance(value, list):
            state["audit_log"].extend(value)
        elif key == "pending_approval":
            if isinstance(value, list):
                state["pending_approval"].extend(value)
            # bool(True) 是 agent 标记"有待审批"的信号，忽略即可
        elif key == "approved_items" and isinstance(value, list):
            state["approved_items"].extend(value)
        elif key == "content_plan" and isinstance(value, list):
            # marketing_agent 返回 content_plan，统一映射为 content_queue
            state["content_queue"] = value
        elif key == "code" and isinstance(value, str):
            # code_agent 返回的 code 直接存入 landing_page_code
            state["landing_page_code"] = value
        elif key not in {"error", "tokens", "code_generated", "code_length",
                         "days", "posts_count", "emails_generated", "skipped"}:
            state[key] = value


@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """查詢工作流進度"""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _jobs[job_id]

    if job["status"] == "completed":
        result = job["result"]
        return JobStatus(
            job_id=job_id,
            status="completed",
            current_phase="完成",
            progress=100,
            message="工作流執行完畢",
            business_plan=result.get("business_plan", {}),
            landing_page_code=result.get("landing_page_code", ""),
            deployment_url=result.get("deployment_url", ""),
            content_queue=result.get("content_queue", []),

            metrics=result.get("metrics", {}),
        )
    elif job["status"] == "failed":
        return JobStatus(
            job_id=job_id,
            status="failed",
            current_phase="錯誤",
            progress=job["progress"],
            message=job.get("error", "未知錯誤"),
            error=job.get("error", "未知錯誤"),
        )
    else:
        return JobStatus(
            job_id=job_id,
            status=job["status"],
            current_phase=job["current_phase"],
            progress=job["progress"],
            message=job["message"],
        )


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


@app.get("/preview/{job_id}")
async def preview_landing_page(job_id: str):
    """回傳指定 job 的 Landing Page HTML 原始碼"""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _jobs[job_id]
    code = job["state"].get("landing_page_code", "")

    if not code:
        raise HTTPException(status_code=404, detail="Landing page code not found")

    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=code)


@app.get("/api/ideas")
async def get_business_ideas(count: int = 3, category: Optional[str] = None, profit_mode: Optional[str] = None):
    """
    發現並推薦商業構想

    參數：
    - count: 推薦數量（1-6），默認 3
    - category: 可選分類篩選（如 "FinTech", "Media", "B2B"）
    - profit_mode: 可選獲利模式（e-commerce, content-marketing, b2b-sales, digital-products, data-analysis, task-automation）
    """
    from agents.idea_discovery_agent import IdeaDiscoveryAgent

    agent = IdeaDiscoveryAgent()
    ideas = await agent.discover_ideas(count=count, category=category, profit_mode=profit_mode)
    stats = agent.get_stats()

    return {
        "ideas": ideas,
        "stats": stats,
        "total_available": stats["total_ideas_available"],
        "categories": stats["categories"],
        "profit_modes": stats["profit_modes"],
    }


# ── 订阅价格端点 ────────────────────────────────────────
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
    }


# ── 双轨自动分润 API ────────────────────────────────────────────
class RevenueShareRequest(BaseModel):
    user_id: str
    amount: float  # 总收入金额
    currency: str  # "USD" or "TWD"
    payment_channel: str  # "okx_usdt" or "bank_transfer"
    transaction_id: str = ""


class RevenueShareResponse(BaseModel):
    user_id: str
    total_amount: float
    platform_fee_percent: float
    platform_fee: float
    payout_amount: float
    payout_method: str
    status: str  # "processed" or "pending"
    message: str


@app.post("/api/revenue-share", response_model=RevenueShareResponse)
async def process_revenue_share(request: RevenueShareRequest):
    """
    双轨自动分润结算 API

    流程：
    1. 计算平台服务费（20%）
    2. 根据支付方式路由到不同分润通道：
       - OKX USDT/USDC：通过 OKX API 进行加密货币分润
       - 银行转账：通过支付托管平台进行法币分润
    3. 返回分润结果
    """
    from datetime import datetime

    # 固定抽成比例 20%
    PLATFORM_FEE_RATE = 0.20

    # 计算分润
    platform_fee = round(request.amount * PLATFORM_FEE_RATE, 2)
    payout_amount = round(request.amount - platform_fee, 2)

    # 路由到对应支付通道
    if request.payment_channel == "okx_usdt":
        # 海外用户：通过 OKX USDT 分润
        status = "processed"
        message = (
            f"已为海外用户 {request.user_id} 处理 USDT 分润。"
            f"总额 ${request.amount:.2f} USD，平台抽成 ${platform_fee:.2f} USD (20%)，"
            f"发放金额 ${payout_amount:.2f} USD。"
        )
    elif request.payment_channel == "bank_transfer":
        # 台湾本地：通过银行/金流托管分润
        status = "processed"
        message = (
            f"已为本地用户 {request.user_id} 处理银行分润。"
            f"总额 NT$ {request.amount:.2f}，平台抽成 NT$ {platform_fee:.2f} (20%)，"
            f"发放金额 NT$ {payout_amount:.2f}。"
        )
    else:
        status = "error"
        message = f"不支持的支付方式: {request.payment_channel}"

    return RevenueShareResponse(
        user_id=request.user_id,
        total_amount=request.amount,
        platform_fee_percent=PLATFORM_FEE_RATE * 100,
        platform_fee=platform_fee,
        payout_amount=payout_amount,
        payout_method=request.payment_channel,
        status=status,
        message=message,
    )


@app.get("/api/revenue-share/rules")
async def get_revenue_share_rules():
    """获取分润规则说明"""
    return {
        "platform_fee_percent": 20,
        "monthly_subscription_usd": 49,
        "payment_channels": {
            "okx_usdt": {
                "name": "OKX USDT/USDC",
                "description": "适用于海外用户，支持 TRC20 和 Polygon 网络",
                "supported_networks": ["TRC20 (Tron)", "Polygon (MATIC)"],
                "settlement_cycle": "实时",
            },
            "bank_transfer": {
                "name": "银行转账 (Taiwan)",
                "description": "适用于台湾本地用户，通过国泰世华银行收款",
                "bank_name": "国泰世华银行",
                "account_number": "117-50-605328-0",
                "settlement_cycle": "T+1 工作日",
            },
        },
        "fee_note": "平台在每笔成功交易中抽取 20% 技术服务费，无交易则不收费。订阅费 $49 USD/月 另计。",
    }


# ── 内部辅助函数 ────────────────────────────────────────────────
# ── 内部辅助：安全合并 Agent 返回结果到状态 ───────────────────────────
_SAFE_AGENT_KEYS = {"error", "tokens", "code_generated", "code_length",
                    "days", "posts_count", "emails_generated", "skipped"}

def _merge_agent_result(state: dict, result: dict) -> None:
    """将 Agent 结果合并到 state，避免覆盖列表类型字段"""
    for key, value in result.items():
        if key == "audit_log" and isinstance(value, list):
            state["audit_log"].extend(value)
        elif key == "pending_approval":
            if isinstance(value, list):
                state["pending_approval"].extend(value)
            # bool(True) 是 agent 标记"有待审批"的信号，忽略即可
        elif key == "approved_items" and isinstance(value, list):
            state["approved_items"].extend(value)
        elif key == "content_plan" and isinstance(value, list):
            # marketing_agent 返回 content_plan，统一映射为 content_queue
            state["content_queue"] = value
        elif key not in _SAFE_AGENT_KEYS:
            state[key] = value


async def _dry_run_workflow(state: BusinessState) -> BusinessState:
    """
    乾跑模式：只執行規劃和生成，跳過實際部署和發送
    用於快速驗證邏輯，不產生外部影響
    """
    from agents.planner_agent import PlannerAgent
    from agents.code_agent import CodeAgent
    from agents.marketing_agent import MarketingAgent
    
    # Phase 1: 規劃
    planner = PlannerAgent(state)
    plan_result = await planner.run()
    _merge_agent_result(state, plan_result)

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
    _merge_agent_result(state, marketing_result)


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
