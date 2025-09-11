import time
from datetime import datetime
from fubon_neo.sdk import FubonSDK

# 模組匯入
from db import get_yesterday_balance, record_trade, record_balance_only
from trade_logic import should_trade, calculate_trade_budget, decide_order_type
from market import get_real_price
from indicator import reshape_kbars_to_df, is_golden_cross

def monitor_and_trade(stock_id):
    sdk = FubonSDK()
    login_result = sdk.login("F129680202", "blick1111", r"C:\CAFubon\F129680202\F129680202.pfx", "Qazxsw21")
    if not login_result.is_success:
        return {"status": "error", "message": "❌ 登入失敗"}

    account = login_result.data[0]
    balance_result = sdk.accounting.bank_remain(account)
    if not balance_result.is_success:
        return {"status": "error", "message": f"❌ 查詢餘額失敗：{balance_result.message}"}

    today_balance = int(balance_result.data.available_balance)
    yesterday_balance = get_yesterday_balance()

    if not should_trade(today_balance, yesterday_balance):
        record_balance_only(today_balance)
        return {"status": "skip", "message": "⛔ 餘額未達門檻，今日不執行交易"}

    trade_budget = calculate_trade_budget(today_balance)
    price, name = get_real_price(stock_id, sdk)
    if not price:
        record_balance_only(today_balance)
        return {"status": "error", "message": "❌ 無法取得即時報價"}

    order_type, quantity = decide_order_type(price, trade_budget)
    if quantity == 0:
        record_balance_only(today_balance)
        return {"status": "skip", "message": "⛔ 預算不足，無法執行任何交易"}

    print(f"🧭 開始監控黃金交叉：{stock_id} 每 2.5 秒偵測一次")
    start_time = time.time()
    max_duration = 1800  # 最長監控 30 分鐘

    while True:
        if time.time() - start_time > max_duration:
            record_balance_only(today_balance)
            return {"status": "timeout", "message": "⏳ 超過監控時間，今日未達成黃金交叉，程式已關閉"}

        kbars_result = sdk.market.intraday_candles(
            stock_id=stock_id,
            interval="1m",
            date=datetime.now().date()
        )
        if not kbars_result.is_success:
            print("⚠️ 無法取得 K 線資料，重試中...")
            time.sleep(2.5)
            continue

        df = reshape_kbars_to_df(kbars_result.data)
        if is_golden_cross(df):
            print("✅ 偵測到黃金交叉，開始執行交易")
            break

        time.sleep(2.5)

    # 執行零股下單（已強制只執行 odd lot）
    order_result = sdk.order.place_odd_lot_order(account, stock_id, "Buy", price, quantity)

    if not order_result.is_success:
        record_balance_only(today_balance)
        return {"status": "error", "message": f"❌ 下單失敗：{order_result.message}"}

    total_amount = int(price * quantity)
    remaining_balance = today_balance - total_amount

    record_trade({
        "stock_id": stock_id,
        "stock_name": name,
        "quantity": quantity,
        "total_amount": total_amount,
        "account_balance": remaining_balance,
        "order_type": "odd"
    })

    return {
        "status": "success",
        "message": f"🚀 成功執行零股交易：{stock_id} {quantity} 股 @ {price} 元",
        "stock_id": stock_id,
        "stock_name": name,
        "price": price,
        "quantity": quantity,
        "total_amount": total_amount,
        "account_balance": remaining_balance,
        "order_type": "odd"
    }
