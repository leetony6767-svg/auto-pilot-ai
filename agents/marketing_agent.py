"""
Marketing Agent — 自動生成 TikTok 短影音行銷腳本

根據商業計劃生成 TikTok 短影音腳本（5支不同切角）
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
    """營銷 Agent：TikTok 短影音腳本自動化生成"""

    name = "marketing_agent"
    permission_level = PermissionLevel.EXECUTE
    cost_model = settings.agnes_model

    def __init__(self, state: BusinessState):
        super().__init__(state)
        self.plan = state.get("business_plan", {})

    async def run(self) -> dict:
        """主入口：生成 5 支 TikTok 短影音腳本 → 審批"""
        logger.info(f"[{self.name}] 開始生成 5 支 TikTok 短影音腳本")

        try:
            content_plan = await self._generate_content_plan()

            # 所有內容加入審批隊列
            self.add_approval(
                item_type="tiktok_scripts",
                content=content_plan,
                reason="5 支 TikTok 短影音腳本，需確認品牌和調性"
            )

            self.log(status="content_generated", posts=len(content_plan))
            logger.info(f"[{self.name}] 生成 {len(content_plan)} 支 TikTok 腳本，待審批")

            return {
                "content_generated": True,
                "posts_count": len(content_plan),
                "pending_approval": True,
                "content_plan": content_plan,
            }

        except Exception as e:
            self.log(status="error", error=str(e))
            logger.error(f"[{self.name}] 執行失敗: {e}")
            return {"error": str(e)}

    async def _generate_content_plan(self) -> list[dict]:
        """生成 5 支不同切角的 TikTok 短影音腳本"""
        from openai import AsyncOpenAI

        brand_tone = self.plan.get("brand_tone", "專業但有親和力")
        product_name = self.plan.get("product_name", "AgentOS")
        positioning = self.plan.get("positioning", "")
        target_audience = self.plan.get("target_audience", "")
        pricing_info = self.plan.get("pricing", "NT$ 1,280/月")
        price_value = self._extract_price_value(pricing_info)

        prompt = f"""你是一位顶级的 TikTok 内容营销专家，擅长创作高完播率、高互动率的短视频脚本。

請為以下產品創作 5 支 TikTok 短影音腳本，每支 15-30 秒。

產品：{product_name}
定位：{positioning}
目標受眾：{target_audience}
品牌調性：{brand_tone}
價格：{pricing_info}

🎯 5 支腳本必須各有不同切角：
1. 痛點型 — 直击用户痛点，引发共鸣
2. 開箱展示型 — 展示產品實際效果
3. 對比型 — 使用前 vs 使用後強烈對比
4. 情境故事型 — 真實生活場景代入
5. 限時優惠型 — 創造緊迫感和 FOMO

⚠️ 每個腳本必須包含以下結構：

【前3秒鉤子】一句會讓人立即停下來看的話（絕對不能在開頭說「大家好」、「今天來介紹」這種無聊開場）

【分鏡表】（每個鏡頭包含）：
- 畫面描述（視覺內容）
- 旁白或字幕文字
- 秒數（總長 15-30 秒）

【行動呼籲 CTA】明確告訴觀眾下一步動作

【建議配樂風格】適合的 BGM 類型（如： upbeat pop, lo-fi hip hop, trending sounds）

【建議 hashtag】5-8 個熱門標籤

📌 嚴格要求：
- 用目標客群的口吻，具體描述產品細節
- 避免空泛形容詞（如「完美相遇」「日常哲學」）
- 避免硬湊的口號
- 內容要有趣、有節奏感、適合 TikTok 短影音形式
- 絕對不能編造顧客見證、虛假評價、虛假銷量或療效保證
- 每支腳本約 15-30 秒，節奏要快

同時輸出 3 組廣告文案（標題 + 內文 + 行動呼籲），每組字數適合 TikTok 廣告（標題 ≤30 字，內文 ≤125 字）。

