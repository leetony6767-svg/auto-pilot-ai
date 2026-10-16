"""
IdeaDiscoveryAgent — 商業創意發現與推薦

當用戶沒有明確的商業構想時，自動推薦市場熱門且高轉化率的微型產品/服務點子。
基於市場趨勢分析、熱門創業模式和轉化率數據。
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from loguru import logger


@dataclass
class BusinessIdea:
    """商業構想數據結構"""
    id: str
    title: str
    category: str
    description: str
    target_audience: str
    revenue_model: str
    difficulty: str  # easy / medium / hard
    estimated_monthly_revenue: float
    required_investment: float
    market_trend: str  # rising / stable / declining
    key_features: List[str]
    competition_level: str  # low / medium / high
    why_now: str
    first_steps: List[str]


class IdeaDiscoveryAgent:
    """商業創意發現 Agent"""

    name = "idea_discovery_agent"

    # 市場熱門微型產品/服務點子庫
    _idea_pool = [
        BusinessIdea(
            id="IDEA-001",
            title="AI 輔助的自由職業者財務管理 SaaS",
            category="FinTech / Productivity",
            description="幫助自由職業者自動追蹤收入、開支、發票和稅務的 AI 工具",
            target_audience="自由職業者、合夥人、小型工作室",
            revenue_model="訂閱制 $29-49/月 + 交易手續費 1%",
            difficulty="medium",
            estimated_monthly_revenue=5000.0,
            required_investment=500.0,
            market_trend="rising",
            key_features=[
                "AI 自動分類交易",
                "智能發票生成與追蹤",
                "稅務預算建議",
                "多客戶儀表板",
                "銀行 API 集成"
            ],
            competition_level="medium",
            why_now="自由職業者數量激增，但現有工具過於複雜或昂貴",
            first_steps=[
                "驗證目標用戶痛點（訪談 10+ 自由職業者）",
                "創建 MVP（簡單的發票追蹤工具）",
                "在 Reddit/r/freelance 獲取反饋",
                "迭代並添加 AI 功能"
            ]
        ),
        BusinessIdea(
            id="IDEA-002",
            title="Niche Content Agency for AI Creators",
            category="Media / Marketing",
            description="專門為 AI/科技創作者提供內容策劃、社媒管理和社群運營的代运营服務",
            target_audience="AI 創始人、技術博主、SaaS 創業者",
            revenue_model="項目制 $2,000-5,000/月 + 成績抽成",
            difficulty="easy",
            estimated_monthly_revenue=8000.0,
            required_investment=100.0,
            market_trend="rising",
            key_features=[
                "AI 生成內容草稿",
                "社媒排程自動化",
                "數據分析與優化",
                "社群管理",
                " influencer 合作對接"
            ],
            competition_level="low",
            why_now="AI 創作者需要專業內容支持但預算有限",
            first_steps=[
                "建立個人品牌展示案例",
                "在 Twitter/LinkedIn 分享內容策略",
                "提供免費審計吸引首批客戶",
                "標準化服務流程並定價"
            ]
        ),
        BusinessIdea(
            id="IDEA-003",
            title="Micro-SaaS: Automated LinkedIn Lead Generation",
            category="B2B SaaS / Sales",
            description="自動化 LinkedIn 潛在客戶發現、訊息發送和跟進的微型 SaaS",
            target_audience="B2B 銷售團隊、獵頭、業務開發人員",
            revenue_model="訂閱制 $99-299/月",
            difficulty="medium",
            estimated_monthly_revenue=15000.0,
            required_investment=1000.0,
            market_trend="rising",
            key_features=[
                "智能候選人篩選",
                "個性化訊息模板",
                "自動跟進排程",
                "CRM 集成",
                "轉化率分析"
            ],
            competition_level="high",
            why_now="B2B 銷售自動化需求持续增长，但現有解決方案過於昂貴",
            first_steps=[
                "研究現有的 CRM 和銷售工具",
                "專注特定行業（如 SaaS、諮詢）",
                "創建等待名單 Landing Page",
                "與 5-10 個潛在用戶進行深度訪談"
            ]
        ),
        BusinessIdea(
            id="IDEA-004",
            title="AI-Powered Resume & Career Coach",
            category="Education / HR Tech",
            description="使用 AI 幫助求職者優化履歷、模擬面試、職業規劃的平台",
            target_audience="求職者、轉職人士、畢業生",
            revenue_model=" Freemium + 高級功能 $19-49/月",
            difficulty="easy",
            estimated_monthly_revenue=3000.0,
            required_investment=200.0,
            market_trend="stable",
            key_features=[
                "AI 履歷審查與優化",
                "虛擬面試模擬",
                "行業薪資報告",
                "職業路線規劃",
                "求職郵件生成"
            ],
            competition_level="medium",
            why_now="就業市場競爭激烈，求職者願意為專業指導付費",
            first_steps=[
                "創建簡單的履歷優化工具",
                "在求職社群分享內容建立信任",
                "收集用戶反饋迭代功能",
                "擴展到面試準備和職業規劃"
            ]
        ),
        BusinessIdea(
            id="IDEA-005",
            title="Niche Newsletter + Paid Community",
            category="Media / Community",
            description="針對特定垂直領域（如 AI 應用、Web3、SaaS 營銷）的付費訂閱通訊 + 社群",
            target_audience="特定領域的專業人士和愛好者",
            revenue_model="訂閱制 $10-50/月 + 贊助",
            difficulty="easy",
            estimated_monthly_revenue=5000.0,
            required_investment=50.0,
            market_trend="rising",
            key_features=[
                "每週深度分析文章",
                "專屬 Discord/Slack 社群",
                "月度AMA座談",
                "行業資源庫",
                "機會板（工作、合作）"
            ],
            competition_level="medium",
            why_now="資訊過載時代，專業篩選和社群歸屬感成為稀缺資源",
            first_steps=[
                "選擇一個你熟悉的垂直領域",
                "免費發送 4-6 週電子報建立受眾",
                "測試付費轉換率",
                "建立社群並提供獨享內容"
            ]
        ),
        BusinessIdea(
            id="IDEA-006",
            title="AI Video Editing Service for YouTubers",
            category="Creative Services",
            description="為 YouTube 創作者提供 AI 輔助剪輯、字幕生成、封面設計的按需服務",
            target_audience="中小型 YouTube 創作者、Podcast 主",
            revenue_model="按作品收費 $50-500/次 + 月訂閱包",
            difficulty="easy",
            estimated_monthly_revenue=4000.0,
            required_investment=300.0,
            market_trend="rising",
            key_features=[
                "AI 自動剪輯長視頻",
                "智能字幕生成",
                "封面設計模板",
                "縮短片段提取",
                "SEO 優化建議"
            ],
            competition_level="low",
            why_now="內容創作需求爆炸，但創作者缺乏時間進行專業剪輯",
            first_steps=[
                "建立展示作品 Portfolio",
                "在 YouTuber 社群推廣服務",
                "與 3-5 個創作者合作獲取案例",
                "標準化流程並引入 AI 工具提高效率"
            ]
        ),
    ]

    def __init__(self):
        self.discovery_count = 0

    async def discover_ideas(self, count: int = 3, category: Optional[str] = None) -> List[dict]:
        """
        發現並推薦商業構想

        Args:
            count: 推薦數量（1-6）
            category: 可選的分類篩選

        Returns:
            商業構想列表
        """
        self.discovery_count += 1
        logger.info(f"[{self.name}] 開始發現商業構想，請求數量: {count}")

        # 篩選
        ideas = self._idea_pool
        if category:
            ideas = [i for i in ideas if i.category.lower().startswith(category.lower())]

        # 如果没有匹配的类别，使用全部
        if not ideas:
            ideas = self._idea_pool

        # 選擇前 count 個
        selected = ideas[:count]

        # 格式化輸出
        results = []
        for idea in selected:
            results.append({
                "id": idea.id,
                "title": idea.title,
                "category": idea.category,
                "description": idea.description,
                "target_audience": idea.target_audience,
                "revenue_model": idea.revenue_model,
                "difficulty": idea.difficulty,
                "estimated_monthly_revenue": idea.estimated_monthly_revenue,
                "required_investment": idea.required_investment,
                "market_trend": idea.market_trend,
                "key_features": idea.key_features,
                "competition_level": idea.competition_level,
                "why_now": idea.why_now,
                "first_steps": idea.first_steps,
                "discovered_at": datetime.now().isoformat(),
            })

        logger.info(f"[{self.name}] 已發現 {len(results)} 個商業構想")
        return results

    def get_stats(self) -> dict:
        """獲取發現統計"""
        return {
            "total_ideas_available": len(self._idea_pool),
            "discoveries_made": self.discovery_count,
            "categories": list(set(i.category.split(" / ")[0] for i in self._idea_pool)),
        }


# 測試函數
def test_idea_discovery():
    """測試 IdeaDiscoveryAgent"""
    print("=" * 70)
    print("IdeaDiscoveryAgent — 商業創意發現測試")
    print("=" * 70)
    print()

    agent = IdeaDiscoveryAgent()

    # 測試 1: 發現 3 個構想
    print("【測試 1】發現 3 個熱門商業構想")
    print("-" * 70)
    ideas = asyncio.run(agent.discover_ideas(count=3))

    for i, idea in enumerate(ideas, 1):
        print(f"\n構想 #{i}: {idea['title']}")
        print(f"  分類: {idea['category']}")
        print(f"  描述: {idea['description']}")
        print(f"  目標受眾: {idea['target_audience']}")
        print(f"  營收模式: {idea['revenue_model']}")
        print(f"  難度: {idea['difficulty']}")
        print(f"  預估月收: ${idea['estimated_monthly_revenue']:,.0f}")
        print(f"  所需投資: ${idea['required_investment']:,.0f}")
        print(f"  市場趨勢: {idea['market_trend']}")
        print(f"  為什麼是現在: {idea['why_now']}")
        print(f"  第一步:")
        for step in idea['first_steps'][:2]:
            print(f"    • {step}")

    # 測試 2: 統計信息
    print("\n" + "=" * 70)
    print("【測試 2】統計信息")
    print("-" * 70)
    stats = agent.get_stats()
    print(f"  可用構想總數: {stats['total_ideas_available']}")
    print(f"  已發現次數: {stats['discoveries_made']}")
    print(f"  可用分類: {', '.join(stats['categories'])}")

    print("\n" + "=" * 70)
    print("✅ IdeaDiscoveryAgent 測試通過！")
    print("=" * 70)


if __name__ == "__main__":
    import asyncio
    test_idea_discovery()
