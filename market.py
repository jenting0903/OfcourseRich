from fubon_neo.sdk import FubonSDK

def get_sdk():
    """
    登入富邦 API，回傳 SDK 與帳號物件
    """
    sdk = FubonSDK()
    login_result = self.sdk.login(
                os.environ["FUBON_USER_ID"],
                os.environ["FUBON_PASSWORD"],
                os.environ["FUBON_CERT_PATH"],
                os.environ["FUBON_CERT_PASSWORD"]
            )
    if not login_result.is_success:
        return None, None
    return sdk, login_result.data[0]


def get_real_price(stock_id, sdk=None):
    """
    使用富邦 Neo API 取得即時報價與股票名稱
    """
    try:
        if not sdk:
            sdk, _ = get_sdk()
            if not sdk:
                return None, None

        quote_result = sdk.quote(stock_id)
        if not quote_result.is_success:
            return None, None

        price = float(quote_result.data.last_price)
        name = quote_result.data.stock_name
        return price, name
    except Exception:
        return None, None


def estimate_quantity(price, budget):
    """
    根據預算與股價，估算可購買股數（以整股為單位）
    """
    try:
        if price <= 0:
            return 0
        return int(budget // price)
    except Exception:
        return 0


def get_account_info():
    """
    查詢帳戶資訊：帳號、餘額、可交易餘額（80%）
    """
    sdk, account = get_sdk()
    if not sdk or not account:
        return None

    balance_result = sdk.accounting.bank_remain(account)
    if not balance_result.is_success:
        return None

    balance = int(balance_result.data.available_balance)
    tradable = int(balance * 0.8)

    return {
        "account": account.account_id,
        "balance": balance,
        "tradable": tradable
    }


def decide_order_type(price, budget, fee_buffer=50):
    """
    根據預算與股價，自動判斷是否執行整股或零股交易
    - 若預算足以買 100 股（含手續費），則執行整股
    - 否則執行零股
    """
    try:
        min_lot_cost = price * 1000 + fee_buffer
        if budget >= min_lot_cost:
            quantity = int(budget // (price * 1000)) * 1000
            return "lot", quantity
        else:
            quantity = int(budget // price)
            return "odd", quantity
    except Exception:
        return "odd", 0
