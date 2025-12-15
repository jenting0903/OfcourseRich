from flask import Flask, request, abort
from stock_service import prepare_stock_info, monitor_and_trade

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    body = request.json
    user_text = body["events"][0]["message"]["text"]

    if user_text == "開始存股":
        return "請輸入想要存股之股票代號："

    elif user_text.isdigit():  # 使用者輸入股票代號
        info = prepare_stock_info(user_text)
        return f"""
股票代碼：{info['stock_no']}
股票名稱：{info['stock_name']}
零股價格：{info['price']}
預估可動用資金：{info['usable_cash']}
預估可購買股數：{info['est_qty']}
是否執行存股交易？請回覆「是」或「否」
"""

    elif user_text == "是":
        result = monitor_and_trade("2330")  # 假設台積電
        if result["status"] == "success":
            return f"""
交易成功！
股票代碼：{result['stock_no']}
股票名稱：{result['stock_name']}
成交價格：{result['price']}
成交股數：{result['qty']}
成交時間：{result['time']}
"""
        else:
            return f"""
今日未交易！
預估可動用資金：{result['usable_cash']}
"""

    elif user_text == "否":
        return "請輸入想要存股之股票代號："

    elif user_text == "停止存股":
        return "存股流程已停止"

    return "未知指令"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)