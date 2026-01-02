def kiso_kojo_kuni(income, year):
    """
    所得税の基礎控除（年別）
    year: 2024, 2025, 2026
    """

    # --- 2024年（現行） ---
    if year == 2024:
        if income <= 2400:
            return 48
        elif income <= 2450:
            return 32
        elif income <= 2500:
            return 16
        else:
            return 0

    # --- 2025年（自民・宮沢折衷案） ---
    elif year == 2025:
        if income <= 2400:
            return 58
        elif income <= 2450:
            return 32
        elif income <= 2500:
            return 16
        else:
            return 0

    # --- 2026年（玉木案フル適用仮定） ---
    elif year == 2026:
        if income <= 2400:
            return 123
        elif income <= 2450:
            return 32
        elif income <= 2500:
            return 16
        else:
            return 0

    else:
        raise ValueError("year must be 2024, 2025, or 2026")

def kiso_kojo_chiho(income):
    """
    住民税の基礎控除（2024–2026 共通）
    """
    if income <= 2400:
        return 43
    elif income <= 2450:
        return 29
    elif income <= 2500:
        return 15
    else:
        return 0
