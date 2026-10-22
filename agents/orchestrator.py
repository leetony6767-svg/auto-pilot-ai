"""
Orchestrator Agent — 總指揮：任務分發、狀態監控、流程協調

反推自 Polsia 的调度 Agent（#9）職責。
"""
from loguru import logger
from datetime import datetime

from agents.base import BaseAgent, BusinessState, PermissionLevel, approval_router, route_by_task
from agents.planner_agent import PlannerAgent
from agents.code_agent import CodeAgent
from agents.marketing_agent import MarketingAgent
from agents.outreach_agent import OutreachAgent
from agents.idea_discovery_agent import IdeaDiscoveryAgent
from config.cost_control import cost_tracker


class OrchestratorAgent(BaseAgent):
    """總指揮 Agent：協調所有子 Agent 執行完整工作流"""

    name = "orchestrator"
    permission_level = PermissionLevel.EXTERNAL

    def __init__(self, state: BusinessState):
        super().__init__(state)
        self.agents = {
            "planner": PlannerAgent,
            "code": CodeAgent,
            "marketing": MarketingAgent,
            "outreach": OutreachAgent,
        }
        self.active_agent = None

    async def run(self) -> BusinessState:
        """主入口：按順序執行完整工作流"""
        logger.info(f"[{self.name}] 啟動自動化工作流，用戶: {self.state['user_id']}")
        idea_text = self.state.get("business_idea", "")
        logger.info(f"[{self.name}] 商業構想: {idea_text[:80] if idea_text else '無（將使用創意發現）'}...")

        try:
            # Phase 0: 創意發現（當用戶沒有明確構想時）
            self.active_agent = "idea_discovery"
            logger.info("[Phase 0/5] 創意發現階段：為用戶推薦市場熱門構想")
            idea_agent = IdeaDiscoveryAgent()
            ideas_result = await idea_agent.discover_ideas(count=3)
            self.state["discovered_ideas"] = ideas_result
            self.state["audit_log"].append({
                "step": "idea_discovery",
                "status": "success",
                "ideas_count": len(ideas_result),
                "tokens": 0,
                "timestamp": datetime.now().isoformat(),
            })
            logger.info(f"[{self.name}] 已發現 {len(ideas_result)} 個商業構想")

            # Phase 1: 規劃（CEO Agent）
            self.active_agent = "planner"
            logger.info("[Phase 1/5] 規劃階段：生成商業執行計劃")
            planner = PlannerAgent(self.state)
            plan_result = await planner.run()
            self.state.update(plan_result)
            self._merge_state(plan_result)

            if "error" in plan_result:
                logger.error(f"[{self.name}] 規劃階段失敗，終止流程")
                return self.state

            # Phase 2: 建站（技術 Agent）
            self.active_agent = "code"
            logger.info("[Phase 2/5] 建站階段：生成 Landing Page")
            coder = CodeAgent(self.state)
            code_result = await coder.run()
            self._merge_state(code_result)

            if code_result.get("error"):
                logger.warning(f"[{self.name}] 建站階段有問題: {code_result['error']}")

            # Phase 3: 內容（營銷 Agent）
            self.active_agent = "marketing"
            logger.info("[Phase 3/5] 內容階段：生成社媒內容排期")
            marketer = MarketingAgent(self.state)
            marketing_result = await marketer.run()
            self._merge_state(marketing_result)

            # Phase 4: 獲客（Outreach Agent）- 已禁用，需要線索數據
            # self.active_agent = "outreach"
            # logger.info("[Phase 4/5] 獲客階段：生成開發郵件")
            # outreach = OutreachAgent(self.state)
            # outreach_result = await outreach.run()
            # self._merge_state(outreach_result)
            self.log(status="outreach_skipped", reason="需要線索數據")

            # 完成報告
            self.state["metrics"] = {
                "workflow_status": "completed",
                "completed_at": datetime.now().isoformat(),
                "pending_approvals": len(self.state["pending_approval"]),
                "audit_log_length": len(self.state["audit_log"]),
                "total_tokens_used": sum(
                    entry.get("tokens", 0) for entry in self.state["audit_log"]
                ),
            }

            logger.info(f"[{self.name}] 工作流完成！待審批項目: {len(self.state['pending_approval'])}")
            logger.info(f"[{self.name}] 總 Token 消耗: {self.state['metrics']['total_tokens_used']}")

            return self.state

        except Exception as e:
            self.state["metrics"] = {
                "workflow_status": "error",
                "error": str(e),
                "completed_at": datetime.now().isoformat(),
            }
            logger.error(f"[{self.name}] 工作流執行失敗: {e}")
            return self.state

    def _merge_state(self, result: dict):
        """將 Agent 結果合併到全局狀態"""
        for key, value in result.items():
            if key == "audit_log" and isinstance(value, list):
                self.state["audit_log"].extend(value)
            elif key == "pending_approval":
                if isinstance(value, list):
                    self.state["pending_approval"].extend(value)
                elif value is True:
                    # Agent 標記有待審批，但不提供具體內容
                    pass
            elif key == "approved_items" and isinstance(value, list):
                self.state["approved_items"].extend(value)
            elif key not in ("error", "tokens", "code_generated", "code_length",
                             "days", "posts_count", "emails_generated", "skipped"):
                self.state[key] = value

    async def handle_approval(self, approval_id: str, approved: bool, comment: str = "") -> dict:
        """處理人工審批決策"""
        logger.info(f"[{self.name}] 審批請求: {approval_id}, 通過: {approved}")

        # 從隊列中移除並記錄
        self.state["pending_approval"] = [
            a for a in self.state["pending_approval"] if str(a.get("id", "")) != approval_id
        ]

        if approved:
            self.state["approved_items"].append({
                "id": approval_id,
                "approved": True,
                "comment": comment,
                "approved_at": datetime.now().isoformat(),
            })
            logger.info(f"[{self.name}] 審批通過: {approval_id}")
        else:
            self.state["approved_items"].append({
                "id": approval_id,
                "approved": False,
                "comment": comment,
                "rejected_at": datetime.now().isoformat(),
            })
            logger.warning(f"[{self.name}] 審批拒絕: {approval_id} - {comment}")

        return {
            "approval_id": approval_id,
            "approved": approved,
            "comment": comment,
        }

    def get_pending_approvals(self) -> list[dict]:
        """獲取所有待審批項目"""
        return self.state["pending_approval"]

    def get_audit_summary(self) -> dict:
        """獲取審計摘要"""
        total_tokens = sum(e.get("tokens", 0) for e in self.state["audit_log"])
        errors = [e for e in self.state["audit_log"] if e.get("status") == "error"]

        return {
            "total_steps": len(self.state["audit_log"]),
            "total_tokens": total_tokens,
            "error_count": len(errors),
            "pending_approvals": len(self.state["pending_approval"]),
            "log_entries": self.state["audit_log"][-10:],  # 最近 10 條
        }
