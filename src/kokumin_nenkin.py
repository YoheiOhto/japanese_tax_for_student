# 国民年金 前能でいくらか安くなる、前納時には安くなる口座振替を使用していると仮定する　https://www.nenkin.go.jp/service/kokunen/hokenryo/zenno.html

def kokumin_nenkin_payment(frequency, payment_method):
    """
    国民年金の納付額と割引額を計算する関数（万円単位で返し、年額納付額も計算）。

    Parameters:
        frequency (str): 支払い頻度 ("2年前納", "1年前納", "6カ月前納", "当月末振替", "毎月納付")
        payment_method (str): 支払い方法 ("納付書払い", "クレジットカード払い", "口座振替")

    Returns:
        dict: 納付額（万円単位）、割引額（万円単位）、年額納付額（万円単位）を含む辞書
    """
    # 納付額と割引額の定義（円単位）
    payment_data = {
        "2年前納": {
            "納付書払い": {"amount": 398590, "discount": 15290},
            "クレジットカード払い": {"amount": 398590, "discount": 15290},
            "口座振替": {"amount": 397290, "discount": 16590},
        },
        "1年前納": {
            "納付書払い": {"amount": 200140, "discount": 3620},
            "クレジットカード払い": {"amount": 200140, "discount": 3620},
            "口座振替": {"amount": 199490, "discount": 4270},
        },
        "6カ月前納": {
            "納付書払い": {"amount": 101050, "discount": 830},
            "クレジットカード払い": {"amount": 101050, "discount": 830},
            "口座振替": {"amount": 100720, "discount": 1160},
        },
        "当月末振替": {
            "口座振替": {"amount": 16920, "discount": 60},
        },
        "毎月納付": {
            "納付書払い": {"amount": 16980, "discount": 0},
            "クレジットカード払い": {"amount": 16980, "discount": 0},
            "口座振替": {"amount": 16980, "discount": 0},
        },
    }

    # 各支払い頻度の年額換算用の係数
    frequency_to_multiplier = {
        "2年前納": 0.5,  # 2年間分で割る
        "1年前納": 1,
        "6カ月前納": 2,
        "当月末振替": 12,
        "毎月納付": 12,
    }

    try:
        result = payment_data[frequency][payment_method]
        multiplier = frequency_to_multiplier[frequency]

        # 万円単位で計算（納付額・割引額）
        amount_in_million = result["amount"] / 10000
        discount_in_million = result["discount"] / 10000

        # 年額換算（万円単位）
        annual_amount_in_million = amount_in_million * multiplier
    
        # 月額換算（万円単位）
        monthly_amount_in_million = annual_amount_in_million / 12

        return {
            "支払い頻度": frequency,
            "支払い方法": payment_method,
            "納付額": amount_in_million,
            "割引額": discount_in_million,
            "年額": annual_amount_in_million,
            "月額": monthly_amount_in_million
        }
    except KeyError:
        return {
            "エラー": "指定された支払い頻度または支払い方法が無効です。"
        }