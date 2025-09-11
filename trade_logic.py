def should_trade(today_balance, yesterday_balance, threshold=50):
    """
    判斷是否啟動交易：餘額比昨日高出 threshold 元
    """
    return today_balance > yesterday_balance and (today_balance - yesterday_balance) >= threshold


def calculate_trade_budget(today_balance, ratio=0.8):
    """
    計算本次交易預算（使用今日餘額的 ratio）
    """
    return int(today_balance * ratio)


def decide_order_type(price, budget):
    """
    強制執行零股交易，根據預算計算可買股數
    """
    quantity = int(budget // price)
    return "odd", quantity
