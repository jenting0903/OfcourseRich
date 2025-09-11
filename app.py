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

# 接收 LINE webhook 的入口
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理文字訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.strip()

    # 範例：收到 "/交易 2330" 指令
    if msg.startswith("/交易"):
        stock_id = msg.replace("/交易", "").strip()
        reply = f"📈 準備執行 {stock_id} 的交易流程..."
        # 你可以在這裡呼叫 monitor_and_trade(stock_id)
    else:
        reply = f"你說的是：{msg}"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

# Render 雲端啟動用
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
