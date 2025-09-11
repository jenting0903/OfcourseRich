from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, PushMessageRequest
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import threading
import os

app = Flask(__name__)

# 設定 LINE 憑證（請改成你自己的）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "P24zhpGoQrbPeuAz0InzmLEutrRhd7qPMF1WntXjtxvtWFVV1KR+SPx9KTeqoZ7GW2gI9ztN43WQ5gaFcwSGpJhwRyBuqEuVAYXHU4iVqZ/mCrjJZOAgorsCre5OIvlOTokS5zbnkLD7OtNZ37LZXAdB04t89/1O/w1cDnyilFU=")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "f1155d43889c61b23f706e9ebbb71565")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ✅ LINE webhook 路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# ✅ 訊息處理邏輯（先回覆，再執行）
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()

    # Step 1：先回覆，避免 webhook timeout
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        messaging_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="⏳ 指令已接收，正在處理中...")]
            )
        )

    # Step 2：背景執行交易邏輯
    def background_task():
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)

            if msg.startswith("/交易"):
                stock_id = msg.replace("/交易", "").strip()
                result = monitor_and_trade(stock_id)  # 你自己的交易函式
                reply = f"✅ 交易完成：{result}"
            else:
                reply = f"📩 你說的是：{msg}"

            messaging_api.push_message_with_http_info(
                PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=reply)]
                )
            )

    threading.Thread(target=background_task).start()

# ✅ Render 雲端啟動用
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)