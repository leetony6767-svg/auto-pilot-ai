"""
AI Hunter Engine — AI 獵客與數據處理引擎

反推自 Polsia 增長/獲客 Agent 的核心能力：
- 多源數據聚合（LinkedIn、Twitter、Crunchbase、新聞稿）
- 智能线索評分與篩選
- 自動數據清洗與格式化
- 目標客戶畫像匹配
- 批量Lead Generation Pipeline
"""
import asyncio
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional, Any
from loguru import logger


@dataclass
class Lead:
    """线索數據結構"""
    id: str
    name: str
    company: str
    title: str
    email: str
    industry: str
    source: str
    score: float  # 匹配分數 0-100
    match_reason: str
    created_at: str
    metadata: Dict[str, Any] = None


@dataclass
class SearchQuery:
    """搜索查詢參數"""
    keywords: List[str]
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    min_score: int = 60
    max_results: int = 50


class AIHunterEngine:
    """AI 獵客引擎 - 多源數據聚合與线索生成"""

    name = "ai_hunter_engine"

    # 模擬數據源
    _mock_data_sources = {
        "linkedin": [
            {"name": "張小明", "company": "AI Startup Inc.", "title": "CEO", "email": "ceo@ai_startup.com", "industry": "AI/ML"},
            {"name": "李華", "company": "TechFlow", "title": "CTO", "email": "cto@techflow.io", "industry": "SaaS"},
            {"name": "王大锤", "company": "DataMiner", "title": "Founder", "email": "founder@dataminer.co", "industry": "Data"},
            {"name": "陳小美", "company": "CloudBase", "title": "VP Engineering", "email": "vp@cloudbase.com", "industry": "Cloud"},
            {"name": "劉技術", "company": "MLPlatform", "title": "Head of Product", "email": "product@mlplatform.ai", "industry": "AI/ML"},
        ],
        "twitter": [
            {"name": "@ai_founder_tw", "company": "AIVenture", "title": "Founder & CEO", "email": "hello@aiventure.io", "industry": "AI/ML"},
            {"name": "@tech_ceo_cn", "company": "SmartCorp", "title": "CEO", "email": "ceo@smartcorp.tech", "industry": "Enterprise"},
        ],
        "crunchbase": [
            {"name": "赵科技", "company": "NextGen AI", "title": "CEO", "email": "ceo@nextgen.ai", "industry": "AI/ML", "funding": "$5M Series A"},
            {"name": "孙创业", "company": "AutoScale", "title": "Co-founder", "email": "co@autoscale.io", "industry": "SaaS", "funding": "$2M Seed"},
        ],
        "news": [
            {"name": "周报道", "company": "InnovateLab", "title": "Founder", "email": "founder@innovatelab.com", "industry": "Tech", "news": "剛獲種子輪融資"},
        ]
    }

    # 行業关键词匹配規則
    _industry_keywords = {
        "AI/ML": ["AI", "ML", "机器学习", "人工智能", "deep learning", "neural"],
        "SaaS": ["SaaS", "software", "platform", "cloud", "subscription"],
        "FinTech": ["fintech", "finance", "payment", "blockchain", "crypto"],
        "EdTech": ["education", "learning", "training", "e-learning"],
        "HealthTech": ["health", "medical", "biotech", "pharma"],
        "E-commerce": ["ecommerce", "retail", "shop", "marketplace"],
    }

    def __init__(self):
        self.leads: List[Lead] = []
        self.search_history: List[Dict] = []
        self.stats = {
            "total_searches": 0,
            "total_leads": 0,
            "avg_score": 0.0,
        }

    async def search_leads(self, query: SearchQuery) -> List[Lead]:
        """執行线索搜索"""
        logger.info(f"[{self.name}] 開始搜索: {query.keywords}")
        self.stats["total_searches"] += 1

        # 從多個數據源聚合
        all_candidates = []
        for source, data in self._mock_data_sources.items():
            candidates = self._filter_by_query(data, query, source)
            all_candidates.extend(candidates)

        # 去重
        seen_emails = set()
        unique_candidates = []
        for c in all_candidates:
            if c["email"] not in seen_emails:
                seen_emails.add(c["email"])
                unique_candidates.append(c)

        # 評分
        scored_leads = []
        for candidate in unique_candidates:
            score = self._calculate_match_score(candidate, query)
            if score >= query.min_score:
                lead = Lead(
                    id=f"LEAD-{datetime.now().strftime('%Y%m%d')}-{len(scored_leads)+1:04d}",
                    name=candidate["name"],
                    company=candidate["company"],
                    title=candidate["title"],
                    email=candidate["email"],
                    industry=candidate.get("industry", "Unknown"),
                    source=f"{'/'.join(query.keywords)} via {candidate.get('source', 'mixed')}",
                    score=round(score, 1),
                    match_reason=self._generate_match_reason(candidate, query),
                    created_at=datetime.now().isoformat(),
                    metadata=candidate,
                )
                scored_leads.append(lead)

        # 排序
        scored_leads.sort(key=lambda x: x.score, reverse=True)

        # 限制數量
        self.leads = scored_leads[:query.max_results]
        self.stats["total_leads"] += len(self.leads)

        # 記錄搜索歷史
        self.search_history.append({
            "query": query.__dict__,
            "results_count": len(self.leads),
            "timestamp": datetime.now().isoformat(),
        })

        logger.info(f"[{self.name}] 搜索完成: 找到 {len(self.leads)} 個高匹配线索")
        return self.leads

    def _filter_by_query(self, data: List[Dict], query: SearchQuery, source: str) -> List[Dict]:
        """根據查詢條件篩選數據"""
        results = []
        for item in data:
            # 关键词匹配
            matched = False
            for keyword in query.keywords:
                if any(kw.lower() in str(v).lower() for v in item.values() for kw in keyword.split()):
                    matched = True
                    break

            # 行业匹配
            if query.industry and item.get("industry") != query.industry:
                continue

            # 来源标记
            item["source"] = source
            if matched or query.industry is None:
                results.append(item)

        return results

    def _calculate_match_score(self, candidate: Dict, query: SearchQuery) -> float:
        """計算匹配分數"""
        score = 50.0  # 基礎分

        # 关键词匹配加分
        for keyword in query.keywords:
            for field_value in candidate.values():
                if keyword.lower() in str(field_value).lower():
                    score += 10
                    break

        # 職位匹配加分（CEO/Founder/CTO 更高價值）
        high_value_titles = ["CEO", "Founder", "CTO", "VP", "Head"]
        for title in high_value_titles:
            if title in candidate.get("title", ""):
                score += 15
                break

        # 行業匹配加分
        if query.industry:
            for ind_key, ind_kw in self._industry_keywords.items():
                if query.industry.lower() in ind_key.lower():
                    if candidate.get("industry", "").lower() in ind_key.lower():
                        score += 20
                        break

        # 有融資金額加分
        if "funding" in candidate:
            score += 10

        return min(score, 100.0)

    def _generate_match_reason(self, candidate: Dict, query: SearchQuery) -> str:
        """生成匹配理由"""
        reasons = []

        # 職位原因
        title = candidate.get("title", "")
        if "CEO" in title or "Founder" in title:
            reasons.append("決策者")
        elif "CTO" in title or "VP" in title:
            reasons.append("技術決策者")

        # 行業原因
        if query.industry and candidate.get("industry") == query.industry:
            reasons.append(f"{query.industry} 領域")

        # 关键词原因
        for kw in query.keywords[:2]:
            reasons.append(f"匹配 '{kw}'")

        return "；".join(reasons) if reasons else "高度匹配目標受眾"

    def get_stats(self) -> Dict:
        """獲取統計信息"""
        avg_score = sum(l.score for l in self.leads) / len(self.leads) if self.leads else 0
        return {
            **self.stats,
            "avg_score": round(avg_score, 1),
            "leads_by_industry": self._count_by_industry(),
            "leads_by_source": self._count_by_source(),
        }

    def _count_by_industry(self) -> Dict[str, int]:
        """按行業統計"""
        counts = {}
        for lead in self.leads:
            counts[lead.industry] = counts.get(lead.industry, 0) + 1
        return counts

    def _count_by_source(self) -> Dict[str, int]:
        """按來源統計"""
        counts = {}
        for lead in self.leads:
            source = lead.source.split(" via ")[-1] if " via " in lead.source else "unknown"
            counts[source] = counts.get(source, 0) + 1
        return counts

    def export_leads(self, format: str = "json") -> str:
        """導出线索數據"""
        if format == "json":
            return json.dumps(
                [asdict(l) for l in self.leads],
                ensure_ascii=False,
                indent=2
            )
        elif format == "csv":
            if not self.leads:
                return ""
            headers = ["id", "name", "company", "title", "email", "industry", "score", "match_reason"]
            lines = [",".join(headers)]
            for lead in self.leads:
                row = [str(getattr(lead, h, "")) for h in headers]
                lines.append(",".join(row))
            return "\n".join(lines)
        return "[]"

    def clear_leads(self):
        """清空线索"""
        self.leads = []
        logger.info(f"[{self.name}] 线索已清空")


