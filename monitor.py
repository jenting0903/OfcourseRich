import time
from datetime import datetime
from indicator import get_kline, check_golden_cross
from trade_logic import execute_order
from fubon_api import get_sdk, get_real_price, get_odd_lot_price, get_tradable_balance, build_odd_lot_order
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, PushMessageRequest, TextMessage

def reply(user_id, text):
    config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
    with ApiClient(config) as api_client:
        messaging_api = MessagingApi(api_client)
        message = TextMessage(text=text)
        push_request = PushMessageRequest(to=user_id, messages=[message])
        messaging_api.push_message(push_request)
monitoring_flags = {}

def start_monitoring(user_id, stock_id, name, sdk, account, tradable):
    monitoring_flags[user_id] = True
    while monitoring_flags.get(user_id):
        now = datetime.now()
        if now.hour == 13 and now.minute >= 29:
            reply(user_id, f"📭 今日未能交易，明日再接再厲\n🔹 股票代號：{stock_id}\n🔹 股票名稱：{name}\n🔹 時間：{now.strftime('%H:%M:%S')}")
            break

        kline_data = get_kline(stock_id, interval="1m")  
        if check_golden_cross(kline_data):
            price = get_odd_lot_price(stock_id, sdk)
            quantity = int(tradable // price)
            order = build_odd_lot_order(stock_id, price, quantity)
            result = execute_order(sdk, account, order)
            reply(user_id, f"✅ 已達成條件並下單\n🔹 股票代號：{stock_id}\n🔹 股票名稱：{name}\n🔹 下單價格：{price}\n🔹 下單股數：{quantity}\n🔹 下單時間：{now.strftime('%H:%M:%S')}")
            break

        time.sleep(2.5)

def stop_monitoring(user_id):
    monitoring_flags[user_id] = False
