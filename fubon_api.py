import os
from fubon_neo.sdk import FubonSDK

class FubonAdventure:
    def __init__(self):
        print("🧙‍♂️ 初始化 FubonAdventure 中...")
        self.sdk = FubonSDK()
        try:
            print("🔐 嘗試登入中...")
            login_result = self.sdk.login(
                os.environ["FUBON_USER_ID"],
                os.environ["FUBON_PASSWORD"],
                os.environ["FUBON_CERT_PATH"],
                os.environ["FUBON_CERT_PASSWORD"]
            )
            print("✅ 登入成功，回傳：", login_result)
            self.account = login_result.data[0]
        except Exception as e:
            print("❌ 登入失敗：", e)
            self.account = None

    def query_account(self):
        if not self.account:
            print("⚠️ 帳戶為空，無法查詢")
            return None
        try:
            print("📦 呼叫 get_summary() 中...")
            summary = self.sdk.get_summary(self.account)
            print("📦 帳務摘要：", summary)
            return {
                "balance": summary["available_cash"],
                "portfolio_value": summary["total_value"],
                "unrealized_pl": summary["unrealized_profit_loss"]
            }
        except Exception as e:
            print("❌ 查詢帳務失敗：", e)
            return None




#git add .
#git commit -m "更新 fubon_api.py，改用環境變數登入"
#git push origin main
