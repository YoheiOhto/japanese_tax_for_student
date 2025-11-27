def simulate_2026(all_salaries, zasshotoku, keihi, kyuyo_kojo_func, kiso_kuni_func, kiso_chiho_func):
    """
    複数給与＋雑所得＋経費から、所得税・復興特別所得税・住民税・国保を計算するシミュレーション
    
    Parameters:
        all_salaries (float): 給与合計（万円）
        zasshotoku (float): 雑所得（奨学金）（万円）
        keihi (float): 雑所得用経費（万円）
        kyuyo_kojo_func (function): 給与所得控除計算関数
        kiso_kuni_func (function): 国の基礎控除計算関数
        kiso_chiho_func (function): 住民税の基礎控除計算関数
        
    Returns:
        dict: 課税所得、所得税、復興特別所得税、住民税、国保（年額・月額）
    """
    # 給与所得控除
    kyuyo_kojo = kyuyo_kojo_func(all_salaries)
    
    # 雑所得（経費控除後）
    zasshotoku_taxable = max(0, zasshotoku - keihi)
    
    # 所得税用課税所得
    taxable_income_income_tax = max(0, all_salaries - kyuyo_kojo + zasshotoku_taxable - kiso_kuni_func(all_salaries))
    
    # 所得税
    income_tax = calculate_income_tax(taxable_income_income_tax)
    monthly_income_tax = income_tax / 12
    
    # 復興特別所得税
    hukko_tax = income_tax * 0.021
    monthly_hukko = hukko_tax / 12
    
    # 住民税用課税所得
    taxable_income_juminzei = max(0, all_salaries - kyuyo_kojo + zasshotoku_taxable - kiso_chiho_func(all_salaries))
    
    # 住民税概算（所得割10%＋均等割0.43万円）
    juminzei = taxable_income_juminzei * 0.10 + 0.43
    monthly_juminzei = juminzei / 12
    
    # 国保概算（基礎分＋支援金分）
    sante_kiso = max(0, all_salaries - kyuyo_kojo - kiso_chiho_func(all_salaries))
    # 基礎分
    kiso_wari = sante_kiso * 0.0869
    kinto_wari = 4.91
    kiso_hoken = kiso_wari + kinto_wari
    # 支援金分
    sien_wari = sante_kiso * 0.028
    kinto_sien = 1.65
    sien_hoken = sien_wari + kinto_sien
    monthly_sien_hoken = sien_hoken / 12
    # 合計
    kokuho = kiso_hoken + sien_hoken
    monthly_kokuho = kokuho / 12

    monthly_total = monthly_income_tax + monthly_hukko + monthly_juminzei + monthly_kokuho
    annual_total = monthly_total * 12

    annual_income = all_salaries + zasshotoku
    monthly_income = annual_income / 12

    annual = {
        "収入合計（年額）": annual_income,
        "合計（年額）": annual_total,
        "所得税": income_tax,
        "復興特別所得税": hukko_tax,
        "住民税": juminzei,
        "国保（年額）": kokuho
    }
    
    monthly = {
        "収入合計（月額）": monthly_income,
        "合計（月額）": monthly_total,
        "所得税（月額）": monthly_income_tax,
        "復興特別所得税（月額）": monthly_hukko,
        "住民税（月額）": monthly_juminzei,
        "国保（月額）": monthly_kokuho
    }

    return annual, monthly

# example usage:
# result1 = simulate_2026(
#     all_salaries = baito_26 + yakugakubu_26 + kougakubu_26,
#     zasshotoku = boost_26,
#     keihi = keihi_26,
#     kyuyo_kojo_func = kyuyo_syotoku_kojo_calc_2025,
#     kiso_kuni_func = kiso_kojo_kuni_2025,
#     kiso_chiho_func = kiso_kojo_chiho
# )