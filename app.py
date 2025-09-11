from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

# 建立 Flask 應用
app = Flask(__name__)

# 設定 LINE 憑證（請改成你自己的）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "P24zhpGoQrbPeuAz0InzmLEutrRhd7qPMF1WntXjtxvtWFVV1KR+SPx9KTeqoZ7GW2gI9ztN43WQ5gaFcwSGpJhwRyBuqEuVAYXHU4iVqZ/mCrjJZOAgorsCre5OIvlOTokS5zbnkLD7OtNZ37LZXAdB04t89/1O/w1cDnyilFU=")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "f1155d43889c61b23f706e9ebbb71565")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ✅ webhook 路由：LINE 平台會呼叫這裡
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ✅ 訊息處理邏輯：放這裡！
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.strip()

    # Step 1：先回覆使用者，避免 webhook timeout
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="⏳ 指令已接收，正在處理中...")
    )

    # Step 2：在背景執行交易邏輯
    def background_task():
        if msg.startswith("/交易"):
            stock_id = msg.replace("/交易", "").strip()
            result = monitor_and_trade(stock_id)  # 你自己的交易主控函式
            line_bot_api.push_message(
                event.source.user_id,
                TextSendMessage(text=f"✅ 交易完成：{result}")
            )
        else:
            line_bot_api.push_message(
                event.source.user_id,
                TextSendMessage(text=f"📩 你說的是：{msg}")
            )

    threading.Thread(target=background_task).start()

# ✅ Render 雲端啟動用
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)