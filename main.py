from trade_logic import prepare_order, execute_order
from threading import Thread
from monitor import start_monitoring, stop_monitoring


user_state = {}

def handle_message(user_id, message):
    if message == "開始存股":
        user_state[user_id] = {"step": "await_stock_id"}
        return "📥 請輸入股票代號："

    elif user_state.get(user_id, {}).get("step") == "await_stock_id":
        stock_id = message.strip()
        result = prepare_order(stock_id)
        user_state[user_id] = {
            "step": "confirm_order",
            "order_data": result
        }
        return result["preview"]

    elif user_state.get(user_id, {}).get("step") == "confirm_order":
        if message == "是":
            reply = "🧙‍♂️ 儀式啟動：開始偵測……"
            Thread(target=start_monitoring, args=(user_id,)).start()
            return reply
        else:
            user_state[user_id] = {"step": "await_stock_id"}
            return "📥 請重新輸入股票代號："

    elif message == "停止存股":
        stop_monitoring(user_id)
        return "🛑 今日未能交易，明日再接再厲"

    return "🤖 無法識別的指令"