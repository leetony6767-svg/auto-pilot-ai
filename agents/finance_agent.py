"""
Finance Agent — 營收分潤計算器

基於 Polsia 商業模式：
- 平台訂閱費: $49/月
- 平台收入抽成: 20%
- 平台廣告支出抽成: 20%
- 用戶留存: 80%
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from loguru import logger

from config.settings import settings


@dataclass
class RevenueSplit:
    """營收分潤結果"""
    gross_revenue: float           # 總營收
    platform_cut: float            # 平台抽成 (20%)
    user_retention: float          # 用戶留存 (80%)
    ad_spend: float                # 廣告支出
    ad_platform_cut: float         # 廣告抽成 (20%)
    ad_user_bear: float            # 用戶承擔廣告費 (80%)
    net_platform_revenue: float    # 平台淨收入
    net_user_revenue: float        # 用戶淨收入
    calculated_at: str             # 計算時間


class FinanceAgent:
    """財務 Agent：計算營收分潤"""

    name = "finance_agent"

    def __init__(self, monthly_revenue: float = 0.0, ad_spend: float = 0.0):
        self.monthly_revenue = monthly_revenue
        self.ad_spend = ad_spend
        self.platform_rate = settings.platform_revenue_share
        self.user_rate = settings.user_revenue_share
        self.ad_rate = settings.ad_spend_share

    def calculate_split(self) -> RevenueSplit:
        """計算營收分潤"""
        # 收入分潤
        platform_cut = self.monthly_revenue * self.platform_rate
        user_retention = self.monthly_revenue * self.user_rate

        # 廣告支出分潤
        ad_platform_cut = self.ad_spend * self.ad_rate
        ad_user_bear = self.ad_spend * (1 - self.ad_rate)

        # 淨收入
        net_platform_revenue = platform_cut + ad_platform_cut
        net_user_revenue = user_retention - ad_user_bear

        return RevenueSplit(
            gross_revenue=self.monthly_revenue,
            platform_cut=platform_cut,
            user_retention=user_retention,
            ad_spend=self.ad_spend,
            ad_platform_cut=ad_platform_cut,
            ad_user_bear=ad_user_bear,
            net_platform_revenue=net_platform_revenue,
            net_user_revenue=net_user_revenue,
            calculated_at=datetime.now().isoformat(),
        )

    def generate_report(self, revenue: float = 0.0, ad_spend: float = 0.0) -> dict:
        """生成營收報告"""
        split = RevenueSplit(
            gross_revenue=revenue,
            platform_cut=revenue * self.platform_rate,
            user_retention=revenue * self.user_rate,
            ad_spend=ad_spend,
            ad_platform_cut=ad_spend * self.ad_rate,
            ad_user_bear=ad_spend * (1 - self.ad_rate),
            net_platform_revenue=(revenue * self.platform_rate) + (ad_spend * self.ad_rate),
            net_user_revenue=(revenue * self.user_rate) - (ad_spend * (1 - self.ad_rate)),
            calculated_at=datetime.now().isoformat(),
        )

        report = {
            "status": "success",
            "currency": settings.currency,
            "platform_rate": f"{self.platform_rate * 100:.0f}%",
            "user_rate": f"{self.user_rate * 100:.0f}%",
            "ad_rate": f"{self.ad_rate * 100:.0f}%",
            "gross_revenue": split.gross_revenue,
            "ad_spend": split.ad_spend,
            "platform_revenue": {
                "subscription_fee": settings.subscription_fee_monthly,
                "revenue_share": split.platform_cut,
                "ad_share": split.ad_platform_cut,
                "total": split.net_platform_revenue,
            },
            "user_revenue": {
                "revenue_after_share": split.user_retention,
                "ad_cost_borne": split.ad_user_bear,
                "net_income": split.net_user_revenue,
            },
            "calculated_at": split.calculated_at,
        }

        logger.info(f"[{self.name}] 營收分潤計算完成: 總營收 ${split.gross_revenue:.2f}")
        logger.info(f"  平台抽成: ${split.platform_cut:.2f} ({self.platform_rate*100:.0f}%)")
        logger.info(f"  用戶留存: ${split.user_retention:.2f} ({self.user_rate*100:.0f}%)")

        return report


# 測試函數
def test_revenue_split():
    """測試營收分潤計算"""
    print("=" * 60)
    print("MVP Agent OS — 營收分潤測試")
    print("=" * 60)
    print()

    finance = FinanceAgent()

    # 測試場景 1: 月營收 $2,000，廣告支出 $500
    print("【測試場景 1】月營收 $2,000，廣告支出 $500")
    report = finance.generate_report(revenue=2000.0, ad_spend=500.0)

    print(f"  總營收: ${report['gross_revenue']:.2f}")
    print(f"  廣告支出: ${report['ad_spend']:.2f}")
    print()
    print(f"  ┌─ 平台收入 (${report['platform_rate']}) ─┐")
    print(f"  │ 訂閱費: ${settings.subscription_fee_monthly:.2f}/月")
    print(f"  │ 營收抽成: ${report['platform_revenue']['revenue_share']:.2f}")
    print(f"  │ 廣告抽成: ${report['platform_revenue']['ad_share']:.2f}")
    print(f"  │ 平台總收入: ${report['platform_revenue']['total']:.2f}")
    print(f"  └────────────────────────────────┘")
    print()
    print(f"  ┌─ 用戶收入 (80%) ─┐")
    print(f"  │ 營收留存: ${report['user_revenue']['revenue_after_share']:.2f}")
    print(f"  │ 承擔廣告費: ${report['user_revenue']['ad_cost_borne']:.2f}")
    print(f"  │ 淨收入: ${report['user_revenue']['net_income']:.2f}")
    print(f"  └────────────────────┘")
    print()

    # 測試場景 2: 模擬 Polsia 典型用戶
    print("【測試場景 2】Polsia 典型用戶 — 月營收 $3,000，廣告支出 $800")
    report2 = finance.generate_report(revenue=3000.0, ad_spend=800.0)

    print(f"  總營收: ${report2['gross_revenue']:.2f}")
    print(f"  廣告支出: ${report2['ad_spend']:.2f}")
    print()
    print(f"  平台收入: ${report2['platform_revenue']['total']:.2f}")
    print(f"    - 訂閱費: ${settings.subscription_fee_monthly:.2f}")
    print(f"    - 營收抽成 (20%): ${report2['platform_revenue']['revenue_share']:.2f}")
    print(f"    - 廣告抽成 (20%): ${report2['platform_revenue']['ad_share']:.2f}")
    print()
    print(f"  用戶淨收入: ${report2['user_revenue']['net_income']:.2f}")
    print(f"    - 營收留存 (80%): ${report2['user_revenue']['revenue_after_share']:.2f}")
    print(f"    - 承擔廣告費 (80%): ${report2['user_revenue']['ad_cost_borne']:.2f}")
    print()

    # 驗證計算正確性
    print("【驗證計算邏輯】")
    expected_platform = 3000.0 * 0.20 + 800.0 * 0.20
    expected_user = 3000.0 * 0.80 - 800.0 * 0.80
    assert abs(report2['platform_revenue']['total'] - expected_platform) < 0.01, \
        f"平台收入計算錯誤: {report2['platform_revenue']['total']} != {expected_platform}"
    assert abs(report2['user_revenue']['net_income'] - expected_user) < 0.01, \
        f"用戶收入計算錯誤: {report2['user_revenue']['net_income']} != {expected_user}"
    print(f"  ✅ 平台收入驗證通過: ${expected_platform:.2f}")
    print(f"  ✅ 用戶淨收入驗證通過: ${expected_user:.2f}")
    print()
    print("=" * 60)
    print("✅ 營收分潤測試全部通過！")
    print("=" * 60)


if __name__ == "__main__":
    test_revenue_split()
