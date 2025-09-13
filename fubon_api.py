from fubon_neo.sdk import FubonSDK

class FubonAdventure:
    def __init__(self, token):
        self.sdk = FubonSDK()
        self.account = self.sdk.login(
            user_id=token["id"],
            password=token["password"],
            cert_path=token["cert_path"],
            cert_password=token["cert_password"]
        ).data[0]  # 假設你只用第一個帳戶

    def query_account(self):
        summary = self.sdk.account.get_summary(self.account)
        return {
            "balance": summary["available_cash"],
            "portfolio_value": summary["total_value"],
            "unrealized_pl": summary["unrealized_profit_loss"]
        }
