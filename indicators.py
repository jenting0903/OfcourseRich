def sma(values, period):
    if period <= 0:
        raise ValueError("period must be > 0")

    out = []
    window_sum = 0.0

    for i, v in enumerate(values):
        window_sum += v
        if i >= period:
            window_sum -= values[i - period]

        if i + 1 >= period:
            out.append(window_sum / period)
        else:
            out.append(None)

    return out


def crossed_above(fast, slow):
    """黃金交叉：上一根 fast ≤ slow，這一根 fast > slow"""
    if len(fast) < 2 or len(slow) < 2:
        return False

    f_prev, f_curr = fast[-2], fast[-1]
    s_prev, s_curr = slow[-2], slow[-1]

    if None in (f_prev, f_curr, s_prev, s_curr):
        return False

    return f_prev <= s_prev and f_curr > s_curr


def golden_cross_1m(close_series, fast_period=5, slow_period=20):
    fast = sma(close_series, fast_period)
    slow = sma(close_series, slow_period)
    return crossed_above(fast, slow), fast, slow
