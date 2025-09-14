from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, PushMessageRequest
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from fubon_api import FubonAdventure
import threading
import os

app = Flask(__name__)

# ✅ LINE 憑證（Render 上用環境變數設定）
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ✅ 財務查詢邏輯
def handle_account_query(user_id):
    try:
        print(f"🧙‍♂️ 正在查詢帳務：使用者 {user_id}")
        fubon = FubonAdventure()
        info = fubon.query_account()
        if not info:
            return "🔶 銷樣被封印了，可能是憑證失效或帳戶未開啟，請稍後再試。"

        return (
            "🧭 冒險者任庭的財務背包已開啟...\n"
            f"💼 銀袋餘額：${info['balance']:,} 金幣\n"
            f"📦 持股倉庫總值：${info['portfolio_value']:,} 金幣\n"
            f"🌪️ 損益風暴：{info['unrealized_pl']:,} 金幣波動\n"
            "\n⚔️ 若要進行交易，請輸入：/交易 [股票代碼]"
        )
    except Exception as e:
        print("⚠️ 財務查詢錯誤：", e)
        return "🔶 銷樣被封印了，可能是憑證失效或帳戶未開啟，請稍後再試。"

# ✅ 推送訊息封裝
def send_line_message(user_id, text):
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        message = TextMessage(text=text)
        request = PushMessageRequest(to=user_id, messages=[message])
        messaging_api.push_message_with_http_info(request)
        print(f"📨 已推送訊息給 {user_id}：{text}")

# ✅ webhook 路由
@app.route("/callback", methods=["POST"])
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

    # Step 2：背景執行邏輯
    def background_task(user_id, msg):
        print(f"🧙‍♂️ 背景任務啟動：{user_id} 說了 {msg}")
        if msg.startswith("/交易"):
            stock_id = msg.replace("/交易", "").strip()
            result = monitor_and_trade(stock_id)  # 你自己的交易函式
            reply = f"✅ 交易完成：{result}"
        elif msg == "/查詢帳務":
            reply = handle_account_query(user_id)
        else:
            reply = f"📩 你說的是：{msg}"

        send_line_message(user_id, reply)

    threading.Thread(target=background_task, args=(user_id, msg)).start()

# ✅ Render 雲端啟動用
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
