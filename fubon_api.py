import os
from fubon_neo.sdk import FubonSDK
from fubon_neo.constant import BSAction, MarketType, PriceType, TimeInForce, OrderType


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
    return sdk

def get_account(sdk):
    try:
        account_list = sdk.stock.get_account_list()
        if not account_list:
            raise Exception("❌ 無法取得交易帳號，請確認憑證與登入資訊")
        return account_list[0]
    except Exception as e:
        raise Exception(f"❌ 帳號取得失敗：{e}")

def get_real_price(stock_id, sdk):
    quote = sdk.stock.get_quote(stock_id)
    return float(quote["RealTimeQuote"]["CurrentPrice"])

def get_odd_lot_price(stock_id, sdk):
    quote = sdk.stock.get_quote(stock_id)
    return float(quote["OddLotQuote"]["CurrentPrice"])

def get_tradable_balance(sdk, account):
    result = sdk.accounting.bank_remain(account)
    if not result.is_success:
        raise Exception(f"❌ 餘額查詢失敗：{result.message}")
    return float(result.data["available_balance"])

def build_odd_lot_order(stock_id, price, quantity, sdk):
    return sdk.stock.build_order_object(
        buy_sell=BSAction.Buy,
        symbol=stock_id,
        price=str(price),
        quantity=quantity,
        market_type=MarketType.IntradayOdd,
        price_type=PriceType.Limit,
        time_in_force=TimeInForce.ROD,
        order_type=OrderType.Stock,
        user_def="📥 存股儀式"
    )

def execute_order(sdk, account, order):
    result = sdk.stock.execute_order(account, order)
    if not result.is_success:
        raise Exception(f"❌ 下單失敗：{result.message}")
    return result

__all__ = [
    "get_sdk",
    "get_account",
    "get_real_price",
    "get_odd_lot_price",
    "get_tradable_balance",
    "build_odd_lot_order",
    "execute_order"
]
