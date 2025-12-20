import time
from datetime import datetime
from fubon_api import get_sdk, get_account, get_quote_sell1, get_usable_cash
from indicators import golden_cross_1m
from fubon_neo.enums import BSAction, MarketType, PriceType, TimeInForce, OrderType


class MinuteBarBuilder:
    """用零股五檔賣出價第一檔生成 1 分 K（只用 close）"""
    def __init__(self):
        self.current_minute = None
        self.last_price = None
        self.closes = []

    def feed(self, price, ts):
        minute_key = ts.replace(second=0, microsecond=0)
        self.last_price = price

        if self.current_minute is None:
            self.current_minute = minute_key
            return False

        if minute_key == self.current_minute:
            return False

        # 分鐘切換 → 推入 close
        self.closes.append(self.last_price)
        self.current_minute = minute_key
        return True


def prepare_stock_info(stock_no):
    sdk = get_sdk()
    account = get_account(sdk)

    stock_name, sell1, ts = get_quote_sell1(sdk, stock_no)
    usable_cash = get_usable_cash(sdk, account, ratio=0.8)
    est_qty = max(1, int(usable_cash // sell1))

    return {
        "stock_no": stock_no,
        "stock_name": stock_name,
        "price": sell1,
        "usable_cash": usable_cash,
        "est_qty": est_qty,
        "time": ts.strftime("%H:%M:%S")
    }


def monitor_and_trade(stock_no, fast_period=5, slow_period=20, sample_interval=2.5):
    sdk = get_sdk()
    account = get_account(sdk)
    builder = MinuteBarBuilder()

    usable_cash = get_usable_cash(sdk, account, ratio=0.8)

    stock_name, sell1, ts = get_quote_sell1(sdk, stock_no)
    est_qty = max(1, int(usable_cash // sell1))

    builder.feed(sell1, ts)

    while True:
        now = datetime.now()

        # 超過 13:00 → 停止交易
        if now.hour >= 13:
            return {
                "status": "timeout",
                "usable_cash": usable_cash
            }

        stock_name, sell1, ts = get_quote_sell1(sdk, stock_no)

        minute_done = builder.feed(sell1, ts)

        if minute_done and len(builder.closes) >= slow_period:
            crossed, ma_fast, ma_slow = golden_cross_1m(builder.closes, fast_period, slow_period)

            if crossed:
                # ✅ 黃金交叉成立 → 盤中零股市價下單
                order = sdk.stock.place_order(
                    account=account,
                    buy_sell=BSAction.Buy,
                    symbol=stock_no,
                    price=None,                         # 市價
                    quantity=est_qty,
                    market_type=MarketType.IntradayOdd, # 盤中零股
                    price_type=PriceType.Market,        # 市價
                    time_in_force=TimeInForce.ROD,
                    order_type=OrderType.Stock,
                    user_def="autosave"
                )

                return {
                    "status": "success",
                    "stock_no": stock_no,
                    "stock_name": stock_name,
                    "price": sell1,
                    "qty": est_qty,
                    "amount": float(sell1) * est_qty,
                    "time": now.strftime("%H:%M:%S")
                }

        time.sleep(sample_interval)