返回 JSON 數組，格式：
[{{
  "title": "痛點型：每天被工作淹沒？",
  "angle": "pain_point",
  "hook_3s": "前3秒鉤子文案",
  "storyboard": [
    {{"visual": "畫面描述", "narration": "旁白或字幕", "duration_sec": 5}},
    {{"visual": "畫面描述", "narration": "旁白或字幕", "duration_sec": 5}}
  ],
  "total_duration_sec": 25,
  "cta": "行動呼籲文字",
  "music_style": "建議配樂風格",
  "hashtags": ["#hashtag1", "#hashtag2"],
  "ad_copies": [
    {{"title": "廣告標題", "body": "廣告內文", "cta": "行動呼籲"}}
  ]
}}]"""

        client = AsyncOpenAI(
            api_key=settings.agnes_api_key,
            base_url=settings.agnes_base_url,
        )

        response = await client.chat.completions.create(
            model=self.cost_model,
            messages=[
                {"role": "system", "content": "你是 TikTok 短影音腳本專家，擅長創作 viral 內容，懂平台算法和用戶心理。輸出具體、生動、有節奏感。"},
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
            content_plan = self._generate_fallback_content(price_value)
        elif not isinstance(content_plan, list):
            content_plan = self._generate_fallback_content(price_value)
        elif len(content_plan) < 5:
            logger.warning(f"[{self.name}] 只生成 {len(content_plan)} 支腳本，補充至 5 支")
            content_plan += self._generate_fallback_content(price_value, offset=len(content_plan))

        # 添加元數據
        for i, post in enumerate(content_plan):
            post["id"] = f"tiktok-{i+1}-{self.state['user_id'][:6]}"
            post["generated_at"] = datetime.now().isoformat()
            post["platform"] = "tiktok"

        self.log(tokens=tokens, status="content_generated")
        logger.debug(f"[{self.name}] 生成 {len(content_plan)} 支 TikTok 腳本")

        return content_plan

    def _extract_price_value(self, pricing_info: str) -> int:
        """從定價文字中提取數值"""
        match = re.search(r'[\d,]+', pricing_info.replace(',', ''))
        if match:
            return int(match.group().replace(',', ''))
        return 1280

    def _generate_fallback_content(self, price_value: int = 1280, offset: int = 0) -> list[dict]:
        """LLM 不可用時的降级方案"""
        product_name = self.plan.get("product_name", "你的產品")
        angle_names = ["痛點型", "開箱展示型", "對比型", "情境故事型", "限時優惠型"]
        angle_keys = ["pain_point", "unboxing", "comparison", "story", "limited_offer"]

        content_plan = []
        today = datetime.now()

        for i in range(5):
            angle_idx = (i + offset) % 5
            title = f"{angle_names[angle_idx]}：{self._get_title(angle_idx)}"

            script = {
                "title": title,
                "angle": angle_keys[angle_idx],
                "hook_3s": self._get_hook(angle_idx),
                "storyboard": self._get_storyboard(angle_idx, product_name, price_value),
                "total_duration_sec": 20 + random.randint(0, 10),
                "cta": self._get_cta(angle_idx),
                "music_style": self._get_music_style(angle_idx),
                "hashtags": self._get_hashtags(angle_idx),
                "ad_copies": [
                    {
                        "title": f"{product_name} — {angle_names[angle_idx]}",
                        "body": f"想要{self._get_ad_body(angle_idx)}嗎？{product_name}幫你解決。現在只要 NT$ {price_value}/月。",
                        "cta": "立即訂閱"
                    }
                ]
            }
            content_plan.append(script)

        return content_plan

    @staticmethod
    def _get_title(idx: int) -> str:
        titles = [
            "每天被工作淹沒？這招救你",
            "開箱這個神器，太神了",
            "使用前 vs 使用後，差別超大",
            "原來他們都這樣做事",
            "最後 24 小時，錯過不再有"
        ]
        return titles[idx] if idx < len(titles) else titles[0]

    @staticmethod
    def _get_hook(idx: int) -> str:
        hooks = [
            "還在加班到凌晨？試試這個方法",
            "我不允許你還沒看過這個！",
            "同樣的工作時間，為什麼他比你快三倍？",
            "你有没有想過，為什麼別人總是比你輕鬆？",
            "限時優惠！現在不下單會後悔"
        ]
        return hooks[idx] if idx < len(hooks) else hooks[0]

    @staticmethod
    def _get_storyboard(idx: int, product: str, price: int) -> list:
        storyboards = [
            # 痛點型
            [
                {"visual": "一個人對電腦抓頭、疲憊的樣子", "narration": "每天早上醒來就想到一堆工作...", "duration_sec": 5},
                {"visual": "手機畫面展示 App 介面", "narration": f"直到我發現 {product}，AI 幫我自動處理", "duration_sec": 5},
                {"visual": "輕鬆喝咖啡、看手機 notification", "narration": "現在我準時下班，還有時間陪家人", "duration_sec": 5},
                {"visual": "App logo + CTA 按鈕", "narration": "免費試用七天，連結在限時動態", "duration_sec": 3}
            ],
            # 開箱展示型
            [
                {"visual": "拆開產品包裝的特寫", "narration": "剛拿到 {product}，第一眼...", "duration_sec": 4},
                {"visual": "快速滑動 App 介面", "narration": "介面超直覺，五分鐘就上手", "duration_sec": 4},
                {"visual": "展示功能運作中的畫面", "narration": "重點是！這些功能都已經幫你自動跑了", "duration_sec": 5},
                {"visual": "滿意微笑 + App 截圖", "narration": f" NT$ {price}/月，真的超值", "duration_sec": 4}
            ],
            # 對比型
            [
                {"visual": "左邊：亂糟糟的桌面，右邊：整潔乾淨", "narration": "以前 vs 現在，差距超誇張", "duration_sec": 5},
                {"visual": "左邊：手忙腳亂，右邊：悠閒喝茶", "narration": "以前要花三小時，現在三分鐘搞定", "duration_sec": 5},
                {"visual": "中間：App 介面特寫", "narration": "只差一個 {product}", "duration_sec": 4},
                {"visual": "右邊畫面放大 + CTA", "narration": "你也想變得跟他一樣輕鬆嗎？", "duration_sec": 4}
            ],
            # 情境故事型
            [
                {"visual": "咖啡廳裡一個看起来很忙碌的人", "narration": "她以前每天都要做到晚上十點", "duration_sec": 5},
                {"visual": "畫面切換：她在旅行的照片", "narration": "現在？她上个月去墾丁玩了三天", "duration_sec": 5},
                {"visual": "手機螢幕展示 App", "narration": "關鍵是用了 {product}，把重複性工作全交給 AI", "duration_sec": 5},
                {"visual": "她對著鏡頭微笑", "narration": "你也值得擁有更多自由時間", "duration_sec": 4}
            ],
            # 限時優惠型
            [
                {"visual": "倒數計時器動畫", "narration": "注意！這個優惠只剩最後 24 小時", "duration_sec": 4},
                {"visual": "產品功能快速閃過", "narration": f"{product} 全功能開放，NT$ {price}/月", "duration_sec": 5},
                {"visual": "紅色警告標語 + 閃爍效果", "narration": "明天就漲價，現在註冊還送一個月", "duration_sec": 5},
                {"visual": "大按鈕「立即免費試用」", "narration": "點下方連結，立刻搶跑！", "duration_sec": 4}
            ]
        ]
        sb = storyboards[idx] if idx < len(storyboards) else storyboards[0]
        return [{"visual": s["visual"], "narration": s["narration"].format(product=product, price=price), "duration_sec": s["duration_sec"]} for s in sb]

    @staticmethod
    def _get_cta(idx: int) -> str:
        ctas = [
            "立即免費試用，改變你的工作方式",
            "點擊連結，今天就開始體驗",
            "别再落後，點下方連結了解詳情",
            "分享給需要的朋友，一起輕鬆工作",
            "限時優惠倒數中，趕快行動！"
        ]
        return ctas[idx] if idx < len(ctas) else ctas[0]

    @staticmethod
    def _get_music_style(idx: int) -> str:
        styles = [
            "Upbeat corporate pop — 有活力但不吵雜，適合效率主題",
            "Trending lo-fi hip hop — 放鬆舒適的節奏感",
            "Dynamic electronic — 節奏強烈，對比其他類內容很適合",
            "Acoustic folk — 溫馨有故事感，適合人生故事",
            "Fast-paced hyperpop — 緊湊有力，創造緊迫感"
        ]
        return styles[idx] if idx < len(styles) else styles[0]

    @staticmethod
    def _get_hashtags(idx: int) -> list:
        hashtag_sets = [
            ["#AI", "#工作效率", "#創業", "#自動化", "#Productivity"],
            ["#開箱", "#好物推薦", "#AI工具", "#創業日常", "#效率神器"],
            ["#beforeandafter", "#改變", "#AI時代", "#工作效率", "#創業"],
            ["#故事", "#創業故事", "#AI生活", "#工作平衡", "#靈感"],
            ["#限時優惠", "#優惠", "#折扣", "#AI工具", "#早鳥價"]
        ]
        return hashtag_sets[idx] if idx < len(hashtag_sets) else hashtag_sets[0]

    @staticmethod
    def _get_ad_body(idx: int) -> str:
        bodies = [
            "每天省下三小時，專心做重要的事",
            "讓 AI 幫你處理瑣碎工作",
            "用一半時間完成兩倍的工作量",
            "像其他人一樣輕鬆又高效",
            "抓住這次機會，別等漲價才後悔"
        ]
        return bodies[idx] if idx < len(bodies) else bodies[0]
