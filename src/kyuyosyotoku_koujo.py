def kyuyo_syotoku_kojo(income: float, year: int) -> float:
    """
    給与所得控除（万円単位）
 
    Parameters
    ----------
    income : float
        給与収入（万円）
    year : int
        課税対象年。2024以前 / 2025以降 で最低保障額が異なる。
 
    Returns
    -------
    float
        給与所得控除額（万円）
 
    制度変遷
    --------
    2024年以前 : 最低保障額 55万円（収入162.5万円未満はこの額を適用）
    2025年以降 : 最低保障額 65万円（令和7年度改正で10万円引き上げ）
                 ※ これにより課税最低限が103万円→160万円（給与所得控除65+基礎控除95）に。
    上限（850万円超）: 195万円（変更なし）
 
    出典: 国税庁「令和7年度税制改正による所得税の基礎控除の見直し等について」
    """
 
    # 最低保障額（2025年以降・2027年以降も同値で恒久化）
    min_kojo = 55 if year <= 2024 else 65
 
    if income <= 162.5:
        return min_kojo
    elif income <= 180:
        # 最低保障額を下回らないよう max を取る
        return max(min_kojo, income * 0.40 - 10)
    elif income <= 360:
        return income * 0.30 + 8
    elif income <= 660:
        return income * 0.20 + 44
    elif income <= 850:
        return income * 0.10 + 110
    else:
        return 195