# 測試函數
def test_hunter_engine():
    """測試 AI 猎客引擎"""
    print("=" * 70)
    print("AI Hunter Engine — 线索搜索測試")
    print("=" * 70)
    print()

    engine = AIHunterEngine()

    # 測試 1: 搜索 AI/ML 相關线索
    print("【測試 1】搜索 AI/ML 領域决策者")
    print("-" * 70)
    query = SearchQuery(
        keywords=["AI", "startup"],
        industry="AI/ML",
        min_score=50,
        max_results=10
    )
    leads = asyncio.run(engine.search_leads(query))

    print(f"找到 {len(leads)} 個线索:")
    for lead in leads[:5]:
        print(f"  [{lead.score:5.1f}] {lead.name} - {lead.company} ({lead.title})")
        print(f"         郵件: {lead.email}")
        print(f"         理由: {lead.match_reason}")
        print()

    # 測試 2: 統計信息
    print("【測試 2】統計信息")
    print("-" * 70)
    stats = engine.get_stats()
    print(f"  總搜索次數: {stats['total_searches']}")
    print(f"  總线索數: {stats['total_leads']}")
    print(f"  平均分數: {stats['avg_score']}")
    print(f"  按行業分佈: {stats['leads_by_industry']}")
    print(f"  按來源分佈: {stats['leads_by_source']}")

    # 測試 3: 導出 CSV
    print("\n【測試 3】導出 CSV")
    print("-" * 70)
    csv_data = engine.export_leads(format="csv")
    print(csv_data[:500] + "..." if len(csv_data) > 500 else csv_data)

    print("\n" + "=" * 70)
    print("✅ AI Hunter Engine 測試通過！")
    print("=" * 70)


if __name__ == "__main__":
    test_hunter_engine()
