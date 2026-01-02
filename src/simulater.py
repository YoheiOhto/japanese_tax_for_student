from .syotoku_zei import calculate_income_tax
from .jumin_zei import tyosei_koujo

def simulate_core(
    all_salaries,
    zasshotoku,
    keihi,
    kyuyo_kojo_func,
    kiso_kuni_func,
    kiso_chiho_func,
):
    # --- 給与所得 ---
    kyuyo_kojo = kyuyo_kojo_func(all_salaries)
    kyuyo_shotoku = max(0, all_salaries - kyuyo_kojo)

    # --- 雑所得 ---
    zasshotoku_taxable = max(0, zasshotoku - keihi)

    # --- 合計所得金額 ---
    total_income = kyuyo_shotoku + zasshotoku_taxable

    # =====================
    # 所得税
    # =====================
    kiso_kuni = kiso_kuni_func(total_income)
    taxable_income_income_tax = max(0, total_income - kiso_kuni)

    income_tax = calculate_income_tax(taxable_income_income_tax)
    hukko_tax = income_tax * 0.021

    # =====================
    # 住民税（調整控除あり）
    # =====================
    kiso_chiho = kiso_chiho_func(total_income)
    taxable_income_jumin = max(0, total_income - kiso_chiho)

    tyosei = tyosei_koujo(
        taxable_income_jumin,
        kiso_kuni,
        kiso_chiho,
    )

    juminzei = taxable_income_jumin * 0.10 + 0.43 - tyosei
    juminzei = max(0, juminzei)

    # =====================
    # 国保（文京区・介護なし）
    # =====================
    sante_kiso = max(0, total_income - 43)

    kokuho = (
        sante_kiso * 0.0869 +
        sante_kiso * 0.028 +
        4.91 +
        1.65
    )

    # =====================
    # 集計
    # =====================
    annual_income = all_salaries + zasshotoku
    annual_total = income_tax + hukko_tax + juminzei + kokuho

    return {
        "年収": annual_income,
        "手取り": annual_income - annual_total,
        "支出合計": annual_total,
        "所得税": income_tax,
        "復興特別所得税": hukko_tax,
        "住民税": juminzei,
        "国保": kokuho,
    }
