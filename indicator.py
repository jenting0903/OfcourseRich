# indicator.py

def get_kline(sdk, stock_id, interval="1m"):
    result = sdk.chart.kline(stock_id, interval=interval)
    if not result.is_success:
        print("❌ K 線查詢失敗：", result.message)
        return []
    return result.data  # 假設格式為 [{"close": 542.0, "time": "13:01"}, ...]

def check_golden_cross(kline_data):
    closes = [k["close"] for k in kline_data if "close" in k]
    if len(closes) < 20:
        return False
    ma5 = sum(closes[-5:]) / 5
    ma20 = sum(closes[-20:]) / 20
    return ma5 > ma20
