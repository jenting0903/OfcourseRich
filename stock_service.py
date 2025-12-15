import time
from fubon_api import get_sdk, get_account

def prepare_stock_info(stock_no):
    sdk = get_sdk()
    account = get_account(sdk)

    quote = sdk.stock.get_quote(stock_no)
    stock_name = quote["stock_name"]
    price = quote["sell_price"][0]  # 五檔賣出價第一檔

    balance = sdk.accounting.bank_remain(account)
    usable_cash = balance * 0.8
    est_qty = int(usable_cash // price)

    return {
        "stock_no": stock_no,
        "stock_name": stock_name,
        "price": price,
        "usable_cash": usable_cash,
        "est_qty": est_qty
    }

def monitor_and_trade(stock_no):
    sdk = get_sdk()
    account = get_account(sdk)

    start_time = time.time()
    while True:
        quote = sdk.stock.get_quote(stock_no)
        price = quote["sell_price"][0]

        # TODO: 判斷 1分K黃金交叉 (需自行補上技術指標判斷)
        golden_cross = True  # 假設達成

        if golden_cross:
            order = sdk.stock.place_order(
                account=account,
                symbol=stock_no,
                price=price,
                quantity=1,
                buy_sell="B"
            )
            return {
                "status": "success",
                "stock_no": stock_no,
                "stock_name": quote["stock_name"],
                "price": price,
                "qty": 1,
                "time": time.strftime("%H:%M:%S")
            }

        # 超過 13:00 停止
        if time.localtime().tm_hour >= 13:
            return {
                "status": "timeout",
                "usable_cash": sdk.accounting.bank_remain(account) * 0.8
            }

        time.sleep(2.5)
