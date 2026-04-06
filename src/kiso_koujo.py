def kiso_kojo_kuni(income: float, year: int) -> float:
    """
    所得税の基礎控除（万円単位）
 
    Parameters
    ----------
    income : float
        合計所得金額（万円）
    year : int
        課税対象年。2024以前 / 2025 / 2026 / 2027以降 で制度が異なる。
 
    Returns
    -------
    float
        基礎控除額（万円）
 
    制度変遷
    --------
    2024年以前  : 2,400万円以下は一律 48万円
    2025・2026年 : 令和7年度改正により9段階テーブルへ変更（経過措置あり）
                   ・132万円以下              → 95万円（恒久）
                   ・132万円超〜336万円以下   → 88万円（2027年〜は58万円）
                   ・336万円超〜489万円以下   → 68万円（2027年〜は58万円）
                   ・489万円超〜655万円以下   → 63万円（2027年〜は58万円）
                   ・655万円超〜2,350万円以下 → 58万円（恒久）
                   ・2,350万円超〜2,400万円以下 → 48万円（変更なし）
                   ・2,400万円超〜2,450万円以下 → 32万円（逓減・変更なし）
                   ・2,450万円超〜2,500万円以下 → 16万円（逓減・変更なし）
                   ・2,500万円超              →  0万円（変更なし）
    2027年以降  : 経過措置終了。132万円超〜2,350万円以下は一律58万円に恒久化。
    """
 
    if year <= 2024:
        if income <= 2400:
            return 48
        elif income <= 2450:
            return 32
        elif income <= 2500:
            return 16
        else:
            return 0
 
    elif year in (2025, 2026):
        if income <= 132:
            return 95
        elif income <= 336:
            return 88
        elif income <= 489:
            return 68
        elif income <= 655:
            return 63
        elif income <= 2350:
            return 58
        elif income <= 2400:
            return 48
        elif income <= 2450:
            return 32
        elif income <= 2500:
            return 16
        else:
            return 0
 
    else:  # year >= 2027
        if income <= 132:
            return 95
        elif income <= 2350:
            return 58
        elif income <= 2400:
            return 48
        elif income <= 2450:
            return 32
        elif income <= 2500:
            return 16
        else:
            return 0

def kiso_kojo_chiho(income: float, year: int = 2025) -> float:
    """
    住民税の基礎控除（万円単位）
 
    令和7年度改正でも据え置き。2,400万円以下は一律43万円。
    year 引数は他関数との統一のために受け取るが、現時点では値に影響しない。
    将来の改正で変更された場合はここを更新する。
 
    Parameters
    ----------
    income : float
        合計所得金額（万円）
    year : int
        課税対象年（現行制度では値に影響しない）
 
    Returns
    -------
    float
        基礎控除額（万円）
    """
    if income <= 2400:
        return 43
    elif income <= 2450:
        return 29
    elif income <= 2500:
        return 15
    else:
        return 0
 
