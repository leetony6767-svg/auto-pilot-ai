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
    cost_model = settings.agnes_model  # 使用 Agnes AI 模型

    async def run(self) -> dict:
        """主入口：分析商業構想，生成執行計劃"""
        logger.info(f"[{self.name}] 開始分析商業構想: {self.state['business_idea'][:50]}...")

        try:
            from openai import AsyncOpenAI

            lang = self.state.get("language", "zh-TW")
            lang_name = {"zh-TW": "繁體中文", "en": "English", "id": "Bahasa Indonesia", "zh-TW+id": "繁體中文+Bahasa Indonesia"}.get(lang, "繁體中文")
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
              "price_twd_monthly": 1280,
              "price_usd_monthly": 42,
              "currency": "TWD",
              "brand_tone": "品牌調性",
              "brand_colors": "推薦配色方案",
              "go_to_market": "Go-to-Market 策略",
              "day1_actions": ["第1天要做的3件事"],
              "day7_actions": ["第7天要做的3件事"],
              "success_metrics": ["關鍵成功指標"],
              "platform_fee_percent": 8,
              "platform_revenue_share": 0.92
            }}

            注意：product_name、pricing、value_proposition 請使用 {lang_name} 輸出。
            請確保計劃具體、可執行，並針對該商業領域提出專業建議。"""

            client = AsyncOpenAI(
                api_key=settings.agnes_api_key,
                base_url=settings.agnes_base_url,
            )

            response = await client.chat.completions.create(
                model=self.cost_model,  # agnes-2.5-flash
                messages=[
                    {"role": "system", "content": "你是 Top-tier 創業顧問，幫助創始人將想法轉化為可執行的商業計劃。輸出精確、具體、可操作。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )

            tokens = response.usage.total_tokens if response.usage else 0
            cost_tracker.record_usage(self.name, self.state["user_id"], tokens)

            # 解析 JSON（處理 markdown 程式碼塊包裹）
            content = response.choices[0].message.content if response.choices else ""
            from agents.utils import parse_llm_json
            success, plan, error = parse_llm_json(content)
            if not success:
                logger.warning(f"[{self.name}] JSON 解析失敗: {error}")
                plan = {"raw_response": content}
            else:
                plan = plan

            self.log(tokens=tokens, status="plan_generated")
            logger.info(f"[{self.name}] 計劃生成完成: {plan.get('product_name', '未知產品')}")

            return {
                "business_plan": plan,
                "tokens": tokens,
            }

        except ImportError:
            logger.warning(f"[{self.name}] LLM client unavailable, using fallback mode")
            return await self._fallback_run()
        except (ValueError, Exception) as e:
            error_str = str(e)
            # 檢查是否是認證錯誤（缺少 API Key）
            if "authentication" in error_str.lower() or "api_key" in error_str.lower() or not settings.agnes_api_key:
                logger.warning(f"[{self.name}] 未配置 Agnes API Key，使用 Fallback 模式")
                return await self._fallback_run()
            logger.warning(f"[{self.name}] LLM 调用失败: {e}，使用 Fallback 模式")
            return await self._fallback_run()

    async def _fallback_run(self) -> dict:
        """Fallback 模式：當 LLM 不可用時使用模板生成計劃"""
        logger.info(f"[{self.name}] 使用 Fallback 模式生成計劃")

        # 根據用戶的商業構想生成相關性更高的模板
        idea = self.state.get("business_idea", "")

        plan = {
            "product_name": self._extract_product_name(idea),
            "positioning": self._generate_positioning(idea),
            "target_market": "對該產品/服務有興趣的潛在客戶群",
            "target_audience": self._extract_target_audience(idea),
            "core_features": [
                f"基於 '{idea}' 的核心功能 1",
                f"針對目標受眾的功能 2",
                f"提升用戶體驗的功能 3",
            ],
            "value_proposition": f"為 {self._extract_target_audience(idea)} 提供專業的 {idea} 解決方案",
            "pricing": "NT$ 1,280/月（台灣市場）或 $42/月（國際市場）",
            "price_twd_monthly": 1280,
            "price_usd_monthly": 42,
            "currency": "TWD",
            "brand_tone": "專業且親切",
            "brand_colors": "#3B82F6 (藍色), #10B981 (綠色)",
            "go_to_market": "內容營銷 + 社交媒體 + SEO",
            "day1_actions": ["確認商業構想細節", "生成執行計劃", "創建 Landing Page"],
            "day7_actions": ["啟動營銷活動", "上線 MVP", "設置數據分析儀表板"],
            "success_metrics": ["月收入增長", "客戶獲取成本", "用戶留存率"],
            "mode": "fallback",
            "note": "此為模板模式，建議配置 Agnes API Key 以獲取真實 AI 生成內容",
        }

        self.log(tokens=0, status="plan_generated_fallback")
        return {
            "business_plan": plan,
            "tokens": 0,
            "mode": "fallback",
        }

    @staticmethod
    def _extract_product_name(idea: str) -> str:
        """從商業構想中提取產品名稱"""
        # 簡單邏輯：提取關鍵詞
        keywords = idea.split()
        if len(keywords) >= 2:
            return " ".join(keywords[:3]).title()
        return idea.title() if idea else "MyProduct"

    @staticmethod
    def _generate_positioning(idea: str) -> str:
        """根據構想生成產品定位"""
        return f"專業的 {idea} 解決方案"

    @staticmethod
    def _extract_target_audience(idea: str) -> str:
        """從構想中提取目標受眾"""
        # 簡單邏輯：提取「給」之後的內容
        if "給" in idea:
            return idea.split("給")[-1].strip()
        elif "向" in idea:
            return idea.split("向")[-1].strip()
        return "潛在客戶"
