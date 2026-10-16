"""
Planner Agent — CEO Agent：接收商業構想，生成執行計劃

這是整個系統的入口點，負責理解用戶意圖並啟動後續流程。
"""
from loguru import logger
from datetime import datetime
import json
import re

from agents.base import BaseAgent, BusinessState, PermissionLevel
from config.cost_control import cost_tracker
from config.settings import settings


class PlannerAgent(BaseAgent):
    """CEO/規劃 Agent：將商業構想轉化為可執行計劃"""

    name = "planner_agent"
    permission_level = PermissionLevel.EXECUTE
    cost_model = "anthropic/claude-sonnet-4-20250514"  # 規劃需要較強推理能力

    async def run(self) -> dict:
        """主入口：分析商業構想，生成執行計劃"""
        logger.info(f"[{self.name}] 開始分析商業構想: {self.state['business_idea'][:50]}...")

        try:
            from langchain_anthropic import ChatAnthropic

            llm = ChatAnthropic(
                model=self.cost_model,
                api_key=settings.anthropic_api_key,
                temperature=0.2,  # 規劃需要確定性
            )

            prompt = f"""你是一位經驗豐富的創業顧問和產品經理。
            用戶想要創辦一家公司，想法是：

            "{self.state['business_idea']}"

            請生成一份詳細的執行計劃，包含以下 JSON 結構：
            {{
              "product_name": "產品名稱",
              "positioning": "產品定位（一句話）",
              "target_market": "目標市場描述",
              "target_audience": "目標受眾畫像",
              "core_features": ["核心功能1", "核心功能2", "核心功能3"],
              "value_proposition": "價值主張",
              "pricing": "定價策略",
              "brand_tone": "品牌調性",
              "brand_colors": "推薦配色方案",
              "go_to_market": "Go-to-Market 策略",
              "day1_actions": ["第1天要做的3件事"],
              "day7_actions": ["第7天要做的3件事"],
              "success_metrics": ["關鍵成功指標"]
            }}

            請確保計劃具體、可執行，並針對該商業領域提出專業建議。"""

            response = await llm.ainvoke([
                {"role": "system", "content": "你是 Top-tier 創業顧問，幫助創始人將想法轉化為可執行的商業計劃。輸出精確、具體、可操作。"},
                {"role": "user", "content": prompt},
            ])

            tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0
            cost_tracker.record_usage(self.name, self.state["user_id"], tokens)

            # 解析 JSON
            content = response.content
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                plan = json.loads(match.group())
            else:
                plan = {"raw_response": content}

            self.log(tokens=tokens, status="plan_generated")
            logger.info(f"[{self.name}] 計劃生成完成: {plan.get('product_name', '未知產品')}")

            return {
                "business_plan": plan,
                "tokens": tokens,
            }

        except ImportError:
            logger.warning(f"[{self.name}] langchain-anthropic 未安裝，使用 fallback 模式")
            return await self._fallback_run()
        except (ImportError, ValueError, Exception) as e:
            error_str = str(e)
            # 檢查是否是認證錯誤（缺少 API Key）
            if "authentication" in error_str.lower() or "api_key" in error_str.lower() or not settings.anthropic_api_key:
                logger.warning(f"[{self.name}] 未配置 Anthropic API Key，使用 Fallback 模式")
                return await self._fallback_run()
            logger.warning(f"[{self.name}] LLM 调用失败: {e}，使用 Fallback 模式")
            return await self._fallback_run()

    async def _fallback_run(self) -> dict:
        """Fallback 模式：當 LLM 不可用時使用模板生成計劃"""
        logger.info(f"[{self.name}] 使用 Fallback 模式生成計劃")

        plan = {
            "product_name": "MyAIProduct",
            "positioning": "AI-powered autonomous company operating system",
            "target_market": "Solo founders and small teams",
            "target_audience": "Technical entrepreneurs, indie hackers",
            "core_features": [
                "Auto code generation & deployment",
                "Automated marketing & ads",
                "AI customer support",
                "Financial tracking & invoicing"
            ],
            "value_proposition": "Run a complete company with AI agents while you sleep",
            "pricing": "$49/month",
            "brand_tone": "professional but approachable",
            "brand_colors": "#3B82F6 (blue), #10B981 (green)",
            "go_to_market": "Product-led growth + viral social media",
            "day1_actions": ["Set up business idea", "Generate execution plan", "Create landing page"],
            "day7_actions": ["Launch marketing campaign", "Deploy MVP", "Set up analytics dashboard"],
            "success_metrics": ["Monthly recurring revenue", "Customer acquisition cost", "Churn rate"],
        }

        self.log(tokens=0, status="plan_generated_fallback")
        return {
            "business_plan": plan,
            "tokens": 0,
            "mode": "fallback",
        }
