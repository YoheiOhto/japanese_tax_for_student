def calculate_income_tax(taxable_income, include_fukkou=False):
    """
    所得税額を計算（万円単位）

    Parameters:
        taxable_income (float): 課税所得（万円）
        include_fukkou (bool): 復興特別所得税（2.1%）を含めるか

    Returns:
        float: 所得税額（万円）
    """

    if taxable_income <= 195:
        tax_rate = 0.05
        deduction = 0
    elif taxable_income <= 330:
        tax_rate = 0.10
        deduction = 9.75
    elif taxable_income <= 695:
        tax_rate = 0.20
        deduction = 42.75
    elif taxable_income <= 900:
        tax_rate = 0.23
        deduction = 63.6
    elif taxable_income <= 1800:
        tax_rate = 0.33
        deduction = 153.6
    elif taxable_income <= 4000:
        tax_rate = 0.40
        deduction = 279.6
    else:
        tax_rate = 0.45
        deduction = 479.6

    base_tax = max(0, taxable_income * tax_rate - deduction)

    # 復興特別所得税（2037年まで）
    if include_fukkou:
        return base_tax * 1.021

    return base_tax
