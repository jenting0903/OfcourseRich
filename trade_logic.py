from fubon_api import (
    get_sdk,
    get_real_price,
    get_odd_lot_price,
    get_tradable_balance,
    build_odd_lot_order,
    execute_order  
)

def estimate_quantity(price, budget):
    if price <= 0:
        return 0
    return int(budget // price)

def prepare_order(stock_id):
    sdk, account = get_sdk()
    if not sdk or not account:
        return None, "❌ 登入失敗"

    price = get_odd_lot_price(stock_id, sdk)
    name = get_real_price(stock_id, sdk)[1]
    tradable = get_tradable_balance(account, sdk)
    quantity = estimate_quantity(price, tradable)

    order = build_odd_lot_order(stock_id, price, quantity)
    preview = format_preview(stock_id, name, price, tradable, quantity)
    return {
        "sdk": sdk,
        "account": account,
        "order": order,
        "preview": preview,
        "stock_id": stock_id,
        "name": name,
        "price": price,
        "quantity": quantity,
        "tradable": tradable
    }

def format_preview(stock_id, name, price, tradable, quantity):
    return (
        f"📜 存股預估卷軸展開：\n"
        f"🔹 股票代號：{stock_id}\n"
        f"🔹 股票名稱：{name}\n"
        f"🔹 零股第一檔賣價：{price:.2f} 元\n"
        f"🔹 可用資源：{tradable:,} 元（80% 計算）\n"
        f"🔹 預估可購買股數：{quantity} 股\n\n"
        f"⚠️ 是否執行存股交易？請回覆「是」或「否」"
    )

def execute_order(sdk, account, order):
    result = execute_order(sdk, account, order)
    if result["success"]:
        return f"✅ 已送出委託，委託書號：{result['order_no']}"
    else:
        return f"❌ 委託失敗：{result['message']}"
