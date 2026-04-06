_NENKIN_RATES: dict = {
    2025: {
        "2年前納": {
            "納付書払い":          (409490, 15670),
            "クレジットカード払い": (409490, 15670),
            "口座振替":             (408150, 17010),
        },
        "1年前納": {
            "納付書払い":          (206390,  3730),
            "クレジットカード払い": (206390,  3730),
            "口座振替":             (205720,  4400),
        },
        "6カ月前納": {
            "納付書払い":          (104210,   850),
            "クレジットカード払い": (104210,   850),
            "口座振替":             (103870,  1190),
        },
        "当月末振替": {
            "口座振替": (17450, 60),   # 早割（月額）
        },
        "毎月納付": {
            "納付書払い":          (17510, 0),
            "クレジットカード払い": (17510, 0),
            "口座振替":             (17510, 0),
        },
    },
    2026: {
        # 2年前納は令和7・8年度またぎのため令和7年度値と同じ
        "2年前納": {
            "納付書払い":          (409490, 15670),
            "クレジットカード払い": (409490, 15670),
            "口座振替":             (408150, 17010),
        },
        # 以下は月額17,920円をもとにした概算値（正式発表後に要更新）
        "1年前納": {
            "納付書払い":          (212030,  2810),
            "クレジットカード払い": (212030,  2810),
            "口座振替":             (211310,  3530),
        },
        "6カ月前納": {
            "納付書払い":          (106890,   630),
            "クレジットカード払い": (106890,   630),
            "口座振替":             (106580,   940),
        },
        "当月末振替": {
            "口座振替": (17860, 60),   # 早割（月額・概算）
        },
        "毎月納付": {
            "納付書払い":          (17920, 0),
            "クレジットカード払い": (17920, 0),
            "口座振替":             (17920, 0),
        },
    },
}
 
_ANNUAL_MULT = {
    "2年前納":   0.5,   # 2年分一括払いのため年換算は÷2
    "1年前納":   1,
    "6カ月前納": 2,
    "当月末振替": 12,
    "毎月納付":  12,
}
 
_NENKIN_LABEL = {
    2025: "令和7年度（2025年4月〜2026年3月）月額17,510円",
    2026: "令和8年度（2026年4月〜2027年3月）月額17,920円（1年・6カ月前納は概算）",
}
 
 
def kokumin_nenkin_payment(
    frequency: str = "1年前納",
    payment_method: str = "口座振替",
    fiscal_year: int = 2025,
) -> dict:
    """
    国民年金の納付額を計算する。
 
    Parameters
    ----------
    frequency : str
        支払い頻度。
        "2年前納" / "1年前納" / "6カ月前納" / "当月末振替" / "毎月納付"
    payment_method : str
        支払い方法。
        "口座振替" / "納付書払い" / "クレジットカード払い"
        ※ "当月末振替" は "口座振替" のみ対応。
    fiscal_year : int
        適用年度。2025（令和7年度）または 2026（令和8年度）。
 
    Returns
    -------
    dict
        実支払額・割引額・年換算額・月換算額（すべて万円単位）
 
    Example
    -------
    >>> kokumin_nenkin_payment("1年前納", "口座振替", 2025)
    {'実支払額（万円）': 20.572, '割引額（万円）': 0.44, ...}
 
    >>> kokumin_nenkin_payment("毎月納付", "口座振替", 2026)
    {'実支払額（万円）': 1.792, '割引額（万円）': 0.0, ...}
    """
 
    if fiscal_year not in _NENKIN_RATES:
        raise ValueError(
            f"fiscal_year は {sorted(_NENKIN_RATES.keys())} のいずれかを指定してください。"
        )
 
    freq_table = _NENKIN_RATES[fiscal_year]
 
    if frequency not in freq_table:
        raise ValueError(
            f"無効な支払い頻度: '{frequency}'. 有効値: {list(freq_table.keys())}"
        )
 
    method_table = freq_table[frequency]
 
    if payment_method not in method_table:
        raise ValueError(
            f"'{frequency}' では '{payment_method}' は選べません。"
            f" 有効値: {list(method_table.keys())}"
        )
 
    amount, discount = method_table[payment_method]
    amount_m   = amount   / 10000
    discount_m = discount / 10000
    annual     = amount_m * _ANNUAL_MULT[frequency]
    monthly    = annual   / 12
 
    return {
        "適用年度":         _NENKIN_LABEL[fiscal_year],
        "支払い頻度":       frequency,
        "支払い方法":       payment_method,
        "実支払額（万円）":  round(amount_m,   4),
        "割引額（万円）":   round(discount_m, 4),
        "年換算額（万円）":  round(annual,     4),
        "月換算額（万円）":  round(monthly,    4),
    }