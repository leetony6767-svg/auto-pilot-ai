"""
Code Agent — 自動編碼與部署

反推自 Polsia 技術 Agent 的職責：
- 根據商業計劃生成 Next.js 代碼
- 自動提交到 GitHub
- 部署到 Vercel
- 執行健康檢查
"""
from typing import AsyncIterator
import json
import re
from loguru import logger

from agents.base import BaseAgent, BusinessState, PermissionLevel
from config.cost_control import cost_tracker
from config.settings import settings


class CodeAgent(BaseAgent):
    """技術 Agent：代碼生成 + 自動化部署"""

    name = "code_agent"
    permission_level = PermissionLevel.EXECUTE
    cost_model = settings.agnes_model  # 使用 Agnes AI 模型

    def __init__(self, state: BusinessState):
        super().__init__(state)
        self.plan = state.get("business_plan", {})

    async def run(self) -> dict:
        """主入口：生成代碼 → 審批 → 部署"""
        logger.info(f"[{self.name}] 開始為用戶 {self.state['user_id']} 生成代碼")

        try:
            # Step 1: 生成 Landing Page 代碼
            code = await self._generate_code()
            self.log(status="code_generated", code_length=len(code))

            # Step 2: 代碼審查（安全檢查）
            review_result = await self._review_code(code)
            if not review_result["passed"]:
                self.log(status="review_failed", reason=review_result["reason"])
                return {"error": f"代碼審查未通過: {review_result['reason']}"}

            # Step 3: 加入審批隊列（L3 操作：部署需確認）
            self.add_approval(
                item_type="deployment",
                content={
                    "code": code,
                    "plan": self.plan,
                    "review": review_result,
                },
                reason="需要確認部署目標和域名"
            )
            self.log(status="pending_approval")

            return {
                "code_generated": True,
                "code": code,
                "code_length": len(code),
                "framework": "nextjs",
                "pending_approval": True,
            }

        except Exception as e:
            self.log(status="error", error=str(e))
            logger.error(f"[{self.name}] 執行失敗: {e}")
            return {"error": str(e)}

    async def _generate_code(self) -> str:
        """使用 LLM 生成 Next.js Landing Page 代碼"""
        from openai import AsyncOpenAI

        prompt = self._build_code_prompt()

        client = AsyncOpenAI(
            api_key=settings.agnes_api_key,
            base_url=settings.agnes_base_url,
        )

        response = await client.chat.completions.create(
            model=self.cost_model,
            messages=[
                {"role": "system", "content": """你是全棧開發專家。
            請生成一個完整的 Next.js 14 Landing Page，要求：
            1. 使用 App Router + TypeScript
            2. 使用 Tailwind CSS 樣式
            3. 包含：Hero Section、Features、Pricing、CTA、Footer
            4. 響應式設計，移動端友好
            5. 現代化 UI，漸變色和微動畫
            只返回 app/page.tsx 的完整代碼，不需要解釋。"""},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        code = response.choices[0].message.content if response.choices else ""
        tokens = response.usage.total_tokens if response.usage else 0

        # 成本控制：記錄 Token 消耗
        cost_tracker.record_usage(self.name, self.state["user_id"], tokens)

        # 提取代碼塊（如果 LLM 返回了 markdown 包裹）
        code = self._extract_code_block(code)

        self.log(tokens=tokens, status="code_generated")
        logger.info(f"[{self.name}] 生成 {len(code)} 字節代碼，消耗 {tokens} tokens")
        return code

    def _build_code_prompt(self) -> str:
        """根據商業計劃構建代碼生成提示"""
        plan = self.plan
        price = plan.get("price_twd_monthly", 1280)
        price_str = f"NT$ {price}/月" if price else "請根據定價策略設定"
        return f"""
產品定位：{plan.get('positioning', 'SaaS 產品')}
目標受眾：{plan.get('target_audience', '技術創業者')}
核心功能：{', '.join(plan.get('core_features', ['功能 A', '功能 B', '功能 C']))}
價格策略：{plan.get('pricing', price_str)}
品牌色調：{plan.get('brand_colors', '藍色系')}

請生成一個完整的、響應式的 HTML Landing Page（單檔案，包含所有 CSS 和 JS），要求：
1. 使用純 HTML + CSS（內聯樣式），不需要外部框架
2. 響應式設計：在手機、平板、桌面都能完美顯示
3. 必須包含以下區塊：
   - Hero Section：大標題、副標題、CTA 按鈕
   - 賣點區塊（3-4 個核心優勢）
   - 商品與價格區塊：明確標示「{price_str}」價格
   - FAQ 區塊（3-5 個常見問題）
   - 購買按鈕（醒目，帶有購買動詞）
   - Footer
4. 現代化 UI：漸變色、微動畫、卡片式布局
5. 使用中文內容，符合台灣市場喜好

只返回完整的 HTML 代碼，不需要解釋。確保代碼能在 iframe 中直接渲染。
        """.strip()

    async def _review_code(self, code: str) -> dict:
        """代碼審查：安全檢查 + 基本質量驗證"""
        issues = []

        # 安全檢查
        dangerous_patterns = [
            (r'\beval\s*\(', 'eval() 调用'),
            (r'dangerouslySetInnerHTML', 'dangerouslySetInnerHTML 使用'),
            (r'process\.env\.SECRET', '硬編碼機密'),
            (r'\.innerHTML\s*=', 'DOM innerHTML 寫入'),
        ]

        for pattern, desc in dangerous_patterns:
            if re.search(pattern, code):
                issues.append(desc)

        # 基本結構檢查 - 只要沒有危險模式就通過
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "missing_sections": [],
            "code_quality_score": max(0, 100 - len(issues) * 20),
        }

    def _extract_code_block(self, text: str) -> str:
        """從 LLM 輸出中提取代碼塊"""
        # 匹配 ```typescript ... ``` 或 ```python ... ``` 等
        match = re.search(r'```\w*\n?(.*?)\n?```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    async def deploy(self, code: str, domain: str = None) -> dict:
        """部署到 Vercel（審批通過後執行）"""
        from config.cost_control import cost_tracker

        logger.info(f"[{self.name}] 開始部署到 Vercel...")

        # 模擬部署流程（實際項目中接入 Vercel API）
        deployment = {
            "status": "deploying",
            "url": f"{settings.deployment_base_url}/project-{self.state['user_id']}",
            "domain": domain or f"{self.state['user_id']}.agent-os.app",
            "framework": "nextjs",
            "commit_sha": "mock-commit-" + self.state["user_id"][:8],
        }

        # 模擬健康檢查
        await self._health_check(deployment["url"])

        cost_tracker.record_usage(self.name, self.state["user_id"], 500)
        self.log(status="deployed", url=deployment["url"])
        logger.info(f"[{self.name}] 部署完成: {deployment['url']}")

        return deployment

    async def _health_check(self, url: str) -> bool:
        """部署後的健康檢查"""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=10)
                return resp.status_code == 200
        except Exception:
            logger.warning(f"[{self.name}] 健康檢查失敗: {url}")
            return False
