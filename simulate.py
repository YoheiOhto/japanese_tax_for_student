# %%
"""
総合納税額シミュレーター
【入力】
  - 給与収入リスト（複数の勤務先に対応）
  - 雑所得の収入・経費（副業・フリーランス想定）
  - 社会保険料控除額（国民年金・国保など）
  - 対象年（year）
 
【計算フロー】
  給与収入 → 給与所得（給与所得控除を差し引き）
  雑所得   = 収入 − 経費
  合計所得 = 給与所得 + 雑所得
 
  ── 所得税 ──
  課税所得 = 合計所得 − 基礎控除（国税） − 社会保険料控除
  所得税額 = calculate_income_tax(課税所得)
 
  ── 住民税 ──
  課税所得（住民税） = 合計所得 − 基礎控除（地方税） − 社会保険料控除
  住民税所得割       = 課税所得 × 10%
  調整控除を差し引き → 住民税額
 
【出典】
  国税庁「確定申告書等作成コーナー」計算ロジック準拠
  https://www.nta.go.jp/taxes/shiraberu/shinkoku/kakutei.htm
"""
 
from src import (
    kyuyo_syotoku_kojo,
    kiso_kojo_kuni,
    kiso_kojo_chiho,
    calculate_income_tax,
    tyosei_koujo,
)
 
 
# ============================================================
# 雑所得
# ============================================================
 
def zassyotoku(revenue: float, expenses: float) -> float:
    """
    雑所得を計算する（副業・フリーランス想定）。
 
    Parameters
    ----------
    revenue : float
        雑所得の収入金額（万円）
    expenses : float
        必要経費（万円）。収入に直接対応する費用のみ算入可。
 
    Returns
    -------
    float
        雑所得金額（万円）。マイナスは 0 として扱う（他の所得との損益通算不可）。
 
    Notes
    -----
    - 副業・フリーランスの報酬は原則「雑所得」に該当。
    - 給与所得との損益通算は不可（雑所得のマイナスは切り捨て）。
    - 300万円超の場合は収支内訳書の保存が必要（令和4年改正）。
    """
    return max(0.0, revenue - expenses)
 
 
# ============================================================
# メイン計算関数
# ============================================================
 
