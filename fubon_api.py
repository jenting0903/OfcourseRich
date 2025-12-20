import os
from fubon_neo import FubonSDK

def get_sdk():
    """依照 EnumMatrix 規範登入 SDK"""
    sdk = FubonSDK()

    login_result = sdk.login(
        user_id=os.environ["FUBON_USER_ID"],
        password=os.environ["FUBON_PASSWORD"],
        cert_path=os.environ["FUBON_CERT_PATH"],
        cert_pass=os.environ["FUBON_CERT_PASSWORD"]
    )

    if not login_result.is_success:
        raise Exception(f"登入失敗：{login_result.message}")

    return sdk


def get_account(sdk):
    """依照 EnumMatrix 規範取得帳號（Account 結構）"""
    accounts = sdk.stock.get_account_list()

    if not accounts or len(accounts) == 0:
        raise Exception("無法取得交易帳號")

    return accounts[0]


def get_quote_sell1(sdk, stock_no):
    """回傳（股票名稱, 五檔賣出價第一檔, 時間）"""
    q = sdk.stock.get_quote(stock_no)
    stock_name = q.get("stock_name")
    sell1 = float(q["sell_price"][0])
    from datetime import datetime
    return stock_name, sell1, datetime.now()


def get_usable_cash(sdk, account, ratio=0.8):
    """可動用資金 = 帳戶總金額 * 80%"""
    total = sdk.accounting.bank_remain(account)
    return float(total) * ratio
