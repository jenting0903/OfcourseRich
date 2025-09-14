import os
from fubon_neo.sdk import FubonSDK

class FubonAdventure:
    def __init__(self):
        self.sdk = FubonSDK()
        login_result = self.sdk.login(
            user_id=os.environ["FUBON_USER_ID"],
            password=os.environ["FUBON_PASSWORD"],
            cert_path=os.environ["FUBON_CERT_PATH"],
            cert_password=os.environ["FUBON_CERT_PASSWORD"]
        )
        self.account = login_result.data[0]

    def query_account(self):
        summary = self.sdk.account.get_summary(self.account)
        return {
            "balance": summary["available_cash"],
            "portfolio_value": summary["total_value"],
            "unrealized_pl": summary["unrealized_profit_loss"]
        }
