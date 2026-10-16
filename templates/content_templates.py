"""
社媒內容模板庫

用於 fallback 模式（LLM 不可用時）和作為 prompt 參考
"""

# ── Twitter/X 貼文模板 ────────────────────────────────────────
TWITTER_TEMPLATES = [
    {
        "theme": "產品介紹",
        "hook": "🚀",
        "template": """{hook} Day 1:  INTRODUCING {product_name}

我們相信，每個創客都值得擁有一支 24/7 的 AI 團隊。

{value_prop}

不需要工程師、不需要市場預算、不需要客服人員。

只需要一個好想法 + {product_name}。

{cta}

#{hashtag1} #{hashtag2} #{hashtag3}""",
        "image_prompt": "Modern workspace with AI dashboard, clean minimalist design, blue gradient accents",
    },
    {
        "theme": "行業洞察",
        "hook": "💡",
        "template": """{hook} 一個讓人震驚的數字：

到 2026 年，超過 {stat}% 的初創公司将使用 AI Agent 運營。

不是「輔助」，是完全自治。

這不是未來式，是現在式。

{product_name} 已經在運行 {companies}+ 家 AI 自治公司。

你準備好了嗎？

#{hashtag1} #{hashtag2}""",
        "image_prompt": "Futuristic cityscape with AI elements, data visualization overlay",
    },
    {
        "theme": "用戶故事",
        "hook": "📖",
        "template": """{hook} 真實用戶故事：

「我用 {product_name} 在 48 小時內搭建了我的 SaaS 產品，
第一週就獲得了 100 個付費用戶。」

— @real_user

這不是自動化工具，這是你的 AI 合夥人。

#{hashtag1} #{hashtag2} #{hashtag3}""",
        "image_prompt": "Happy entrepreneur working from laptop in cafe, success moment",
    },
    {
        "theme": "幕後花絮",
        "hook": "🎬",
        "template": """{hook} 幕後：我們如何用 AI 運營一家公司

• CEO 決策 → AI Agent
• 寫代码 → AI Agent  
• 投放廣告 → AI Agent
• 客服回覆 → AI Agent
• 財務對帳 → AI Agent

人類只做一件事：設定方向。

剩下的，交給 AI。

#{hashtag1} #{hashtag2}""",
        "image_prompt": "Behind-the-scenes office with multiple screens showing AI dashboards",
    },
    {
        "theme": "互動內容",
        "hook": "❓",
        "template": """{hook} 提問時間：

如果你可以擁有一個 AI 員工，你最希望 Ta 幫你做什麼？

A) 寫代码
B) 做營銷  
C) 回郵件
D) 全部都要 😏

回答下面 👇

#{hashtag1} #{hashtag2}""",
        "image_prompt": "Question mark made of AI/tech elements, interactive poll style",
    },
    {
        "theme": "教育性內容",
        "hook": "📚",
        "template": """{hook} 5 個步驟，用 AI Agent 啟動你的第一家公司：

1️⃣ 輸入你的商業構想
2️⃣ AI 生成執行計劃
3️⃣ AI 自動編碼 & 部署網站
4️⃣ AI 開始投放廣告 & 獲取客戶
5️⃣ 你审阅結果，做關鍵決策

全程 24/7 自動運行。

第 6 步：睡覺 😴

完整的指南在 bio。

#{hashtag1} #{hashtag2} #{hashtag3}""",
        "image_prompt": "Step-by-step infographic style, numbered steps with AI icons",
    },
    {
        "theme": "促銷活動",
        "hook": "🔥",
        "template": """{hook} 限時優惠：

前 100 名用戶享受：
✅ 首月免費
✅ 1對1 啟動指導
✅ 終身折扣價

機會只屬於行動派。

鏈接在 bio 👆

#{hashtag1} #{hashtag2}""",
        "image_prompt": "Urgency style with countdown timer, bold typography, red/orange accents",
    },
]

