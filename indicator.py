import pandas as pd

def reshape_kbars_to_df(kbars):
    """
    將富邦 API 回傳的 kbars 資料轉換為 pandas DataFrame
    並依時間排序、設為索引
    """
    df = pd.DataFrame(kbars)
    df['ts'] = pd.to_datetime(df['ts'])
    df.set_index('ts', inplace=True)
    df.sort_index(inplace=True)
    return df


def calculate_ma(df, window):
    """
    計算移動平均線（MA）
    """
    if 'close' not in df.columns:
        raise ValueError("DataFrame 缺少 'close' 欄位")
    return df['close'].rolling(window=window).mean()


def is_golden_cross(df, short_window=5, long_window=10):
    """
    判斷是否出現黃金交叉（MA5 上穿 MA10）
    - short_window：短期均線天數（預設 5）
    - long_window：長期均線天數（預設 10）
    回傳 True 表示觸發交易條件
    """
    if df.empty or len(df) < long_window + 1:
        print("⚠️ 資料不足，無法判斷黃金交叉")
        return False

    ma_short = calculate_ma(df, short_window)
    ma_long = calculate_ma(df, long_window)

    # 檢查是否有 NaN 值
    if pd.isna(ma_short.iloc[-2]) or pd.isna(ma_short.iloc[-1]):
        print("⚠️ 短期均線資料不足")
        return False
    if pd.isna(ma_long.iloc[-2]) or pd.isna(ma_long.iloc[-1]):
        print("⚠️ 長期均線資料不足")
        return False

    cross = ma_short.iloc[-2] < ma_long.iloc[-2] and ma_short.iloc[-1] > ma_long.iloc[-1]
    if cross:
        print("✅ 黃金交叉成立")
    else:
        print("⛔ 尚未達成黃金交叉")

    return cross