def simulate_tax(
    salaries: list[float],
    zassyotoku_revenue: float,
    zassyotoku_expenses: float,
    shakai_hoken_kojo: float,
    year: int = 2025,
    include_fukkou: bool = False,
) -> dict:
    """
    給与＋雑所得をもとに所得税・住民税を計算する。
 
    Parameters
    ----------
    salaries : list[float]
        給与収入のリスト（万円）。複数の勤務先がある場合は全て列挙する。
        例: [400.0, 80.0]  → メイン400万＋副業給与80万
    zassyotoku_revenue : float
        雑所得の収入金額（万円）。
    zassyotoku_expenses : float
        雑所得の必要経費（万円）。
    shakai_hoken_kojo : float
        社会保険料控除額（万円）。
        国民年金・国民健康保険料の実支払額を合計して渡す。
    year : int
        課税対象年。基礎控除・給与所得控除の計算に使用。
    include_fukkou : bool
        True = 復興特別所得税（2.1%）を所得税に加算。
 
    Returns
    -------
    dict
        所得・控除・税額の内訳（すべて万円単位）。
 
    Example
    -------
    >>> result = simulate_tax(
    ...     salaries=[400.0],
    ...     zassyotoku_revenue=100.0,
    ...     zassyotoku_expenses=20.0,
    ...     shakai_hoken_kojo=30.0,
    ...     year=2025,
    ... )
    >>> result["所得税額"]
    >>> result["住民税額（所得割）"]
    """
 
    # ── 1. 給与所得 ──────────────────────────────────────────
    # 複数給与は各給与に控除を適用してから合算（合算後控除ではない）
    kyuyo_shotoku_list = [
        s - kyuyo_syotoku_kojo(s, year) for s in salaries
    ]
    kyuyo_shotoku_total = sum(kyuyo_shotoku_list)
 
    # ── 2. 雑所得 ─────────────────────────────────────────────
    zasso = zassyotoku(zassyotoku_revenue, zassyotoku_expenses)
 
    # ── 3. 合計所得金額 ────────────────────────────────────────
    # 基礎控除の逓減判定に使う（社会保険料控除前）
    gokei_shotoku = kyuyo_shotoku_total + zasso
 
    # ── 4. 基礎控除 ───────────────────────────────────────────
    kiso_kuni  = kiso_kojo_kuni(gokei_shotoku, year)
    kiso_chiho = kiso_kojo_chiho(gokei_shotoku, year)
 
    # ── 5. 所得税の課税所得・税額 ─────────────────────────────
    kazei_shotoku_kuni = max(
        0.0,
        gokei_shotoku - kiso_kuni - shakai_hoken_kojo,
    )
    zei_kuni = calculate_income_tax(kazei_shotoku_kuni, include_fukkou)
 
    # ── 6. 住民税の課税所得・税額 ─────────────────────────────
    kazei_shotoku_chiho = max(
        0.0,
        gokei_shotoku - kiso_chiho - shakai_hoken_kojo,
    )
    # 所得割: 一律10%（市区町村民税6% + 都道府県民税4%）
    juminzei_shotokuwari_mae = kazei_shotoku_chiho * 0.10
 
    # 調整控除
    chosei = tyosei_koujo(kazei_shotoku_chiho, kiso_kuni, kiso_chiho)
    juminzei_shotokuwari = max(0.0, juminzei_shotokuwari_mae - chosei)
 
    # ── 7. 結果を返す ─────────────────────────────────────────
    return {
        # 入力サマリ
        "対象年":                  year,
        "給与収入合計":            sum(salaries),
        "給与収入内訳":            salaries,
        "雑所得収入":              zassyotoku_revenue,
        "雑所得経費":              zassyotoku_expenses,
        "社会保険料控除":          shakai_hoken_kojo,
 
        # 所得計算
        "給与所得合計":            round(kyuyo_shotoku_total, 4),
        "給与所得内訳":            [round(x, 4) for x in kyuyo_shotoku_list],
        "雑所得":                  round(zasso, 4),
        "合計所得金額":            round(gokei_shotoku, 4),
 
        # 控除
        "基礎控除（所得税）":      kiso_kuni,
        "基礎控除（住民税）":      kiso_chiho,
        "調整控除（住民税）":      round(chosei, 4),
 
        # 課税所得
        "課税所得（所得税）":      round(kazei_shotoku_kuni, 4),
        "課税所得（住民税）":      round(kazei_shotoku_chiho, 4),
 
        # 税額
        "所得税額":                round(zei_kuni, 4),
        "住民税額（所得割）":      round(juminzei_shotokuwari, 4),
        "合計納税額":              round(zei_kuni + juminzei_shotokuwari, 4),
 
        # フラグ
        "復興特別所得税込み":      include_fukkou,
    }
 
 
# ============================================================
# 年度比較
# ============================================================
 
def compare_tax_by_year(
    salaries: list[float],
    zassyotoku_revenue: float,
    zassyotoku_expenses: float,
    shakai_hoken_kojo: float,
    years: list[int] = [2024, 2025, 2026, 2027],
    include_fukkou: bool = False,
) -> dict[int, dict]:
    """
    複数年度の納税額を一括比較する。
 
    Parameters
    ----------
    salaries, zassyotoku_revenue, zassyotoku_expenses, shakai_hoken_kojo
        simulate_tax() と同じ。
    years : list[int]
        比較したい年度のリスト。デフォルトは 2024〜2027。
 
    Returns
    -------
    dict[int, dict]
        { year: simulate_tax() の戻り値 } の辞書。
 
    Example
    -------
    >>> results = compare_tax_by_year([400.0], 100.0, 20.0, 30.0)
    >>> for year, r in results.items():
    ...     print(year, r["合計納税額"])
    """
    return {
        y: simulate_tax(
            salaries=salaries,
            zassyotoku_revenue=zassyotoku_revenue,
            zassyotoku_expenses=zassyotoku_expenses,
            shakai_hoken_kojo=shakai_hoken_kojo,
            year=y,
            include_fukkou=include_fukkou,
        )
        for y in years
    }
# %%
