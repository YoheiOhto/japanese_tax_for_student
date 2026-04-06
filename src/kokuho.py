# 国保 https://www.city.bunkyo.lg.jp/b021/p000424.html
# 年齢的に介護保険を支払う必要がないと想定

_BUNKYO_RATES = {
    2025: (0.0869, 0.0280, 4.91,  1.65),  # 令和7年度
    2026: (0.0751, 0.0280, 4.76,  1.76),  # 令和8年度（子ども支援金分が新設）
}

def kokumin_kenko_hoken_bunkyo(
    total_income: float,
    num_persons: int = 1,
    fiscal_year: int = 2025,
    no_kaigo: bool = True,
) -> dict:
    """
    国民健康保険料（文京区）
 
    Parameters
    ----------
    total_income : float
        総所得金額等（万円）
    num_persons : int
        被保険者数（世帯人数）
    fiscal_year : int
        年度。2025（令和7年度）または 2026（令和8年度）。
        ※ 2026年度から子ども支援金分（18歳以上・所得割0.27%・均等割3,000円）が新設。
    no_kaigo : bool
        True = 介護分なし（40歳未満 or 65歳以上と仮定）。
        介護分（40〜64歳）を含む場合は別途加算が必要。
 
    Returns
    -------
    dict
        年額・月額・内訳（万円）
 
    令和8年度（2026年度）の変更点
    -------------------------------
    - 基礎分所得割: 8.69% → 7.51%
    - 基礎分均等割: 49,100円 → 47,600円
    - 支援金分均等割: 16,500円 → 17,600円
    - 子ども支援金分（新設）: 所得割0.27%、均等割3,000円（18歳以上対象）
    - 介護分（40〜64歳）: 所得割2.43%、均等割17,800円
 
    出典: 文京区「保険料の計算方法」（2026年4月1日更新）
    https://www.city.bunkyo.lg.jp/b021/p000424.html
    """
 
    if fiscal_year not in _BUNKYO_RATES:
        raise ValueError(
            f"fiscal_year は {sorted(_BUNKYO_RATES.keys())} のいずれかを指定してください。"
        )
 
    rate_kiso, rate_sien, kinto_kiso, kinto_sien = _BUNKYO_RATES[fiscal_year]
 
    # 所得割の算定基礎（住民税基礎控除43万円を控除）
    sante_kiso = max(0.0, total_income - 43)
 
    # 所得割
    syotoku_kiso = sante_kiso * rate_kiso
    syotoku_sien = sante_kiso * rate_sien
 
    # 均等割
    kintos_kiso = kinto_kiso * num_persons
    kintos_sien = kinto_sien * num_persons
 
    kiso_hoken = syotoku_kiso + kintos_kiso
    sien_hoken = syotoku_sien + kintos_sien
    total = kiso_hoken + sien_hoken
 
    labels = {
        2025: "令和7年度（2025年4月〜2026年3月）",
        2026: "令和8年度（2026年4月〜2027年3月）※子ども支援金分・介護分は別途",
    }
 
    return {
        "適用年度":         labels[fiscal_year],
        "算定基礎所得":     sante_kiso,
        "総保険料（年額）":  total,
        "月額":             total / 12,
        "基礎分":           kiso_hoken,
        "支援金分":         sien_hoken,
    }
 