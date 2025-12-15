import os
from fubon_neo import FubonSDK
from fubon_neo.stock import Stock as FubonStock

def get_sdk():
    sdk = FubonSDK()
    login_result = sdk.login(
        os.environ["FUBON_USER_ID"],
        os.environ["FUBON_PASSWORD"],
        os.environ["FUBON_CERT_PATH"],
        os.environ["FUBON_CERT_PASSWORD"]
    )
    if not login_result.is_success:
        raise Exception(f"❌ 登入失敗：{login_result.message}")

    if not isinstance(sdk.stock, FubonStock):
        raise Exception("❌ SDK 初始化錯誤：sdk.stock 類型異常")

    return sdk

def get_account(sdk):
    account_list = sdk.stock.get_account_list()
    if not account_list:
        raise Exception("❌ 無法取得交易帳號")
    return account_list[0]
