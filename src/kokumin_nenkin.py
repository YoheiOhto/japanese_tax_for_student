def kokumin_nenkin_payment(frequency="1年前納", payment_method="口座振替"):
    """
    国民年金（令和6年度）納付額計算
    戻り値はすべて万円単位
    """

    payment_data = {
        "2年前納": {
            "納付書払い": (398590, 15290),
            "クレジットカード払い": (398590, 15290),
            "口座振替": (397290, 16590),
        },
        "1年前納": {
            "納付書払い": (200140, 3620),
            "クレジットカード払い": (200140, 3620),
            "口座振替": (199490, 4270),
        },
        "6カ月前納": {
            "納付書払い": (101050, 830),
            "クレジットカード払い": (101050, 830),
            "口座振替": (100720, 1160),
        },
        "当月末振替": {
            "口座振替": (16920, 60),
        },
        "毎月納付": {
            "納付書払い": (16980, 0),
            "クレジットカード払い": (16980, 0),
            "口座振替": (16980, 0),
        },
    }

    annual_multiplier = {
        "2年前納": 0.5,
        "1年前納": 1,
        "6カ月前納": 2,
        "当月末振替": 12,
        "毎月納付": 12,
    }

    if frequency not in payment_data:
        raise ValueError("無効な支払い頻度")

    if payment_method not in payment_data[frequency]:
        raise ValueError("この支払い頻度では選べない支払い方法")

    amount, discount = payment_data[frequency][payment_method]

    amount_m = amount / 10000
    discount_m = discount / 10000

    annual = amount_m * annual_multiplier[frequency]
    monthly = annual / 12

    return {
        "支払い頻度": frequency,
        "支払い方法": payment_method,
        "実支払額": amount_m,
        "割引額": discount_m,
        "年額": annual,
        "月額": monthly
    }
