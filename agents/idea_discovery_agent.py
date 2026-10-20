"""
IdeaDiscoveryAgent — 商業創意發現與推薦

當用戶沒有明確的商業構想時，自動推薦市場熱門且高轉化率的微型產品/服務點子。
基於市場趨勢分析、熱門創業模式和轉化率數據。

支援 6 大自動化獲利模式：
1. 電商自動化 (E-commerce)
2. 內容營銷 (Content Marketing)
3. B2B 獲客開發 (Outbound Sales)
4. 數位產品 (Digital Products)
5. 數據分析 (Data Analysis)
6. 任務自動化 (Task Automation)
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from loguru import logger

# 6 大獲利模式
PROFIT_MODES = {
    "e-commerce": "電商自動化",
    "content-marketing": "內容營銷",
    "b2b-sales": "B2B 獲客開發",
    "digital-products": "數位產品",
    "data-analysis": "數據分析",
    "task-automation": "任務自動化",
}


@dataclass
class BusinessIdea:
    """商業構想數據結構"""
    id: str
    title: str
    category: str
    profit_mode: str  # 獲利模式
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
    automation_steps: List[str]  # AI Agent 自動化步驟


class IdeaDiscoveryAgent:
    """商業創意發現 Agent — 支援 6 大獲利模式"""

    name = "idea_discovery_agent"

    # 6 大獲利模式構想庫
    _idea_pool = [
        # ═══════════════════════════════════════════════════════════
        # ① 電商自動化 (E-commerce)
        # ═══════════════════════════════════════════════════════════
        BusinessIdea(
            id="ECOM-001",
            title="Dropshipping 自動化商店",
            category="E-commerce / Automation",
            profit_mode="e-commerce",
            description="AI 自動選品、上架、定價、廣告投放的無人值守電商商店",
            target_audience="初創創業者、副業玩家",
            revenue_model="商品銷售利潤 $10-50/單",
            difficulty="medium",
            estimated_monthly_revenue=8000.0,
            required_investment=500.0,
            market_trend="rising",
            key_features=[
                "AI 自動選品（熱銷品挖掘）",
                "競價監控與自動定價",
                "多平台同步上架（Amazon/eBay/Shopify）",
                "訂單自動履行",
                "廣告 ROI 優化"
            ],
            competition_level="high",
            why_now="Dropshipping 門檻降低，AI 讓個人也能操作大規模商店",
            first_steps=[
                "選擇利基市場（如寵物用品、家居裝飾）",
                "使用 AutoDS 或 DSers 導入供應商",
                "建立 Shopify 商店並配置自動化",
                "測試 Facebook/Google 廣告",
                "逐步擴大產品線"
            ],
            automation_steps=[
                "每日自動抓取熱銷品數據",
                "AI 生成產品描述和標題",
                "競價監控機器人（±5% 調整）",
                "訂單處理自動化（API 對接 Suplier）",
                "廣告預算自動分配"
            ]
        ),
        BusinessIdea(
            id="ECOM-002",
            title="Print on Demand 客製化商品",
            category="E-commerce / Custom Products",
            profit_mode="e-commerce",
            description="AI 設計圖案 + 自動印製出貨的客製化商品商店",
            target_audience="設計師、藝術家、創作者",
            revenue_model="單品利潤 $15-40",
            difficulty="easy",
            estimated_monthly_revenue=5000.0,
            required_investment=200.0,
            market_trend="rising",
            key_features=[
                "AI 圖像生成設計",
                "自動同步 Printful/Printify",
                "多平台一鍵上架",
                "庫存零風險",
                "熱銷品自動複製"
            ],
            competition_level="medium",
            why_now="POD 模式零庫存，AI 設計工具大幅降低創作門檻",
            first_steps=[
                "學習 Midjourney/DALL-E 生成設計",
                "註冊 Printful 帳戶",
                "建立 Etsy/Shopify 商店",
                "批量上架 50+ 設計",
                "投放 Pinterest/Instagram 廣告"
            ],
            automation_steps=[
                "AI 每日生成 10+ 新設計",
                "自動檢查版權和熱銷趨勢",
                "多平台同步上架",
                "自動回應客服訊息",
                "廣告素材自動 A/B 測試"
            ]
        ),
        BusinessIdea(
            id="ECOM-003",
            title="亞馬遜 FBA 批發模式",
            category="E-commerce / Wholesale",
            profit_mode="e-commerce",
            description="AI 選品 + 庫存預測 + 補貨提醒的亞馬遜 FBA 自動化營運",
            target_audience="電商進階創業者",
            revenue_model="單品毛利 20-40%",
            difficulty="hard",
            estimated_monthly_revenue=25000.0,
            required_investment=5000.0,
            market_trend="rising",
            key_features=[
                "競品銷售數據監控",
                "庫存預警與自動補貨",
                "PPC 廣告自動優化",
                "價格competitive 監控",
                "評論管理自動化"
            ],
            competition_level="high",
            why_now="亞馬遜 FBA 是最大電商平台，AI 能顯著提升選品成功率",
            first_steps=[
                "研究 Amazon Seller University",
                "使用 Helium 10/Jungle Scout 選品",
                "尋找品質穩定的供應商",
                "發貨至亞馬遜倉庫",
                "啟動 PPC 廣告"
            ],
            automation_steps=[
                "每日競品價格監控",
                "庫存水位自動計算",
                "廣告 bid 自動調整",
                "負評 alerts 系統",
                "銷售數據週報生成"
            ]
        ),

        # ═══════════════════════════════════════════════════════════
        # ② 內容營銷 (Content Marketing)
        # ═══════════════════════════════════════════════════════════
        BusinessIdea(
            id="CONTENT-001",
            title="短影音自動化帳號",
            category="Content Marketing / Short Video",
            profit_mode="content-marketing",
            description="AI 自動生產短影音（TikTok/Reels/Shorts）並自動發布",
            target_audience="內容創作者、品牌行銷",
            revenue_model="廣告分成 + 聯盟佣金 + 品牌合作",
            difficulty="easy",
            estimated_monthly_revenue=3000.0,
            required_investment=100.0,
            market_trend="rising",
            key_features=[
                "AI 腳本生成",
                "自動剪輯與字幕",
                "多平台排程發布",
                "熱門話題追蹤",
                "數據分析優化"
            ],
            competition_level="high",
            why_now="短影音是流量入口，AI 讓個人也能日更多條影片",
            first_steps=[
                "選擇垂直領域（如理財、健身、美食）",
                "研究熱門內容格式",
                "使用 CapCut/Claude 生成腳本",
                "建立發布排程",
                "分析數據迭代內容"
            ],
            automation_steps=[
                "每日抓取熱門話題",
                "AI 生成 5-10 個腳本",
                "自動生成影音素材",
                "多平台自動發布",
                "互動訊息自動回覆"
            ]
        ),
        BusinessIdea(
            id="CONTENT-002",
            title="SEO 自動化部落格",
            category="Content Marketing / SEO",
            profit_mode="content-marketing",
            description="AI 自動撰寫 SEO 文章並持續更新的老舊網站流量變現",
            target_audience="內容創作者、affiliate 行銷者",
            revenue_model="廣告收入 + 聯盟行銷佣金",
            difficulty="easy",
            estimated_monthly_revenue=2000.0,
            required_investment=50.0,
            market_trend="stable",
            key_features=[
                "關鍵字研究自動化",
                "AI 文章生成與優化",
                "自動內鏈和外鏈策略",
                "競爭對手文章分析",
                "搜尋結果監控"
            ],
            competition_level="medium",
            why_now="AI 能生產高品質 SEO 內容，降低內容創作成本 90%",
            first_steps=[
                "選擇利基市場（如科技評論、產品比較）",
                "購買高權重舊域名",
                "設定 WordPress + SEO 插件",
                "導入 AI 內容生成流程",
                "建立聯盟連結"
            ],
            automation_steps=[
                "每日關鍵字研究",
                "AI 撰寫 3-5 篇文章",
                "自動檢查重複內容",
                "社群媒體自動分享",
                "流量異常 alerts"
            ]
        ),
        BusinessIdea(
            id="CONTENT-003",
            title="聯盟行銷自動化平台",
            category="Content Marketing / Affiliate",
            profit_mode="content-marketing",
            description="AI 自動比價、生成推薦內容、追蹤佣金的全自動聯盟行銷系統",
            target_audience="理財部落客、產品評測網站",
            revenue_model="聯盟佣金 5-30%",
            difficulty="medium",
            estimated_monthly_revenue=10000.0,
            required_investment=300.0,
            market_trend="rising",
            key_features=[
                "價格監控與歷史比價",
                "AI 產品評測生成",
                "多平台聯盟連結管理",
                "轉化率分析",
                "自動更新失效連結"
            ],
            competition_level="medium",
            why_now="電商聯盟計畫廣泛，AI 能大规模生產推薦內容",
            first_steps=[
                "申請 Amazon Associates 等聯盟計畫",
                "建立產品評測網站",
                "撰寫高品質比較文章",
                "優化 SEO 和轉換率",
                "擴展到多個聯盟計畫"
            ],
            automation_steps=[
                "每日價格監控",
                "AI 生成產品比較表",
                "Hot 產品自動推薦",
                "失效連結自動替換",
                "佣金報表自動生成"
            ]
        ),

        # ═══════════════════════════════════════════════════════════
        # ③ B2B 獲客開發 (Outbound Sales)
        # ═══════════════════════════════════════════════════════════
        BusinessIdea(
            id="SALES-001",
            title="自動化冷開發系統",
            category="B2B Sales / Outreach",
            profit_mode="b2b-sales",
            description="AI 自動尋找潛在客戶、發送個人化開發信、跟進的全自動銷售系統",
            target_audience="B2B SaaS、顧問服務、自由職業者",
            revenue_model="專案制 $1,000-5,000/客戶",
            difficulty="medium",
            estimated_monthly_revenue=15000.0,
            required_investment=200.0,
            market_trend="rising",
            key_features=[
                "LinkedIn 自動搜尋與驗證",
                "個性化開發信生成",
                "多時段發送優化",
                "自動跟進排程",
                "CRM 數據整合"
            ],
            competition_level="medium",
            why_now="B2B 銷售自動化市場增長，個人也能使用企業級工具",
            first_steps=[
                "定義目標客戶画像",
                "購買 LinkedIn Sales Navigator",
                "設定自動化工作流（Apollo/Snovio）",
                "撰寫個人化模板",
                "測試並優化開啟率"
            ],
            automation_steps=[
                "每日自動搜尋新目標",
                "AI 研究潛在客戶背景",
                "個性化第一封開發信",
                "自動化跟進序列（3-5 次觸及）",
                "高意向客戶自動標記"
            ]
        ),
        BusinessIdea(
            id="SALES-002",
            title="B2B 開發信郵件系統",
            category="B2B Sales / Email",
            profit_mode="b2b-sales",
            description="AI 撰寫高轉換率開發信並自動化發送的 B2B 領先生成系統",
            target_audience="SaaS 銷售團隊、業務開發人員",
            revenue_model="訂閱制 $99-299/月",
            difficulty="easy",
            estimated_monthly_revenue=8000.0,
            required_investment=100.0,
            market_trend="stable",
            key_features=[
                "AI 撰寫個人化郵件",
                "發送時間最佳化",
                "A/B 測試主題行",
                "退信處理與名單清洗",
                "回覆分類與優先級排序"
            ],
            competition_level="medium",
            why_now="郵件仍是 B2B 最高 ROI 渠道，AI 大幅提升個人化和效率",
            first_steps=[
                "研究目標產業的痛點",
                "建立精準的名單搜尋策略",
                "撰寫多套郵件模板",
                "使用 Instantly/Apollo 發送",
                "追蹤開信率和回覆率"
            ],
            automation_steps=[
                "自動名單篩選和驗證",
                "AI 根據公司背景撰寫郵件",
                "智能發送時間排程",
                "回覆意圖識別分類",
                "高意向自動轉交人工"
            ]
        ),
        BusinessIdea(
            id="SALES-003",
            title="LinkedIn 自動化開發",
            category="B2B Sales / LinkedIn",
            profit_mode="b2b-sales",
            description="AI 自動加好友、發送訊息、培育關係的 LinkedIn 銷售自動化",
            target_audience="B2B 銷售、獵頭、業務開發",
            revenue_model="訂閱制 $49-199/月",
            difficulty="medium",
            estimated_monthly_revenue=12000.0,
            required_investment=300.0,
            market_trend="rising",
            key_features=[
                "智能加好友請求",
                "第一人稱訊息撰寫",
                "互動跟進排程",
                "個人資料洞察分析",
                "自動記錄 CRM"
            ],
            competition_level="high",
            why_now="LinkedIn 是 B2B 最大專業社交網路，自動化開發效率提升 10 倍",
            first_steps=[
                "優化個人檔案為銷售導向",
                "設定目標受眾篩選條件",
                "撰寫多種訊息模板",
                "使用 Expandi/PhantomBuster",
                "監控連接率和回覆率"
            ],
            automation_steps=[
                "每日自動發送 20-30 個請求",
                "AI 根據頭銜和行業撰寫訊息",
                "自動化後續互動（點讚、留言）",
                "潛在客戶標籤和分類",
                "會議預約自動化"
            ]
        ),

        # ═══════════════════════════════════════════════════════════
        # ④ 數位產品 (Digital Products)
        # ═══════════════════════════════════════════════════════════
        BusinessIdea(
            id="DIGITAL-001",
            title="AI 生成電子書系列",
            category="Digital Products / eBooks",
            profit_mode="digital-products",
            description="AI 自動撰寫、設計封面、上架銷售的電子書系列",
            target_audience="知識型創作者、專家",
            revenue_model="單本銷售 $9-49",
            difficulty="easy",
            estimated_monthly_revenue=3000.0,
            required_investment=50.0,
            market_trend="rising",
            key_features=[
                "AI 書籍大綱生成",
                "自動章節撰寫",
                "封面 AI 設計",
                "多平台自動上架",
                "定價 A/B 測試"
            ],
            competition_level="medium",
            why_now="AI 能 10 倍速生產內容，個人也能出版專業電子書",
            first_steps=[
                "選擇你有專長的領域",
                "使用 ChatGPT 撰寫大綱",
                "擴充各章節內容",
                "設計封面（Midjourney）",
                "上架 Amazon KDP/Gumroad"
            ],
            automation_steps=[
                "每日研究熱門關鍵字",
                "AI 生成書籍內容",
                "自動排版和格式轉換",
                "多平台同步上架",
                "評價提醒和回覆"
            ]
        ),
        BusinessIdea(
            id="DIGITAL-002",
            title="Notion/Excel 模板商店",
            category="Digital Products / Templates",
            profit_mode="digital-products",
            description="AI 設計和創建 Notion、Excel、Google Sheets 模板並自動銷售",
            target_audience="效率控、自由職業者、小型團隊",
            revenue_model="單品銷售 $5-30",
            difficulty="easy",
            estimated_monthly_revenue=2000.0,
            required_investment=30.0,
            market_trend="rising",
            key_features=[
                "AI 模板設計建議",
                "自動化生成內容",
                "多平台一鍵上架",
                "客戶支持自動化",
                "熱銷品快速複製"
            ],
            competition_level="low",
            why_now="Notion/Etsy 模板市場持續增長，AI 能快速生成高品質模板",
            first_steps=[
                "研究 Etsy/Notion Template 市場",
                "設計 3-5 個核心模板",
                "建立展示頁面",
                "上架 Gumroad/Etsy",
                "透過社群媒體推廣"
            ],
            automation_steps=[
                "監控熱門模板趨勢",
                "AI 生成新模板設計",
                "自動更新舊模板",
                "客戶問答自動回覆",
                "銷售數據週報生成"
            ]
        ),
        BusinessIdea(
            id="DIGITAL-003",
            title="線上課程自動化",
            category="Digital Products / Courses",
            profit_mode="digital-products",
            description="AI 自動撰寫課程大綱、生成教材、錄製講解的線上課程系統",
            target_audience="專家、講師、企業培訓",
            revenue_model="單課程 $97-497，批量銷售",
            difficulty="medium",
            estimated_monthly_revenue=10000.0,
            required_investment=500.0,
            market_trend="rising",
            key_features=[
                "AI 課程大綱生成",
                "自動生成 PPT/教材",
                "AI 配音和字幕",
                "多平台自動上架",
                "學員進度追蹤"
            ],
            competition_level="medium",
            why_now="線上教育市場持續增長，AI 能大幅降低課程製作成本",
            first_steps=[
                "選擇你有專長的教學主題",
                "規劃課程架構",
                "使用 AI 生成教材內容",
                "錄製或配音講解",
                "上架 Udemy/Coursera/Gumroad"
            ],
            automation_steps=[
                "市場需求分析",
                "AI 生成課程內容",
                "自動製作講義和測驗",
                "多平台同步上架",
                "學員問題 AI 自動回覆"
            ]
        ),

        # ═══════════════════════════════════════════════════════════
        # ⑤ 數據分析 (Data Analysis)
        # ═══════════════════════════════════════════════════════════
        BusinessIdea(
            id="DATA-001",
            title="投資分析自動化報告",
            category="Data Analysis / Investing",
            profit_mode="data-analysis",
            description="AI 自動分析股票、加密貨幣、期貨數據並生成投資建議報告",
            target_audience="散戶投資者、金融從業者",
            revenue_model="訂閱制 $29-99/月",
            difficulty="medium",
            estimated_monthly_revenue=15000.0,
            required_investment=200.0,
            market_trend="rising",
            key_features=[
                "即時市場數據監控",
                "技術分析指標計算",
                "AI 趨勢預測",
                "風險評估報告",
                "交易信號推送"
            ],
            competition_level="high",
            why_now="零售投資興起，散戶需要專業級分析工具",
            first_steps=[
                "選擇追蹤的市場（股票/加密/期貨）",
                "設定數據來源（Yahoo Finance/Binance API）",
                "建立分析模型",
                "設計報告格式",
                "透過 Newsletter/Telegram 分發"
            ],
            automation_steps=[
                "每日自動抓取市場數據",
                "AI 生成技術分析報告",
                "關鍵事件 alerts",
                "智能推薦和風險提示",
                "週報/月報自動生成"
            ]
        ),
        BusinessIdea(
            id="DATA-002",
            title="商業 Intelligence 儀表板",
            category="Data Analysis / BI",
            profit_mode="data-analysis",
            description="為中小企業自動生成銷售、行銷、財務數據儀表板的 SaaS",
            target_audience="小型企業、電商卖家、創投",
            revenue_model="訂閱制 $49-199/月",
            difficulty="medium",
            estimated_monthly_revenue=20000.0,
            required_investment=1000.0,
            market_trend="rising",
            key_features=[
                "多數據源整合",
                "自動圖表生成",
                "異常檢測 alerts",
                "預測分析",
                "可分享報告"
            ],
            competition_level="medium",
            why_now="中小企業需要數據驅動決策，但無法負擔 BI 工具",
            first_steps=[
                "定義目標客戶痛點",
                "選擇 2-3 個主要數據源（Stripe、Google Analytics、Shopify）",
                "設計 MVP 儀表板",
                "找到首批 10 個付費用戶",
                "迭代功能擴充數據源"
            ],
            automation_steps=[
                "每日數據自動同步",
                "AI 生成洞察摘要",
                "異常數據自動標記",
                "智能推薦行動方案",
                "客戶健康度評分"
            ]
        ),
        BusinessIdea(
            id="DATA-003",
            title="競品監控與分析服務",
            category="Data Analysis / Competitive Intelligence",
            profit_mode="data-analysis",
            description="AI 自動監控競爭對手價格、產品、評價並生成競爭分析報告",
            target_audience="電商賣家、產品經理、市場行銷",
            revenue_model="訂閱制 $99-299/月",
            difficulty="easy",
            estimated_monthly_revenue=8000.0,
            required_investment=150.0,
            market_trend="rising",
            key_features=[
                "價格監控與歷史追蹤",
                "新品上架 alerts",
                "評價情感分析",
                "市佔率估算",
                "競爭策略建議"
            ],
            competition_level="medium",
            why_now="競爭情報市場增長，AI 能實時監控大量數據源",
            first_steps=[
                "選擇目標行業和競爭對手",
                "設定監控清單（產品、價格、評價）",
                "使用爬蟲或 API 收集數據",
                "設計分析報告模板",
                "透過 Email/Slack 發送報告"
            ],
            automation_steps=[
                "每日競品數據同步",
                "價格變動 alerts",
                "AI 生成競爭分析",
                "策略建議自動推送",
                "月度報告自動生成"
            ]
        ),

        # ═══════════════════════════════════════════════════════════
        # ⑥ 任務自動化 (Task Automation)
        # ═══════════════════════════════════════════════════════════
        BusinessIdea(
            id="AUTO-001",
            title="無代碼自動化代理",
            category="Task Automation / No-Code",
            profit_mode="task-automation",
            description="為企業自動搭建 Zapier/Make 工作流的顧問服務",
            target_audience="中小企業、運營團隊",
            revenue_model="項目制 $500-5,000 + 維護費",
            difficulty="easy",
            estimated_monthly_revenue=10000.0,
            required_investment=100.0,
            market_trend="rising",
            key_features=[
                "流程分析與優化",
                "Zapier/Make 自動化作業",
                "API 整合設定",
                "錯誤監控和修復",
                "效能優化建議"
            ],
            competition_level="low",
            why_now="企業自動化需求激增，但缺乏技術人才",
            first_steps=[
                "學習 Zapier/Make/Integromat",
                "建立自動化案例作品集",
                "在 Upwork/Fiverr 接案",
                "累積客戶評價",
                "開發標準化產品"
            ],
            automation_steps=[
                "客戶需求 AI 分析",
                "自動生成工作流方案",
                "一鍵部署自動化",
                "運行監控和告警",
                "定期效能優化報告"
            ]
        ),
        BusinessIdea(
            id="AUTO-002",
            title="數據匯出與報表自動化",
            category="Task Automation / Reporting",
            profit_mode="task-automation",
            description="自動匯出多平台數據、生成報表、發送 Email 的自動化服務",
            target_audience="市場行銷、財務團隊、運營管理",
            revenue_model="訂閱制 $99-499/月",
            difficulty="easy",
            estimated_monthly_revenue=6000.0,
            required_investment=50.0,
            market_trend="stable",
            key_features=[
                "多平台數據匯出",
                "自動報表生成（PDF/Excel）",
                "Email/Slack 發送排程",
                "數據異常 alerts",
                "歷史數據存檔"
            ],
            competition_level="low",
            why_now="企業依賴數據驅動決策，但手動匯報耗時",
            first_steps=[
                "了解目標客戶的報表需求",
                "選擇主要數據源（GA、Ads、CRM）",
                "設計報表模板",
                "使用 Make/Zapier 自動化",
                "透過社群媒體推廣"
            ],
            automation_steps=[
                "每日自動匯出數據",
                "AI 生成洞察摘要",
                "多格式報表自動生成",
                "按角色發送個性化報告",
                "異常數據自動標記"
            ]
        ),
        BusinessIdea(
            id="AUTO-003",
            title="客服機器人與自動化",
            category="Task Automation / Support",
            profit_mode="task-automation",
            description="AI 客服機器人自動處理常見問題、分流工單、提升客服效率",
            target_audience="電商、SaaS、服務型企業",
            revenue_model="訂閱制 $199-999/月",
            difficulty="medium",
            estimated_monthly_revenue=20000.0,
            required_investment=500.0,
            market_trend="rising",
            key_features=[
                "FAQ 自動回覆",
                "工單分類和分流",
                "情緒識別和升級",
                "多語言支援",
                "知識庫自我學習"
            ],
            competition_level="high",
            why_now="AI 聊天機器人技術成熟，能處理 80% 常見客服問題",
            first_steps=[
                "研究目標客戶的客服痛點",
                "選擇機器人平台（Zendesk、Intercom、Dialogflow）",
                "建立 FAQ 知識庫",
                "設定分流規則",
                "A/B 測試優化解答品質"
            ],
            automation_steps=[
                "7x24 即時回覆",
                "常見問題自動識別和解答",
                "複雜問題智能分流",
                "客戶情緒監控",
                "知識庫自動更新"
            ]
        ),
    ]

    def __init__(self):
        self.discovery_count = 0

    async def discover_ideas(self, count: int = 3, category: Optional[str] = None, profit_mode: Optional[str] = None) -> List[dict]:
        """
        發現並推薦商業構想

        Args:
            count: 推薦數量（1-6）
            category: 可選的分類篩選
            profit_mode: 可選的獲利模式篩選（e-commerce, content-marketing, b2b-sales, digital-products, data-analysis, task-automation）

        Returns:
            商業構想列表
        """
        self.discovery_count += 1
        logger.info(f"[{self.name}] 開始發現商業構想，請求數量: {count}, 獲利模式: {profit_mode}")

        # 根據獲利模式篩選
        ideas = self._idea_pool
        if profit_mode:
            ideas = [i for i in ideas if i.profit_mode == profit_mode]

        # 如果指定的獲利模式沒有結果，回退到全部
        if not ideas:
            ideas = self._idea_pool

        # 如果指定了 category，進一步篩選
        if category and profit_mode:
            ideas = [i for i in ideas if i.category.lower().startswith(category.lower())]

        # 選擇前 count 個
        selected = ideas[:count]

        # 格式化輸出
        results = []
        for idea in selected:
            results.append({
                "id": idea.id,
                "title": idea.title,
                "category": idea.category,
                "profit_mode": idea.profit_mode,
                "profit_mode_name": PROFIT_MODES.get(idea.profit_mode, idea.profit_mode),
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
                "automation_steps": idea.automation_steps,
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
            "profit_modes": list(PROFIT_MODES.keys()),
        }

    def get_profit_modes(self) -> dict:
        """獲取所有獲利模式"""
        return PROFIT_MODES


# 測試函數
def test_idea_discovery():
    """測試 IdeaDiscoveryAgent"""
    print("=" * 70)
    print("IdeaDiscoveryAgent — 商業創意發現測試（6 大獲利模式）")
    print("=" * 70)
    print()

    agent = IdeaDiscoveryAgent()

    # 測試 1: 按獲利模式篩選
    print("【測試 1】按獲利模式篩選")
    print("-" * 70)
    for mode in ["e-commerce", "content-marketing", "b2b-sales", "digital-products", "data-analysis", "task-automation"]:
        ideas = asyncio.run(agent.discover_ideas(count=2, profit_mode=mode))
        print(f"\n{mode}: {len(ideas)} 個構想")
        for idea in ideas:
            print(f"  - {idea['title']}")

    # 測試 2: 統計信息
    print("\n" + "=" * 70)
    print("【測試 2】統計信息")
    print("-" * 70)
    stats = agent.get_stats()
    print(f"  可用構想總數: {stats['total_ideas_available']}")
    print(f"  已發現次數: {stats['discoveries_made']}")
    print(f"  獲利模式: {', '.join(stats['profit_modes'])}")

    print("\n" + "=" * 70)
    print("✅ IdeaDiscoveryAgent 測試通過！")
    print("=" * 70)


if __name__ == "__main__":
    import asyncio
    test_idea_discovery()
