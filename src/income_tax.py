def calculate_income_tax(taxable_income: float, include_fukkou: bool = False) -> float:
    """
    所得税額を計算する（万円単位）

    Parameters
    ----------
    taxable_income : float
        課税所得（万円）。所得から各種控除を差し引いた後の金額。
    include_fukkou : bool
        True = 復興特別所得税（2.1%加算、2037年まで）を含める。

    Returns
    -------
    float
        所得税額（万円）

    税率表（超過累進課税）
    ----------------------
    課税所得        税率    控除額
    〜195万円       5%      0万円
    〜330万円      10%      9.75万円
    〜695万円      20%     42.75万円
    〜900万円      23%     63.6万円
    〜1,800万円    33%    153.6万円
    〜4,000万円    40%    279.6万円
    4,000万円超    45%    479.6万円

    ※ 税率表自体は令和7年度改正でも変更なし。
    出典: 国税庁「所得税の税率」
    https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2260.htm
    """

    brackets = [
        (195,          0.05,   0.00),
        (330,          0.10,   9.75),
        (695,          0.20,  42.75),
        (900,          0.23,  63.60),
        (1800,         0.33, 153.60),
        (4000,         0.40, 279.60),
        (float("inf"), 0.45, 479.60),
    ]

    tax_rate = deduction = 0.0
    for threshold, rate, ded in brackets:
        if taxable_income <= threshold:
            tax_rate, deduction = rate, ded
            break

    base_tax = max(0.0, taxable_income * tax_rate - deduction)
    return round(base_tax * 1.021 if include_fukkou else base_tax, 6)
