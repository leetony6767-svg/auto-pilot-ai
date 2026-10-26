"""
StorePilot AI — Configuration

基於 Polsia 逆向分析的最小可行原型配置
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # ── LLM Provider ──────────────────────────────────────────────
    # Agnes AI（OpenAI 相容格式）
    agnes_api_key: str = os.getenv("AGNES_API_KEY", "")
    agnes_base_url: str = os.getenv("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1")
    agnes_model: str = os.getenv("AGNES_MODEL", "agnes-2.5-flash")

    # 模型路由配置（成本控制核心）
    # 簡單任務 → 便宜模型，複雜推理 → 強模型
    model_routing: dict[str, str] = {
        "planning": "agnes-2.5-flash",           # 規劃需要較強推理
        "coding": "agnes-2.5-flash",              # 代碼生成
        "content": "agnes-2.5-flash",             # 創意內容
        "customer_service": "agnes-2.5-flash",    # 高頻簡單任務
        "routing": "agnes-2.5-flash",             # 調度用
    }

    # ── 數據庫 ─────────────────────────────────────────────────────
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/agent_os"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # ── 向量存儲 ───────────────────────────────────────────────────
    chroma_path: str = os.getenv("CHROMA_PATH", "./storage/chroma_db")

    # ── 部署 ───────────────────────────────────────────────────────
    vercel_token: str = os.getenv("VERCEL_TOKEN", "")
    deployment_base_url: str = os.getenv(
        "DEPLOYMENT_BASE_URL", "https://agent-os-demo.vercel.app"
    )

    # ── 審批閾值 ───────────────────────────────────────────────────
    approval_required: list[str] = [
        "send_email",
        "post_to_social",
        "deploy_to_production",
        "process_payment",
    ]

    # ── 平台營收抽成配置（基於 Polsia 商業模式）────────────────────
    # 可透過 PLATFORM_FEE_PERCENT 環境變數覆蓋（預設 8%）
    platform_fee_percent: float = float(os.getenv("PLATFORM_FEE_PERCENT", "8"))
    platform_revenue_share: float = 0.20      # 平台抽成比例 20%
    user_revenue_share: float = 0.80          # 用戶留存比例 80%
    ad_spend_share: float = 0.20              # 廣告支出抽成 20%
    subscription_fee_monthly: float = 49.0    # 月度訂閱費 $49
    currency: str = "TWD"                     # 主要幣別（台灣市場）

    # ── 雙幣別訂閱價格配置 ─────────────────────────────────────────
    # 台灣市場定價
    price_twd_monthly: float = 1568.0        # NT$ 1,568/月
    price_twd_yearly: float = 15680.0        # NT$ 15,680/年（約 9 折）
    # 國際市場定價
    price_usd_monthly: float = 49.0          # $49/月
    price_usd_yearly: float = 490.0          # $490/年（約 9 折）
    # 匯率參考
    exchange_rate_twd_usd: float = 0.031     # 1 TWD ≈ 0.031 USD

    # ── 收款配置（暂未启用）─────────────────────────────────────────
    # 线上支付功能尚未部署，以下字段仅作占位，不暴露真实账户信息
    bank_name: str = ""
    bank_code: str = ""
    account_number: str = ""
    account_name: str = ""
    usdt_supported: bool = False
    usdt_networks: list[str] = []
    usdt_wallet_address: str = ""  # TRC20 地址
    usdt_wallet_polygon: str = ""  # Polygon 地址
    usdt_price_monthly: float = 0.0
    usdt_payment_note: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# 全局配置實例
settings = Settings()
