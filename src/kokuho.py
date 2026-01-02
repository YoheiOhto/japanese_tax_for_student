# 国保 https://www.city.bunkyo.lg.jp/b021/p000424.html
# 年齢的に介護保険を支払う必要がないと想定

def kokumin_kenko_hoken_bunkyo(
    total_income,
    num_persons=1,
    no_kaigo=True
):
    """
    国民健康保険料（文京区・令和6年度想定）
    
    Parameters:
        total_income (float): 総所得金額等（万円）
        num_persons (int): 被保険者数（世帯人数）
        no_kaigo (bool): 40歳未満で介護保険料なしと仮定
    
    Returns:
        dict: 年額・月額・内訳（万円）
    """

    # --- 所得割の算定基礎 ---
    sante_kiso = max(0, total_income - 43)

    # --- 料率（文京区 令和6年度） ---
    RATE_KISO = 0.0869
    RATE_SIEN = 0.0280

    KINTO_KISO = 4.91
    KINTO_SIEN = 1.65

    # --- 所得割 ---
    syotoku_kiso = sante_kiso * RATE_KISO
    syotoku_sien = sante_kiso * RATE_SIEN

    # --- 均等割 ---
    kinto_kiso = KINTO_KISO * num_persons
    kinto_sien = KINTO_SIEN * num_persons

    # --- 合計 ---
    kiso_hoken = syotoku_kiso + kinto_kiso
    sien_hoken = syotoku_sien + kinto_sien
    total = kiso_hoken + sien_hoken

    return {
        "算定基礎所得": sante_kiso,
        "総保険料（年額）": total,
        "月額": total / 12,
        "基礎分": kiso_hoken,
        "支援金分": sien_hoken
    }
