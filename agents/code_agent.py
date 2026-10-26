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
        sell_price = self.state.get("sell_price") or plan.get("price_twd_monthly", 1280)
        product_name = plan.get("product_name", "產品名稱")
        currency = self.state.get("currency", "TWD")
        lang = self.state.get("language", "zh-TW")
        is_bilingual = lang == "zh-TW+id"
        currency_symbol = {"TWD": "NT$", "USD": "$", "IDR": "Rp"}.get(currency, "NT$")
        price_str = f"{currency_symbol} {sell_price}"

        lang_instruction = {
            "zh-TW": "全部使用繁體中文（台灣用語），絕對不得使用簡體字",
            "en": "All content must be in English (US)",
            "id": "Semua konten harus dalam Bahasa Indonesia yang natural dan sehari-hari",
            "zh-TW+id": "全部使用繁體中文（台灣用語），絕對不得使用簡體字。雙語模式下需包含 id 區塊",
        }.get(lang, "全部使用繁體中文（台灣用語），絕對不得使用簡體字")

        bilingual_instruction = ""
        if is_bilingual:
            bilingual_instruction = """
【雙語模式特殊規範】
- 頁面需包含語言切換按鈕（中文 / Indonesia），預設顯示中文
- 所有文字內容都必須有兩個版本：繁體中文和 Bahasa Indonesia
- 價格、品牌名稱、公司名稱在兩種語言中必須完全一致，不可翻譯
- 未填寫的聯絡資料：中文寫「待店家填寫」，印尼文寫「Akan diisi oleh toko」
- 使用 data-lang="zh-TW" 和 data-lang="id" 屬性標記不同語言的內容
- 切換語言時只用前端 JavaScript 切換 visibility，不重新請求 AI
- 印尼文要用日常、自然的口語，像在台灣生活的印尼人會看懂的說法，不要逐字硬翻
"""

        return f"""
產品名稱：{product_name}
產品定位：{plan.get('positioning', 'SaaS 產品')}
目標受眾：{plan.get('target_audience', '技術創業者')}
核心功能：{', '.join(plan.get('core_features', ['功能 A', '功能 B', '功能 C']))}
品牌色調：{plan.get('brand_colors', '藍色系')}
用戶設定售價：{price_str}
幣別：{currency}

請生成一個完整的、響應式的 HTML Landing Page（單檔案，包含所有 CSS 和 JS），嚴格遵守以下規範：

【硬性規定】
1. {lang_instruction}
2. 【重要】商品價格必須嚴格使用 {price_str}，這是用戶設定的價格，你絕對不可以更改價格或換成其他幣別
3. 如果頁面有多個品項，以 {price_str} 為基準價格
4. 頁面標題和Logo必須使用「{product_name}」，與商業藍圖完全一致
5. 禁止編造聯絡資訊：地址、電話、Email、營業時間一律寫「待填寫」（英文：To be filled by the store，印尼文：Akan diisi oleh toko）
6. 禁止編造顧客見證、評價、銷量數據
7. 社群按鈕如有網址才顯示，沒有就隱藏
8. 不使用外部圖片連結，用 CSS 漸層、SVG 或 emoji 做視覺
9. 全部使用內嵌 CSS，單一 HTML 檔案可獨立運作

{bilingual_instruction}
【設計要求】
- 手機優先（Mobile First）響應式設計
- 首屏：大標題、一句吸引人的副標、明確的購買按鈕
- 賣點區塊：3-4 個具體優勢（不要空泛形容詞）
- 商品與價格區塊：明確標示售價 {price_str}
- 購買流程：清晰的 CTA 按鈕
- FAQ 區塊：3-5 個常見問題
- 頁尾：基本的版權聲明即可

【UI 品質】
- 配色與字型一致，符合行業特性
- 留白充足，圓角與陰影統一
- 字級層次清楚
- 手機底部固定一個「立即訂購」按鈕

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
