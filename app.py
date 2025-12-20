from flask import Flask, request, abort
from stock_service import prepare_stock_info, monitor_and_trade

app = Flask(__name__)

# 全域變數暫存最後查詢的股票代號
LAST_STOCK_NO = None

@app.route("/callback", methods=["POST"])
def callback():
    global LAST_STOCK_NO

    body = request.json
    user_text = body["events"][0]["message"]["text"].strip()

    # 開始存股
    if user_text == "開始存股":
        return "請輸入想要存股之股票代號："

    # 使用者輸入股票代號
    elif user_text.isdigit():
        info = prepare_stock_info(user_text)
        LAST_STOCK_NO = user_text  # 自動暫存最後查詢的股票代號
        return f"""
股票代碼：{info['stock_no']}
股票名稱：{info['stock_name']}
零股價格(五檔賣出價第一檔)：{info['price']}
預估可動用資金(80%)：{info['usable_cash']}
預估可購買之股數：{info['est_qty']}
是否執行存股交易？請回覆「是」或「否」
"""

    # 使用者確認交易
    elif user_text == "是":
        if LAST_STOCK_NO is None:
            return "尚未輸入股票代號，請先輸入。"

        result = monitor_and_trade(LAST_STOCK_NO)

        if result["status"] == "success":
            return f"""
交易成功！
股票代碼：{result['stock_no']}
股票名稱：{result['stock_name']}
購買零股成交價格：{result['price']}
成交股數：{result['qty']}
購買總金額：{result['amount']}
成交時間：{result['time']}
"""
        else:
            return f"""
今日未交易！
預估可動用資金(帳戶總金額80%)：{result['usable_cash']}
"""

    elif user_text == "否":
        return "請輸入想要存股之股票代號："

    elif user_text == "停止存股":
        LAST_STOCK_NO = None  # 清除暫存代號
        return "存股流程已停止"

    return "未知指令"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
