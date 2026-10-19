"""
多語言支援模組 - StorePilot AI
支援: 繁體中文 (zh-TW), 英文 (en), 印尼文 (id)
"""

class I18n:
    def __init__(self):
        self.current_lang = "zh-TW"
        self.translations = {
            "zh-TW": {
                # 導航列
                "navbar.title": "StorePilot AI",
                "navbar.subtitle": "AI 在你睡覺時替你運營商店",
                "navbar.dashboard": "儀表板",
                "navbar.analyze": "逆向分析",
                "navbar.pricing": "定價方案",
                "navbar.status": "運行狀態",
                "navbar.logs": "執行日誌",
                "navbar.settings": "設定",

                # 標題與說明
                "hero.title": "自動運營你的電子商務商店",
                "hero.subtitle": "AI Agent 在您睡眠時自動執行市場分析、產品定價、行銷推廣和客戶開發",
                "hero.start": "開始自動化",
                "hero.demo": "觀看演示",

                # 功能卡片
                "feature.1.title": "智能市場分析",
                "feature.1.desc": "自動分析目標市場趨勢、競爭對手定價和消費者行為",
                "feature.2.title": "動態定價策略",
                "feature.2.desc": "基於市場數據自動調整價格，最大化利潤率",
                "feature.3.title": "自動行銷推廣",
                "feature.3.desc": "生成並發布社交媒體內容，管理廣告活動",
                "feature.4.title": "客戶開發",
                "feature.4.desc": "自動識別潛在客戶並發起個性化 outreach",

                # 操作按鈕
                "btn.run": "啟動自動化工作流",
                "btn.stop": "停止運行",
                "btn.analyze": "開始逆向分析",
                "btn.submit": "提交目標",
                "btn.reset": "重置",
                "btn.copy": "複製",
                "btn.start": "開始運行",
                "btn.pause": "暫停",
                "btn.resume": "繼續",

                # 狀態訊息
                "status.idle": "待機中",
                "status.running": "運行中",
                "status.paused": "已暫停",
                "status.completed": "已完成",
                "status.error": "發生錯誤",

                # 定價資訊
                "pricing.monthly": "每月方案",
                "pricing.twd": "NT$ 1,568/月",
                "pricing.usd": "$49/月",
                "pricing.annual": "年付方案",
                "pricing.annual_discount": "年付享 8 折優惠",
                "pricing.twd_annual": "NT$ 12,600/年",
                "pricing.usd_annual": "$392/年",

                # 支付資訊
                "payment.usdt": "USDT 加密貨幣支付",
                "payment.wallet": "錢包地址",
                "payment.bank": "銀行轉帳",
                "payment.bank_name": "國泰世華銀行",
                "payment.account": "帳號: 117-50-605328-0",

                # 日誌
                "log.analysis": "分析階段",
                "log.strategy": "策略制定",
                "log.execution": "執行階段",
                "log.complete": "任務完成",
                "log.cost": "Token 成本",

                # 設定了
                "settings.language": "語言設定",
                "settings.api_key": "API Key",
                "settings.theme": "主題",
                "settings.dark": "深色模式",
                "settings.light": "浅色模式",

                # 側邊欄
                "sidebar.title": "StorePilot AI 控制台",
                "sidebar.workspace": "工作區",
                "sidebar.user": "使用者",
                "sidebar.help": "幫助",
                "sidebar.docs": "文件",
                "sidebar.support": "支援",
                "sidebar.logout": "登出",

                # 分析功能
                "analyze.title": "逆向工程分析",
                "analyze.target": "輸入目標 URL",
                "analyze.placeholder": "https://example.com",
                "analyze.result": "分析結果",
                "analyze.tech_stack": "技術棧",
                "analyze.api_endpoints": "API 端點",
                "analyze.features": "功能列表",
                "analyze.suggestions": "改進建議",

                # 系統資訊
                "system.name": "StorePilot AI",
                "system.version": "版本 0.1.0",
                "system.status": "系統狀態",
                "system.health": "健康檢查",
                "system.uptime": "運行時間",
            },
            "en": {
                # Navigation
                "navbar.title": "StorePilot AI",
                "navbar.subtitle": "AI runs your store while you sleep",
                "navbar.dashboard": "Dashboard",
                "navbar.analyze": "Analysis",
                "navbar.pricing": "Pricing",
                "navbar.status": "Status",
                "navbar.logs": "Logs",
                "navbar.settings": "Settings",

                # Hero Section
                "hero.title": "Automate Your E-commerce Store",
                "hero.subtitle": "AI Agents automatically perform market analysis, pricing, marketing, and lead generation while you sleep",
                "hero.start": "Start Automation",
                "hero.demo": "Watch Demo",

                # Feature Cards
                "feature.1.title": "Smart Market Analysis",
                "feature.1.desc": "Automatically analyze market trends, competitor pricing, and consumer behavior",
                "feature.2.title": "Dynamic Pricing Strategy",
                "feature.2.desc": "Automatically adjust prices based on market data to maximize profit margins",
                "feature.3.title": "Automated Marketing",
                "feature.3.desc": "Generate and publish social media content, manage ad campaigns",
                "feature.4.title": "Lead Generation",
                "feature.4.desc": "Automatically identify potential customers and initiate personalized outreach",

                # Buttons
                "btn.run": "Start Workflow",
                "btn.stop": "Stop",
                "btn.analyze": "Start Analysis",
                "btn.submit": "Submit",
                "btn.reset": "Reset",
                "btn.copy": "Copy",
                "btn.start": "Start",
                "btn.pause": "Pause",
                "btn.resume": "Resume",

                # Status
                "status.idle": "Idle",
                "status.running": "Running",
                "status.paused": "Paused",
                "status.completed": "Completed",
                "status.error": "Error",

                # Pricing
                "pricing.monthly": "Monthly Plan",
                "pricing.twd": "NT$ 1,568/month",
                "pricing.usd": "$49/month",
                "pricing.annual": "Annual Plan",
                "pricing.annual_discount": "Get 20% off with annual billing",
                "pricing.twd_annual": "NT$ 12,600/year",
                "pricing.usd_annual": "$392/year",

                # Payment
                "payment.usdt": "USDT Crypto Payment",
                "payment.wallet": "Wallet Address",
                "payment.bank": "Bank Transfer",
                "payment.bank_name": "Cathay United Bank",
                "payment.account": "Account: 117-50-605328-0",

                # Logs
                "log.analysis": "Analysis Phase",
                "log.strategy": "Strategy Phase",
                "log.execution": "Execution Phase",
                "log.complete": "Task Completed",
                "log.cost": "Token Cost",

                # Settings
                "settings.language": "Language",
                "settings.api_key": "API Key",
                "settings.theme": "Theme",
                "settings.dark": "Dark Mode",
                "settings.light": "Light Mode",

                # Sidebar
                "sidebar.title": "StorePilot AI Console",
                "sidebar.workspace": "Workspace",
                "sidebar.user": "User",
                "sidebar.help": "Help",
                "sidebar.docs": "Docs",
                "sidebar.support": "Support",
                "sidebar.logout": "Logout",

                # Analysis
                "analyze.title": "Reverse Engineering Analysis",
                "analyze.target": "Enter Target URL",
                "analyze.placeholder": "https://example.com",
                "analyze.result": "Analysis Result",
                "analyze.tech_stack": "Tech Stack",
                "analyze.api_endpoints": "API Endpoints",
                "analyze.features": "Features",
                "analyze.suggestions": "Suggestions",

                # System
                "system.name": "StorePilot AI",
                "system.version": "Version 0.1.0",
                "system.status": "System Status",
                "system.health": "Health Check",
                "system.uptime": "Uptime",
            },
            "id": {
                # Navigasi
                "navbar.title": "StorePilot AI",
                "navbar.subtitle": "AI mengoperasikan toko Anda saat Anda tidur",
                "navbar.dashboard": "Dasbor",
                "navbar.analyze": "Analisis",
                "navbar.pricing": "Harga",
                "navbar.status": "Status",
                "navbar.logs": "Catatan",
                "navbar.settings": "Pengaturan",

                # Hero Section
                "hero.title": "Otomatisasi Toko E-commerce Anda",
                "hero.subtitle": "AI Agents secara otomatis melakukan analisis pasar, penentuan harga, pemasaran, dan pengadaan pelanggan saat Anda tidur",
                "hero.start": "Mulai Otomasi",
                "hero.demo": "Lihat Demo",

                # Feature Cards
                "feature.1.title": "Analisis Pasar Cerdas",
                "feature.1.desc": "Secara otomatis menganalisis tren pasar, harga pesaing, dan perilaku konsumen",
                "feature.2.title": "Strategi Harga Dinamis",
                "feature.2.desc": "Secara otomatis menyesuaikan harga berdasarkan data pasar untuk memaksimalkan margin keuntungan",
                "feature.3.title": "Pemasaran Otomatis",
                "feature.3.desc": "Menghasilkan dan memposting konten media sosial, mengelola kampanye iklan",
                "feature.4.title": "Pengadaan Calon Pelanggan",
                "feature.4.desc": "Secara otomatis mengidentifikasi calon pelanggan dan memulai outreach yang dipersonalisasi",

                # Buttons
                "btn.run": "Mulai Alur Kerja",
                "btn.stop": "Berhenti",
                "btn.analyze": "Mulai Analisis",
                "btn.submit": "Kirim",
                "btn.reset": "Reset",
                "btn.copy": "Salin",
                "btn.start": "Mulai",
                "btn.pause": "Jeda",
                "btn.resume": "Lanjutkan",

                # Status
                "status.idle": "Siaga",
                "status.running": "Berjalan",
                "status.paused": "Dijeda",
                "status.completed": "Selesai",
                "status.error": "Kesalahan",

                # Pricing
                "pricing.monthly": "Rencana Bulanan",
                "pricing.twd": "NT$ 1,568/bulan",
                "pricing.usd": "$49/bulan",
                "pricing.annual": "Rencana Tahunan",
                "pricing.annual_discount": "Dapatkan diskon 20% dengan tagihan tahunan",
                "pricing.twd_annual": "NT$ 12,600/tahun",
                "pricing.usd_annual": "$392/tahun",

                # Payment
                "payment.usdt": "Pembayaran Kripto USDT",
                "payment.wallet": "Alamat Dompet",
                "payment.bank": "Transfer Bank",
                "payment.bank_name": "Bank Cathay United",
                "payment.account": "Rekening: 117-50-605328-0",

                # Logs
                "log.analysis": "Fase Analisis",
                "log.strategy": "Fase Strategi",
                "log.execution": "Fase Eksekusi",
                "log.complete": "Tugas Selesai",
                "log.cost": "Biaya Token",

                # Settings
                "settings.language": "Bahasa",
                "settings.api_key": "API Key",
                "settings.theme": "Tema",
                "settings.dark": "Mode Gelap",
                "settings.light": "Mode Terang",

                # Sidebar
                "sidebar.title": "Konsol StorePilot AI",
                "sidebar.workspace": "Ruang Kerja",
                "sidebar.user": "Pengguna",
                "sidebar.help": "Bantuan",
                "sidebar.docs": "Dokumentasi",
                "sidebar.support": "Dukungan",
                "sidebar.logout": "Keluar",

                # Analysis
                "analyze.title": "Analisis Rekayasa Balik",
                "analyze.target": "Masukkan URL Target",
                "analyze.placeholder": "https://contoh.com",
                "analyze.result": "Hasil Analisis",
                "analyze.tech_stack": "Tumpukan Teknologi",
                "analyze.api_endpoints": "Endpoint API",
                "analyze.features": "Fitur",
                "analyze.suggestions": "Saran",

                # System
                "system.name": "StorePilot AI",
                "system.version": "Versi 0.1.0",
                "system.status": "Status Sistem",
                "system.health": "Pemeriksaan Kesehatan",
                "system.uptime": "Waktu Aktif",
            }
        }

    def get(self, key: str) -> str:
        """Get translation for key in current language"""
        return self.translations.get(self.current_lang, {}).get(key, key)

    def set_language(self, lang: str):
        """Set current language"""
        if lang in self.translations:
            self.current_lang = lang

    def get_available_languages(self) -> list:
        """Get list of available languages"""
        return [
            {"code": "zh-TW", "name": "繁體中文", "native": "繁體中文"},
            {"code": "en", "name": "English", "native": "English"},
            {"code": "id", "name": "Bahasa Indonesia", "native": "Bahasa Indonesia"},
        ]


# 全局實例
i18n = I18n()


def t(key: str) -> str:
    """快捷函數：獲取翻譯"""
    return i18n.get(key)


def set_lang(lang: str):
    """設定當前語言"""
    i18n.set_language(lang)
