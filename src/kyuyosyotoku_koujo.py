def kyuyo_syotoku_kojo(income, year):
    """
    給与所得控除（年別・万円単位）
    year: 2024, 2025, 2026
    """

    # --- 最低保障額 ---
    if year == 2024 or year == 2026:
        min_kojo = 55
        min_threshold = 162.5
    elif year == 2025:
        min_kojo = 65
        min_threshold = 162.5
    else:
        raise ValueError("year must be 2024, 2025, or 2026")

    # --- 控除計算 ---
    if income <= min_threshold:
        return min_kojo
    elif income <= 180:
        return income * 0.40 - 10
    elif income <= 360:
        return income * 0.30 + 8
    elif income <= 660:
        return income * 0.20 + 44
    elif income <= 850:
        return income * 0.10 + 110
    else:
        return 195
