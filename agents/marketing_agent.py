"""
Marketing Agent — 自動生成社群貼文

反推自 Polsia 營銷 Agent 的職責：
- 根據商業計劃生成 Twitter/X、LinkedIn 等社媒內容
- 內容策略規劃（7 天排期）
- 所有對外發布需人工審批
"""
from typing import AsyncIterator
import json
import re
from loguru import logger
from datetime import datetime, timedelta
import random

from agents.base import BaseAgent, BusinessState, PermissionLevel
from config.cost_control import cost_tracker
from config.settings import settings


class MarketingAgent(BaseAgent):
    """營銷 Agent：社群內容自動化生成"""

    name = "marketing_agent"
    permission_level = PermissionLevel.EXECUTE
    cost_model = settings.agnes_model  # 使用 Agnes AI 模型

    # 各平台字符限制
    PLATFORM_LIMITS = {
        "twitter": 280,
        "linkedin": 3000,
        "threads": 500,
    }

    def __init__(self, state: BusinessState):
        super().__init__(state)
        self.plan = state.get("business_plan", {})

    async def run(self) -> dict:
        """主入口：生成 7 天社媒內容 → 審批"""
        logger.info(f"[{self.name}] 開始生成 7 天社媒內容排期")

        try:
            content_plan = await self._generate_content_plan(days=7)

            # 所有內容加入審批隊列
            self.add_approval(
                item_type="social_content",
                content=content_plan,
                reason="7 天社媒內容排期，需確認品牌和調性"
            )

            self.log(status="content_generated", days=7, posts=len(content_plan))
            logger.info(f"[{self.name}] 生成 {len(content_plan)} 條社媒內容，待審批")

            return {
                "content_generated": True,
                "days": 7,
                "posts_count": len(content_plan),
                "pending_approval": True,
                "content_plan": content_plan,
            }

        except Exception as e:
            self.log(status="error", error=str(e))
            logger.error(f"[{self.name}] 執行失敗: {e}")
            return {"error": str(e)}

    async def _generate_content_plan(self, days: int = 7) -> list[dict]:
        """生成 N 天的社媒內容排期"""
        from openai import AsyncOpenAI

        brand_tone = self.plan.get("brand_tone", "專業但有親和力")
        product_name = self.plan.get("product_name", "AgentOS")
        positioning = self.plan.get("positioning", "")
        target_audience = self.plan.get("target_audience", "")

        prompt = f"""你是一位顶级的內容營銷專家。請為以下產品生成 {days} 天的社媒內容排期。

產品：{product_name}
定位：{positioning}
目標受眾：{target_audience}
品牌調性：{brand_tone}

內容策略要求：
- Day 1: 產品介紹 / 價值主張
- Day 2: 行業洞察 / 趨勢分析
- Day 3: 用戶故事 / 案例分享
- Day 4: 幕後花絮 / 團隊故事
- Day 5: 互動內容 / 問答 / 投票
- Day 6: 教育性內容 / 教程
- Day 7: 促銷 / CTA / 限時優惠

每條內容要求：
1. Twitter 版本（≤280字，包含 Hook）
2. LinkedIn 版本（可更長，≤3000字）
3. 包含相關 Hashtag（3-5個）
4. 建議配图方向描述

返回 JSON 數組，格式：
[{{
  "day": 1,
  "date": "2026-10-15",
  "theme": "產品介紹",
  "twitter": {{
    "copy": "推文內容",
    "hashtags": ["#AI", "#Startup"],
    "image_prompt": "配图描述"
  }},
  "linkedin": {{
    "copy": "LinkedIn 帖子內容",
    "hashtags": ["#AI", "#Startup", "#Entrepreneurship"],
    "image_prompt": "配图描述"
  }}
}}]"""

        client = AsyncOpenAI(
            api_key=settings.agnes_api_key,
            base_url=settings.agnes_base_url,
        )

        response = await client.chat.completions.create(
            model=self.cost_model,
            messages=[
                {"role": "system", "content": "你是 Social Media 內容專家，擅長創建高互動率社媒內容。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )

        tokens = response.usage.total_tokens if response.usage else 0
        content = response.choices[0].message.content if response.choices else ""
        from agents.utils import parse_llm_json
        success, content_plan, error = parse_llm_json(content)
        if not success:
            logger.warning(f"[{self.name}] JSON 解析失敗: {error}，使用 fallback")
            content_plan = self._generate_fallback_content(days)
        elif not isinstance(content_plan, list):
            # 確保返回的是列表
            content_plan = self._generate_fallback_content(days)

        # 添加元數據
        for i, post in enumerate(content_plan):
            post["id"] = f"post-{i+1}-{self.state['user_id'][:6]}"
            post["generated_at"] = datetime.now().isoformat()
            post["platforms"] = ["twitter", "linkedin"]

        self.log(tokens=tokens, status="content_generated")
        logger.debug(f"[{self.name}] 生成 {len(content_plan)} 天內容排期")

        return content_plan

    def _generate_fallback_content(self, days: int) -> list[dict]:
        """LLM 不可用時的降级方案：使用模板生成內容"""
        themes = [
            "產品介紹", "行業洞察", "用戶故事", "幕後花絮",
            "互動內容", "教育性內容", "促銷活動"
        ]
        products = [
            "AgentOS", "Polsia-like", "AI Company OS", "SoloFounder AI"
        ]
        product_name = self.plan.get("product_name", random.choice(products))

        content_plan = []
        today = datetime.now()

        for i in range(days):
            date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
            theme = themes[i % len(themes)]

            # 簡單模板
            twitter_copy = f"""🚀 Day {i+1}: {theme}

正在用 AI 重新定義創業方式。

{product_name} 讓一人公司成為可能。

#AI #Startup #SoloFounder"""

            linkedin_copy = f"""Day {i+1}: {theme}

在 AI 時代，創業的門檻正在被重新定義。

過去你需要：
• 工程師團隊
• 市場預算
• 客服人員
• 財務會計

現在你只需要：
• 一個好想法
• {product_name} 這樣的 AI 自治系統

這就是為什麼我們建立了 {product_name} —— 讓每個創客都能擁有一支 24/7 的 AI 團隊。

你有過「如果有一個團隊幫我執行就好了」的想法嗎？

#AI #Startup #Entrepreneurship #SoloFounder #Automation"""

            content_plan.append({
                "day": i + 1,
                "date": date,
                "theme": theme,
                "twitter": {
                    "copy": twitter_copy,
                    "hashtags": ["#AI", "#Startup", "#SoloFounder"],
                    "image_prompt": f"Professional workspace with AI dashboard, modern aesthetic",
                },
                "linkedin": {
                    "copy": linkedin_copy,
                    "hashtags": ["#AI", "#Startup", "#Entrepreneurship", "#SoloFounder", "#Automation"],
                    "image_prompt": f"Entrepreneur working with AI assistant, futuristic office",
                },
                "id": f"post-{i+1}-{self.state['user_id'][:6]}",
                "generated_at": datetime.now().isoformat(),
                "platforms": ["twitter", "linkedin"],
            })

        return content_plan

    async def post_to_platform(self, post: dict, platform: str, api_creds: dict) -> dict:
        """發布到社交平台（審批通過後執行）"""
        logger.info(f"[{self.name}] 发布到 {platform}: {post.get('theme', 'unknown')}")

        # 模擬發帖 API 調用
        cost_tracker.record_usage(self.name, self.state["user_id"], 100)

        return {
            "status": "posted",
            "platform": platform,
            "post_id": f"social-{random.randint(10000, 99999)}",
            "url": f"https://{platform}.com/post/{random.randint(10000, 99999)}",
            "posted_at": datetime.now().isoformat(),
        }

    async def analyze_engagement(self, post_id: str) -> dict:
        """分析帖文互動數據"""
        # 模擬數據
        return {
            "post_id": post_id,
            "impressions": random.randint(500, 5000),
            "engagements": random.randint(50, 500),
            "clicks": random.randint(10, 100),
            "conversions": random.randint(0, 5),
            "analyzed_at": datetime.now().isoformat(),
        }
