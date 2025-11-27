# 所得税 https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2260.htm
# 定額減税 https://www.nta.go.jp/users/gensen/teigakugenzei/01.htm
# 定額減税は関数の外部で計算する。

def calculate_income_tax(taxable_income):
    if taxable_income <= 194.9:
        tax_rate = 0.05
        deduction = 0
    elif taxable_income <= 329.9:
        tax_rate = 0.10
        deduction = 9.75
    elif taxable_income <= 694.9:
        tax_rate = 0.20
        deduction = 42.75
    elif taxable_income <= 899.9:
        tax_rate = 0.23
        deduction = 63.6
    elif taxable_income <= 1799.9:
        tax_rate = 0.33
        deduction = 153.6
    elif taxable_income <= 3999.9:
        tax_rate = 0.40
        deduction = 279.6
    else:
        tax_rate = 0.45
        deduction = 479.6

    tax = taxable_income * tax_rate - deduction
    return max(0, tax)  # 課税所得0の場合も安全