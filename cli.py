"""CLI 入口 — 命令行工具"""
import typer
import asyncio
from typing import Optional
from loguru import logger

from app import app
import uvicorn

cli = typer.Typer(help="StorePilot AI — 命令行工具")


@cli.command()
def serve(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True,
):
    """啟動 API 服務器"""
    logger.info(f"啟動 StorePilot AI 服務器: http://{host}:{port}")
    logger.info(f"API 文檔: http://{host}:{port}/docs")
    logger.info(f"重載模式: {'啟用' if reload else '禁用'}")

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


@cli.command()
def dry_run(
    user_id: str = "demo-user",
    idea: str = "一個幫助自由職業者自動管理客戶和發票的 AI SaaS 產品",
):
    """乾跑模式：驗證完整工作流邏輯"""
    logger.info(f"=== Dry Run 模式 ===")
    logger.info(f"用戶: {user_id}")
    logger.info(f"商業構想: {idea}")
    logger.info("")

    from agents.base import BusinessState
    from app import _dry_run_workflow

    initial_state: BusinessState = {
        "user_id": user_id,
        "business_idea": idea,
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

    async def run():
        result = await _dry_run_workflow(initial_state)
        return result

    result = asyncio.run(run())

    logger.info("")
    logger.info("=== 執行結果 ===")
    logger.info(f"工作流狀態: {result['metrics'].get('workflow_status', 'unknown')}")
    logger.info(f"待審批項目: {len(result.get('pending_approval', []))}")
    logger.info(f"審計日誌條數: {len(result.get('audit_log', []))}")
    logger.info(f"總 Token 消耗: {result['metrics'].get('total_tokens_used', 'N/A')}")

    if result.get("business_plan"):
        plan = result["business_plan"]
        logger.info(f"產品名稱: {plan.get('product_name', 'N/A')}")
        logger.info(f"產品定位: {plan.get('positioning', 'N/A')}")
        logger.info(f"目標受眾: {plan.get('target_audience', 'N/A')}")

    if result.get("pending_approval"):
        logger.info("")
        logger.info("=== 待審批項目 ===")
        for item in result["pending_approval"]:
            logger.info(f"  - [{item['type']}] {item.get('reason', '')}")


@cli.command()
def test():
    """運行單元測試"""
    import pytest
    pytest.main(["-v", "tests/"])


@cli.command()
def cost_report():
    """顯示成本統計報告"""
    from config.cost_control import budget, cost_tracker

    logger.info("=== 成本統計報告 ===")
    logger.info(f"全局每日 Token 使用: {budget.global_daily_usage:,}")
    logger.info(f"全局每日預算上限: {budget.global_daily:,}")
    usage_pct = (budget.global_daily_usage / budget.global_daily) * 100
    logger.info(f"預算使用率: {usage_pct:.1f}%")
    logger.info(f"預估成本: ${cost_tracker.estimate_cost(budget.global_daily_usage, 'deepseek-chat'):.2f}")
    logger.info("")
    logger.info("Agent 層面使用（最近 5 條）:")
    for key, val in list(budget.agent_usage.items())[-5:]:
        logger.info(f"  {key}: {val:,} tokens")


if __name__ == "__main__":
    cli()
