"""Agent 基礎類與狀態定義"""
from abc import ABC, abstractmethod
from typing import TypedDict, Annotated, Literal, Optional
import operator
from datetime import datetime


# ── 權限級別 ────────────────────────────────────────────────────
class PermissionLevel(str):
    READ = "read"          # 只讀：查知識庫、讀數據
    EXECUTE = "execute"    # 執行：寫內部記錄、生成草稿
    EXTERNAL = "external"  # 外部影響：發郵件、調支付（需人工審批）


# ── 業務狀態定義（LangGraph State）──────────────────────────────
class BusinessState(TypedDict):
    # 輸入
    user_id: str
    business_idea: str

    # 中間產物
    business_plan: dict
    landing_page_code: str
    deployment_url: str
    content_queue: list[dict]
    outreach_emails: list[dict]
    leads: list[dict]

    # 人工審批隊列
    pending_approval: Annotated[list[dict], operator.add]

    # 審批結果
    approved_items: Annotated[list[dict], operator.add]

    # 審計日誌
    audit_log: Annotated[list[dict], operator.add]

    # 輸出指標
    metrics: dict


# ── Agent 基類 ──────────────────────────────────────────────────
class BaseAgent(ABC):
    """所有 Agent 的基礎類"""

    name: str = "base_agent"
    permission_level: PermissionLevel = PermissionLevel.READ
    cost_model: str = "deepseek-chat"  # 默認使用低成本模型

    def __init__(self, state: BusinessState):
        self.state = state
        self.audit_entry: dict = {
            "agent": self.name,
            "model": self.cost_model,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "tokens": 0,
            "error": None,
        }

    @abstractmethod
    async def run(self) -> dict:
        """Agent 核心執行邏輯，返回狀態更新"""
        ...

    def log(self, **kwargs):
        """記錄審計日誌"""
        entry = {**self.audit_entry, **kwargs}
        self.state["audit_log"].append(entry)

    def add_approval(self, item_type: str, content: list | dict, reason: str = ""):
        """將內容加入審批隊列（L3 操作）"""
        self.state["pending_approval"].append({
            "type": item_type,
            "content": content,
            "reason": reason,
            "created_at": datetime.now().isoformat(),
        })

    def can_execute(self, action: str) -> bool:
        """檢查是否有权執行某操作"""
        from config.settings import settings
        if self.permission_level == PermissionLevel.READ:
            return action in ("read", "query", "generate_draft")
        if self.permission_level == PermissionLevel.EXECUTE:
            return action in ("write_internal", "send_draft", "generate_content")
        if self.permission_level == PermissionLevel.EXTERNAL:
            return action in settings.approval_required or False
        return False


# ── 測試用的具體 Agent 實現 ─────────────────────────────────────
class _TestAgent(BaseAgent):
    """用於測試 BaseAgent 的具體實現"""
    name = "test_agent"
    permission_level = PermissionLevel.READ

    async def run(self) -> dict:
        return {}


# ── 審批路由函數 ────────────────────────────────────────────────
def approval_router(state: BusinessState) -> str:
    """判斷是否有待審批內容"""
    if state["pending_approval"]:
        return "human_review"
    return "execute"


def route_by_task(task: str) -> str:
    """根據任務類型路由到對應 Agent"""
    routing_map = {
        "plan": "planner",
        "code": "coder",
        "content": "marketer",
        "outreach": "outreach",
        "analyze": "analyst",
    }
    return routing_map.get(task, "planner")
