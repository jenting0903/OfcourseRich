import os
from fubon_neo.sdk import FubonSDK, OrderObject
from fubon_neo.sdk import BSAction, MarketType, PriceType, TimeInForce, OrderType

def get_sdk():
    sdk = FubonSDK()
    login_result = sdk.login(
        os.environ["FUBON_USER_ID"],
        os.environ["FUBON_PASSWORD"],
        os.environ["FUBON_CERT_PATH"],
        os.environ["FUBON_CERT_PASSWORD"]
    )
    if not login_result.is_success:
        print("❌ 登入失敗：", login_result.message)
        return None, None
    return sdk, login_result.data[0]

def get_real_price(stock_id, sdk):
    quote_result = sdk.quote(stock_id)
    if not quote_result.is_success:
        print("❌ 查詢股價失敗：", quote_result.message)
        return None, None
    return float(quote_result.data.last_price), quote_result.data.stock_name

def get_odd_lot_price(stock_id, sdk):
    quote_result = sdk.quote(stock_id)
    if not quote_result.is_success:
        print("❌ 查詢零股五檔失敗：", quote_result.message)
        return None
    try:
        return float(quote_result.data.odd_lot_sell_prices[0])
    except:
        return float(quote_result.data.last_price)

def get_tradable_balance(account, sdk):
    balance_result = sdk.accounting.bank_remain(account)
    if not balance_result.is_success:
        print("❌ 查詢餘額失敗：", balance_result.message)
        return 0
    return int(balance_result.data.available_balance * 0.8)

def build_odd_lot_order(stock_id, price, quantity):
    return OrderObject(
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
    if result.is_success:
        return {
            "success": True,
            "order_no": result.data.order_no
        }
    else:
        return {
            "success": False,
            "message": result.message
        }

def cancel_order(sdk, account, order_no):
    result = sdk.stock.cancel_order(account, order_no)
    return result.is_success
