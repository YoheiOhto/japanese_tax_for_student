import pytest

from src.income_tax import calculate_income_tax


@pytest.mark.parametrize(
    "taxable_income, expected",
    [
        (0, 0.0),
        (100, 100 * 0.05),
        (195, 195 * 0.05 - 0.0),  # 5%ブラケット上限
        (195.0001, 195.0001 * 0.10 - 9.75),  # 10%ブラケット下限超
        (330, 330 * 0.10 - 9.75),  # 10%ブラケット上限
        (330.0001, 330.0001 * 0.20 - 42.75),  # 20%ブラケット下限超
        (695, 695 * 0.20 - 42.75),  # 20%ブラケット上限
        (695.0001, 695.0001 * 0.23 - 63.60),  # 23%ブラケット下限超
        (900, 900 * 0.23 - 63.60),  # 23%ブラケット上限
        (900.0001, 900.0001 * 0.33 - 153.60),  # 33%ブラケット下限超
        (1800, 1800 * 0.33 - 153.60),  # 33%ブラケット上限
        (1800.0001, 1800.0001 * 0.40 - 279.60),  # 40%ブラケット下限超
        (4000, 4000 * 0.40 - 279.60),  # 40%ブラケット上限
        (4000.0001, 4000.0001 * 0.45 - 479.60),  # 45%ブラケット下限超
    ],
)
def test_income_tax_brackets(taxable_income, expected):
    assert calculate_income_tax(taxable_income) == pytest.approx(expected, abs=1e-6)


def test_income_tax_with_fukkou():
    base = calculate_income_tax(330)
    with_fukkou = calculate_income_tax(330, include_fukkou=True)
    assert with_fukkou == pytest.approx(base * 1.021, abs=1e-6)


def test_income_tax_negative_taxable_income_is_zero():
    # 課税所得がマイナス（控除超過）の場合は0円
    assert calculate_income_tax(-10) == 0.0
