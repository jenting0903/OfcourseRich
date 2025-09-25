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

def get_real_price(stock_id, sdk):
    quote = sdk.stock.get_quote(stock_id)
    return float(quote["RealTimeQuote"]["CurrentPrice"])

def get_odd_lot_price(stock_id, sdk):
    quote = sdk.stock.get_quote(stock_id)
    return float(quote["OddLotQuote"]["CurrentPrice"])

def get_tradable_balance(sdk, account):
    balance = sdk.stock.get_balance(account)
    return float(balance["AvailableBalance"])

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
        user_def="存股零股"
    )

def place_order(sdk, account, order):
    result = sdk.stock.place_order(account, order)
    if not result.is_success:
        raise Exception(f"❌ 下單失敗：{result.message}")
    return result
