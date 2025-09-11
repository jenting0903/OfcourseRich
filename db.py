import os
import json
from datetime import datetime, timedelta

def get_yesterday_balance(folder="trades"):
    """
    讀取昨日帳戶餘額，若無紀錄則回傳 0
    """
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    file_path = os.path.join(folder, f"{date_str}.json")

    if not os.path.exists(file_path):
        return 0

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return int(data.get("account_balance", 0))


def record_trade(data, folder="trades"):
    """
    儲存交易紀錄 JSON（包含股票代碼、股數、總金額、餘額等）
    """
    if not os.path.exists(folder):
        os.makedirs(folder)

    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(folder, f"{date_str}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record_balance_only(balance, folder="trades"):
    """
    儲存當日帳戶餘額（即使沒有交易）
    """
    if not os.path.exists(folder):
        os.makedirs(folder)

    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(folder, f"{date_str}.json")

    data = {
        "account_balance": balance,
        "stock_id": None,
        "stock_name": None,
        "quantity": 0,
        "total_amount": 0,
        "order_type": "none"
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
