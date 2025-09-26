from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, PushMessageRequest
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from fubon_api import get_sdk, get_account, get_real_price, get_odd_lot_price, get_tradable_balance, build_odd_lot_order, execute_order


from trade_logic import format_preview
from indicator import get_kline, check_golden_cross
import threading
import time
import os
from datetime import datetime

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

user_state = {}
monitoring_flags = {}

def send_line_message(user_id, text):
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        message = TextMessage(text=text)
        request = PushMessageRequest(to=user_id, messages=[message])
        messaging_api.push_message_with_http_info(request)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()

    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        messaging_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="⏳ 指令已接收，正在處理中...")]
            )
        )

    def background_task():
        if msg == "/開始存股":
            user_state[user_id] = {"step": "await_stock_id"}
            send_line_message(user_id, "📥 請輸入股票代號：")

        elif user_state.get(user_id, {}).get("step") == "await_stock_id":
            stock_id = msg
            sdk = get_sdk()
            account = get_account(sdk)
            price = get_odd_lot_price(stock_id, sdk)
            name = get_real_price(stock_id, sdk)[1]
            tradable = get_tradable_balance(account, sdk)
            quantity = int(tradable // price)
            preview = format_preview(stock_id, name, price, tradable, quantity)
            user_state[user_id] = {
                "step": "confirm_order",
                "stock_id": stock_id,
                "name": name,
                "sdk": sdk,
                "account": account,
                "price": price,
                "quantity": quantity,
                "tradable": tradable
            }
            send_line_message(user_id, preview)

        elif user_state.get(user_id, {}).get("step") == "confirm_order":
            if msg == "是":
                send_line_message(user_id, "🧙‍♂️ 儀式啟動：開始偵測……")
                data = user_state[user_id]
                threading.Thread(target=start_monitoring, args=(
                    user_id, data["stock_id"], data["name"], data["sdk"], data["account"], data["tradable"]
                )).start()
            else:
                user_state[user_id] = {"step": "await_stock_id"}
                send_line_message(user_id, "📥 請重新輸入股票代號：")

        elif msg == "/停止存股":
            monitoring_flags[user_id] = False
            send_line_message(user_id, "🛑 今日未能交易，明日再接再厲")

    threading.Thread(target=background_task).start()

def start_monitoring(user_id, stock_id, name, sdk, account, tradable):
    monitoring_flags[user_id] = True
    while monitoring_flags.get(user_id):
        now = datetime.now()
        if now.hour == 13 and now.minute >= 29:
            send_line_message(user_id, f"📭 今日未能交易，明日再接再厲\n🔹 股票代號：{stock_id}\n🔹 股票名稱：{name}\n🔹 時間：{now.strftime('%H:%M:%S')}")
            break

        kline_data = get_kline(sdk, stock_id)
        if check_golden_cross(kline_data):
            price = get_odd_lot_price(stock_id, sdk)
            quantity = int(tradable // price)
            order = build_odd_lot_order(stock_id, price, quantity)
            result = execute_order(sdk, account, order)
            if result["success"]:
                send_line_message(user_id, f"✅ 已達成條件並下單\n🔹 股票代號：{stock_id}\n🔹 股票名稱：{name}\n🔹 下單價格：{price}\n🔹 下單股數：{quantity}\n🔹 下單時間：{now.strftime('%H:%M:%S')}")
            else:
                send_line_message(user_id, f"❌ 下單失敗：{result['message']}")
            break

        time.sleep(2.5)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
