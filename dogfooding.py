"""
Dogfooding Script — 真實產品生成
執行完整工作流，生成 Landing Page 和營銷內容
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from agents.idea_discovery_agent import IdeaDiscoveryAgent
from agents.planner_agent import PlannerAgent
from agents.code_agent import CodeAgent
from agents.marketing_agent import MarketingAgent
from agents.outreach_agent import OutreachAgent
from agents.finance_agent import FinanceAgent
from config.settings import settings


async def run_dogfooding():
    """執行完整產品生成流程"""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("MVP Agent OS — Dogfooding 真實產品生成")
    print("=" * 70)
    print()

    # Step 1: 發現創意
    print("[Step 1] 發現商業構想...")
    idea_agent = IdeaDiscoveryAgent()
    ideas = await idea_agent.discover_ideas(count=3)

    # 選擇 Niche Content Agency for AI Creators
    selected_idea = None
    for idea in ideas:
        if "Content Agency" in idea["title"]:
            selected_idea = idea
            break
    if not selected_idea:
        selected_idea = ideas[1]  # fallback

    print(f"  已選擇: {selected_idea['title']}")
    print(f"  分類: {selected_idea['category']}")
    print(f"  預估月收: ${selected_idea['estimated_monthly_revenue']:,.0f}")
    print()

    # 保存選擇的構想
    with open(output_dir / "selected_idea.json", "w", encoding="utf-8") as f:
        json.dump(selected_idea, f, ensure_ascii=False, indent=2)

    # Step 2: 初始化 BusinessState
    state = {
        "user_id": "dogfooding-demo",
        "business_idea": selected_idea["title"],
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

    # Step 3: 規劃階段
    print("[Step 2] 規劃階段 — Planner Agent...")
    planner = PlannerAgent(state)
    plan_result = await planner.run()
    state.update(plan_result)

    if "error" in plan_result:
        print(f"  規劃失敗: {plan_result['error']}")
        return
    print(f"  業務計劃已生成: {plan_result.get('business_plan', {}).get('product_name', 'Unknown')}")
    print()

    # Step 4: 建站階段
    print("[Step 3] 建站階段 — Code Agent...")
    code_agent = CodeAgent(state)
    code_result = await code_agent.run()
    state.update(code_result)

    if "error" in code_result:
        print(f"  代碼生成失敗: {code_result['error']}")
        return
    print(f"  代碼長度: {code_result.get('code_length', 0)} 字節")
    print()

    # 保存生成的代碼
    with open(output_dir / "landing_page.html", "w", encoding="utf-8") as f:
        f.write(state.get("landing_page_code", "<!-- Landing Page Generated -->"))
    print(f"  已保存到: output/landing_page.html")
    print()

    # Step 5: 營銷階段
    print("[Step 4] 營銷階段 — Marketing Agent...")
    marketing_agent = MarketingAgent(state)
    marketing_result = await marketing_agent.run()
    state.update(marketing_result)

    if "error" in marketing_result:
        print(f"  內容生成失敗: {marketing_result['error']}")
        return
    posts_count = marketing_result.get("posts_count", 0)
    print(f"  已生成 {posts_count} 篇社媒內容")
    print()

    # 保存營銷內容
    with open(output_dir / "marketing_content.json", "w", encoding="utf-8") as f:
        json.dump({
            "posts": state.get("content_queue", []),
            "pending_approval": True,
        }, f, ensure_ascii=False, indent=2)
    print(f"  已保存到: output/marketing_content.json")
    print()

    # Step 6: 財務計算
    print("[Step 5] 財務分析 — Finance Agent...")
    finance = FinanceAgent(
        monthly_revenue=selected_idea.get("estimated_monthly_revenue", 8000.0),
        ad_spend=0.0
    )
    split = finance.calculate_split()
    report = finance.generate_report(
        revenue=selected_idea.get("estimated_monthly_revenue", 8000.0)
    )

    print(f"  總營收: ${report['gross_revenue']:,.2f}")
    print(f"  平台抽成 ({report['platform_rate']}): ${report['platform_revenue']['total']:,.2f}")
    print(f"  用戶留存 ({report['user_rate']}): ${report['user_revenue']['revenue_after_share']:,.2f}")
    print(f"  用戶淨收入: ${report['user_revenue']['net_income']:,.2f}")
    print()

    # 保存財務報告
    with open(output_dir / "revenue_split.json", "w", encoding="utf-8") as f:
        json.dump({
            "source_idea": selected_idea,
            "financial_split": report,
            "calculation_timestamp": datetime.now().isoformat(),
        }, f, ensure_ascii=False, indent=2)
    print(f"  已保存到: output/revenue_split.json")
    print()

    # Step 7: 獲取客階段 (可选)
    print("[Step 6] 獲客階段 — Outreach Agent...")
    outreach = OutreachAgent(state)
    outreach_result = await outreach.run()
    state.update(outreach_result)

    if "error" not in outreach_result:
        emails_count = outreach_result.get("emails_generated", 0)
        print(f"  已生成 {emails_count} 封開發郵件")
        print()

        # 保存 outreach 內容
        with open(output_dir / "outreach_emails.json", "w", encoding="utf-8") as f:
            json.dump(state.get("outreach_emails", []), f, ensure_ascii=False, indent=2)
        print(f"  已保存到: output/outreach_emails.json")

    print()
    print("=" * 70)
    print("Dogfooding 完成!")
    print("=" * 70)
    print()
    print("生成的文件:")
    print(f"  - output/selected_idea.json")
    print(f"  - output/landing_page.html")
    print(f"  - output/marketing_content.json")
    print(f"  - output/revenue_split.json")
    if outreach_result.get("emails_generated", 0) > 0:
        print(f"  - output/outreach_emails.json")
    print()
    print("財務分潤摘要:")
    print(f"  總營收: ${report['gross_revenue']:,.2f}/月")
    print(f"  平台收入: ${report['platform_revenue']['total']:,.2f}/月")
    print(f"  用戶淨收入: ${report['user_revenue']['net_income']:,.2f}/月")


if __name__ == "__main__":
    asyncio.run(run_dogfooding())