# ── LinkedIn 貼文模板 ─────────────────────────────────────────
LINKEDIN_TEMPLATES = [
    {
        "theme": "產品介紹",
        "template": """我在思考一個問題：

如果「僱人」變成「下指令」，商業會變成什麼樣子？

過去 10 年，我見證了太多創始人因為以下原因失敗：
• 找不到技術合夥人
• 行銷預算不夠
• 客服跟不上需求
• 財務管理混亂

每個痛點都需要一個團隊來解決。

但今天，AI 改變了一切。

我剛完成了一個項目：用 AI Agent 運營一家完整的公司。

9 個 AI Agent，分工明確：
→ CEO Agent 制定戰略
→ 技術 Agent 寫 code、部署網站
→ 營銷 Agent 投放廣告、生成內容
→ 客服 Agent 7x24 處理諮詢
→ 財務 Agent 對帳、開發票
→ ...等等

用戶只需輸入一個商業構想，AI 完成剩餘的一切。

這不是科幻。這已經在發生了。

{product_name} 正在讓「一人公司」成為可規模化的商業模式。

你在創業路上最大的痛點是什麼？歡迎在評論區分享 👇

#{hashtag1} #{hashtag2} #{hashtag3} #{hashtag4}""",
    },
    {
        "theme": "行業洞察",
        "template": """數據說話：2026 年 AI Agent 產業正在經歷什麼？

📊 关键數字：
• 全球 AI Agent 市場規模：$XX 億（+XXX% YoY）
• 一人公司數量：6 年內增長 53%
• AI 推理成本：過去 2 年下降超過 95%
• Polsia 等平台的用戶數：從 0 到 7,600+（僅 6 個月）

這不是趨勢，這是拐點。

我觀察到的三個信號：

1️⃣ 「Agent 操作系統」正在成為新的 SaaS 品類
以前的 SaaS 是「工具」——幫你做一件事。
現在的 Agent OS 是「員工」——幫你運營整個業務。

2️⃣ 成本曲線已經跨越臨界點
當 AI 推理成本下降到一定程度，「僱 AI 员工」比「僱真人」更經濟。
Polsia 的經驗：從 $120萬/月 AI 帳單降到 $10萬/月，
關鍵是模型分級 + 開源替代。

3️⃣ 數據網絡效應開始顯現
跨公司的學習數據形成飛輪：
用戶越多 → 知識庫越豐富 → Agent 越智能 → 吸引更多用戶

這才是真正的護城河。

你在觀察哪些 AI Agent 的應用場景？

#{hashtag1} #{hashtag2} #{hashtag3}""",
    },
]

# ── 模板渲染工具 ──────────────────────────────────────────────
def render_twitter_template(template_key: str, context: dict) -> dict:
    """渲染 Twitter 模板"""
    template = TWITTER_TEMPLATES[template_key % len(TWITTER_TEMPLATES)]
    context.setdefault("product_name", "AgentOS")
    context.setdefault("value_prop", "AI-powered autonomous company operating system")
    context.setdefault("cta", "👉 免費開始：agent-os.app")
    context.setdefault("hashtag1", "AI")
    context.setdefault("hashtag2", "Startup")
    context.setdefault("hashtag3", "SoloFounder")
    context.setdefault("stat", "70")
    context.setdefault("companies", "7600")

    copy = template["template"].format(**context)
    # 確保不超過 280 字符
    if len(copy) > 280:
        copy = copy[:277] + "..."

    return {
        "copy": copy,
        "hashtags": template.get("hashtags", ["#AI", "#Startup"]),
        "image_prompt": template["image_prompt"],
        "theme": template["theme"],
    }


def render_linkedin_template(template_key: str, context: dict) -> dict:
    """渲染 LinkedIn 模板"""
    template = LINKEDIN_TEMPLATES[template_key % len(LINKEDIN_TEMPLATES)]
    context.setdefault("product_name", "AgentOS")
    context.setdefault("hashtag1", "AI")
    context.setdefault("hashtag2", "Startup")
    context.setdefault("hashtag3", "Entrepreneurship")
    context.setdefault("hashtag4", "SoloFounder")

    return {
        "copy": template["template"].format(**context),
        "hashtags": ["#AI", "#Startup", "#Entrepreneurship"],
        "theme": template["theme"],
    }
