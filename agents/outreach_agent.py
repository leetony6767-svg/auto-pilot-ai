"""
Outreach Agent — 自動撰寫/發送開發郵件

反推自 Polsia 銷售/獲客 Agent 的職責：
- 根據目標客戶信息生成個性化開發郵件
- 追蹤開信率和回覆率
- 所有對外郵件需人工審批後發送
"""
from typing import AsyncIterator
import json
import re
from loguru import logger
from datetime import datetime

from agents.base import BaseAgent, BusinessState, PermissionLevel
from config.cost_control import cost_tracker
from config.settings import settings


class OutreachAgent(BaseAgent):
    """銷售/獲客 Agent：個性化開發郵件自動化"""

    name = "outreach_agent"
    permission_level = PermissionLevel.EXECUTE
    cost_model = "anthropic/claude-haiku-4-20250514"  # 郵件生成用低成本模型

    def __init__(self, state: BusinessState):
        super().__init__(state)
        self.leads = state.get("leads", [])
        self.plan = state.get("business_plan", {})

    async def run(self) -> dict:
        """主入口：生成郵件 → 審批 → 發送"""
        logger.info(f"[{self.name}] 開始為 {len(self.leads)} 個线索生成開發郵件")

        if not self.leads:
            self.log(status="skipped", reason="無可用线索")
            return {"emails_generated": 0, "skipped": True}

        try:
            emails = []
            for lead in self.leads[:10]:  # 每次最多處理 10 個
                email = await self._generate_email(lead)
                emails.append(email)

                # 每封郵件都加入審批隊列
                self.add_approval(
                    item_type="outreach_email",
                    content=email,
                    reason=f"向 {lead.get('name', '未知')} 發送開發郵件"
                )

            self.log(status="emails_generated", count=len(emails))
            return {
                "emails_generated": len(emails),
                "pending_approval": True,
                "emails": emails,
            }

        except Exception as e:
            self.log(status="error", error=str(e))
            logger.error(f"[{self.name}] 執行失敗: {e}")
            return {"error": str(e)}

    async def _generate_email(self, lead: dict) -> dict:
        """生成個性化開發郵件"""
        from langchain_anthropic import ChatAnthropic

        product = self.plan.get("positioning", "我們的產品")
        value_prop = self.plan.get("value_proposition", "幫助創作者自動運營業務")
        target_audience = self.plan.get("target_audience", "")

        prompt = f"""你是一位專業的業務拓展專家。請為以下目標客戶撰寫一封個性化開發郵件。

目標客戶信息：
- 姓名：{lead.get('name', '負責人')}
- 公司：{lead.get('company', '未知公司')}
- 職位：{lead.get('title', '')}
- 行業：{lead.get('industry', '')}
- 聯繫方式：{lead.get('email', '')}
- 獲取自：{lead.get('source', '公開信息')}
- 匹配理由：{lead.get('match_reason', '與我們的目標客戶高度匹配')}

產品信息：
- 產品名稱：{self.plan.get('product_name', 'AgentOS')}
- 產品定位：{product}
- 價值主張：{value_prop}
- 目標受眾：{target_audience}

郵件要求：
1. 開頭個人化（提及對方公司或近期動態）
2. 簡短有力（不超過 150 詞）
3. 突出價值，而非功能
4. 明確的 CTA（建議 15 分鐘通話）
5. 語氣專業但有親和力

返回 JSON：
{{
  "subject": "郵件主題",
  "body": "郵件正文",
  "tone": "professional|friendly|casual",
  "cta": "建議的行動呼籲"
}}"""

        llm = ChatAnthropic(
            model=self.cost_model,
            api_key=settings.anthropic_api_key,
            temperature=0.7,
        )

        response = await llm.ainvoke([
            {"role": "system", "content": "你是頂級 B2B 銷售專家，擅長撰寫高回覆率的開發郵件。"},
            {"role": "user", "content": prompt},
        ])

        tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0
        cost_tracker.record_usage(self.name, self.state["user_id"], tokens)

        # 解析 JSON 響應
        content = response.content
        match = re.search(r'\{[^}]+\}', content)
        if match:
            email_data = json.loads(match.group())
        else:
            email_data = {
                "subject": f"合作機會：{self.plan.get('product_name', 'AgentOS')}",
                "body": content,
                "tone": "professional",
                "cta": "安排 15 分鐘通話",
            }

        email_data.update({
            "to": lead.get("email", ""),
            "lead_id": lead.get("id", ""),
            "generated_at": datetime.now().isoformat(),
        })

        self.log(tokens=tokens, lead=lead.get("name", ""))
        logger.debug(f"[{self.name}] 為 {lead.get('name')} 生成郵件，主題：{email_data['subject'][:30]}...")

        return email_data

    async def send_email(self, email: dict, smtp_config: dict = None) -> dict:
        """發送郵件（審批通過後執行）"""
        import smtplib
        from email.mime.text import MIMEText

        logger.info(f"[{self.name}] 发送邮件至 {email.get('to')}")

        msg = MIMEText(email["body"], "plain", "utf-8")
        msg["Subject"] = email["subject"]
        msg["From"] = smtp_config.get("from_email", "hello@agent-os.app") if smtp_config else "hello@agent-os.app"
        msg["To"] = email["to"]

        # 實際發送（這裡模擬）
        # server = smtplib.SMTP(smtp_config["smtp_server"], 587)
        # server.starttls()
        # server.login(smtp_config["username"], smtp_config["password"])
        # server.send_message(msg)
        # server.quit()

        cost_tracker.record_usage(self.name, self.state["user_id"], 50)
        self.log(status="email_sent", to=email["to"])

        return {
            "status": "sent",
            "to": email["to"],
            "subject": email["subject"],
            "sent_at": datetime.now().isoformat(),
        }

    async def track_opens(self, email_id: str) -> dict:
        """追蹤開信率（輪詢模擬）"""
        import random
        # 模擬開信率 30-60%
        opened = random.random() < 0.45
        return {
            "email_id": email_id,
            "opened": opened,
            "clicked": opened and random.random() < 0.3,
            "tracked_at": datetime.now().isoformat(),
        }
