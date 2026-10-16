"""
LangGraph 圖定義 — 完整的狀態機編排

將所有 Agent 組織成一個有向圖，支持：
- 條件路由（根據任務類型分發）
- 人工審批節點
- 循環回退（審批不通過時回到生成階段）
"""
from langgraph.graph import StateGraph, END
from typing import Literal

from agents.base import BusinessState
from agents.orchestrator import OrchestratorAgent


def build_workflow_graph() -> StateGraph:
    """構建完整的 LangGraph 工作流圖"""

    graph = StateGraph(BusinessState)

    # ── 註冊節點 ────────────────────────────────────────────────
    graph.add_node("orchestrator", async_orchestrator_node)
    graph.add_node("human_review", async_human_review_node)
    graph.add_node("execute", async_execute_node)
    graph.add_node("rework", async_rework_node)

    # ── 設定入口 ────────────────────────────────────────────────
    graph.set_entry_point("orchestrator")

    # ── 主流程邊 ────────────────────────────────────────────────
    # orchestrator 完成後，進入審批路由
    graph.add_conditional_edges(
        "orchestrator",
        check_approvals,  # 檢查是否有待審批項目
        {
            "has_pending": "human_review",   # 有待審批 → 進入人工審批
            "all_clear": "execute",           # 無待審批 → 直接完成
        }
    )

    # ── 審批節點 ────────────────────────────────────────────────
    graph.add_edge("human_review", "execute")

    # ── 執行節點 ────────────────────────────────────────────────
    # 實際部署/發送等操作（此處為佔位，真實實現需接入外部 API）
    graph.add_edge("execute", END)

    return graph


async def async_orchestrator_node(state: BusinessState) -> BusinessState:
    """ orchestrator 節點的 LangGraph 適配器 """
    orch = OrchestratorAgent(state)
    result = await orch.run()
    return result


async def async_human_review_node(state: BusinessState) -> BusinessState:
    """
    人工審批節點

    在真實系統中，這裡會：
    1. 暫停執行，等待 Webhook/回調
    2. 顯示 Dashboard 供用戶審批
    3. 審批後觸發後續流程

    此處為演示目的，模擬審批決策
    """
    pending = state.get("pending_approval", [])
    if not pending:
        return state

    # 模擬：自動審批第一項（實際應等待人工操作）
    for item in pending[:3]:  # 最多審批前 3 項
        item.setdefault("approved", True)
        item.setdefault("comment", "Demo auto-approval")

    # 將已審批項目移到 approved_items
    approved_ids = {id(item) for item in pending[:3]}
    state["approved_items"].extend([
        {**item, "approved": True, "approved_at": "demo"}
        for item in pending[:3]
    ])
    state["pending_approval"] = [
        item for item in pending if id(item) not in approved_ids
    ]

    return state


async def async_execute_node(state: BusinessState) -> BusinessState:
    """執行節點：處理已審批的動作"""
    approved = state.get("approved_items", [])
    state["metrics"] = state.get("metrics", {})
    state["metrics"]["executed_items"] = len(approved)
    return state


async def async_rework_node(state: BusinessState) -> BusinessState:
    """重做節點：審批不通過時返回重新生成"""
    state["metrics"] = state.get("metrics", {})
    state["metrics"]["rework_count"] = state["metrics"].get("rework_count", 0) + 1
    return state


def check_approvals(state: BusinessState) -> str:
    """條件路由：是否有待審批項目"""
    if state.get("pending_approval"):
        return "has_pending"
    return "all_clear"


# ── 簡化版圖（適合 MVP 演示）───────────────────────────────────
def build_simple_workflow():
    """
    簡化版工作流圖：
    輸入 → 規劃 → 生成 → 審批 → 執行 → 輸出

    適用於快速驗證核心邏輯
    """
    from langgraph.graph import StateGraph, END

    simple_graph = StateGraph(BusinessState)

    simple_graph.add_node("input", lambda s: s)  # 保持輸入
    simple_graph.add_node("plan", async_orchestrator_node)
    simple_graph.add_node("approve", async_human_review_node)
    simple_graph.add_node("run", async_execute_node)

    simple_graph.set_entry_point("input")
    simple_graph.add_edge("input", "plan")
    simple_graph.add_conditional_edges(
        "plan",
        lambda s: "approve" if s.get("pending_approval") else "run",
        {"approve": "approve", "run": "run"}
    )
    simple_graph.add_edge("approve", "run")
    simple_graph.add_edge("run", END)

    return simple_graph.compile()


# ── 導出供外部使用 ─────────────────────────────────────────────
workflow_graph = build_workflow_graph()
