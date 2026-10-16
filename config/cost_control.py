"""
成本控制策略 — 從 Polsia $120萬帳單危機中汲取的教訓

核心原則：
1. 模型分級路由 — 簡單任務用小模型，複雜推理用大模型
2. Token 預算限制 — 每個 Agent 每任務有上限
3. 上下文裁剪 — 只保留必要信息，避免 Token 浪費
"""
from dataclasses import dataclass, field
from typing import Optional


# ── Token 預算 ──────────────────────────────────────────────────
@dataclass
class TokenBudget:
    """Token 使用限制"""
    per_agent_per_task: int = 8_000       # 每 Agent 每任務上限
    per_user_per_day: int = 500_000       # 每用戶每日上限
    global_daily: int = 10_000_000        # 全局每日上限

    # 歷史記錄
    agent_usage: dict = field(default_factory=dict)   # {agent_name: {date: tokens}}
    user_usage: dict = field(default_factory=dict)    # {user_id: {date: tokens}}
    global_daily_usage: int = 0


budget = TokenBudget()


# ── 上下文裁剪策略 ──────────────────────────────────────────────
@dataclass
class ContextPolicy:
    """上下文管理策略"""
    keep_last_n_messages: int = 10          # 只保留最近 N 條對話
    summarize_after_n_messages: int = 20   # 超過 N 條時觸發摘要
    max_context_tokens: int = 4_000        # 單條上下文最大 Token
    enable_summarization: bool = True      # 是否啟用自動摘要


context_policy = ContextPolicy()


# ── 成本監控工具 ────────────────────────────────────────────────
class CostTracker:
    """追蹤並控制 Token 消耗"""

    def __init__(self, budget: TokenBudget, policy: ContextPolicy):
        self.budget = budget
        self.policy = policy

    def check_agent_budget(self, agent_name: str, tokens: int) -> bool:
        """檢查 Agent 當前任務是否超出預算"""
        today = self._today()
        key = f"{agent_name}:{today}"
        current = self.budget.agent_usage.get(key, 0)
        return (current + tokens) <= self.budget.per_agent_per_task

    def check_user_budget(self, user_id: str, tokens: int) -> bool:
        """檢查用戶當日是否超出預算"""
        today = self._today()
        key = f"{user_id}:{today}"
        current = self.budget.user_usage.get(key, 0)
        return (current + tokens) <= self.budget.per_user_per_day

    def check_global_budget(self, tokens: int) -> bool:
        """檢查全局當日是否超出預算"""
        return (self.budget.global_daily_usage + tokens) <= self.budget.global_daily

    def record_usage(self, agent_name: str, user_id: str, tokens: int):
        """記錄 Token 消耗"""
        today = self._today()

        # Agent 層面
        agent_key = f"{agent_name}:{today}"
        self.budget.agent_usage[agent_key] = (
            self.budget.agent_usage.get(agent_key, 0) + tokens
        )

        # 用戶層面
        user_key = f"{user_id}:{today}"
        self.budget.user_usage[user_key] = (
            self.budget.user_usage.get(user_key, 0) + tokens
        )

        # 全局層面
        self.budget.global_daily_usage += tokens

    def trim_context(self, messages: list, max_tokens: Optional[int] = None) -> list:
        """上下文裁剪：只保留最近 N 條消息"""
        limit = max_tokens or self.policy.max_context_tokens
        if len(messages) <= self.policy.keep_last_n_messages:
            return messages
        # 保留最後 N 條 + 開頭系統提示
        return [messages[0]] + messages[-self.policy.keep_last_n_messages:]

    def estimate_cost(self, tokens: int, model: str) -> float:
        """估算成本（USD）"""
        # 參考定價（每百万 Token）
        prices = {
            "claude-sonnet-4": 3.0,
            "claude-haiku-4": 0.25,
            "deepseek-chat": 0.14,
            "deepseek-r1": 0.55,
            "gpt-4o": 2.50,
        }
        price_per_m = prices.get(model, 1.0)
        return (tokens / 1_000_000) * price_per_m

    @staticmethod
    def _today() -> str:
        from datetime import date
        return date.today().isoformat()


# 全局實例
cost_tracker = CostTracker(budget, context_policy)
