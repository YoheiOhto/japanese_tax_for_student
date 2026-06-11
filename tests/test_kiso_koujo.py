import pytest

from src.kiso_koujo import kiso_kojo_chiho, kiso_kojo_kuni


@pytest.mark.parametrize(
    "income, year, expected",
    [
        # 2024年以前: 2,400万円以下は一律48万円
        (0, 2024, 48),
        (2400, 2024, 48),
        (2400.0001, 2024, 32),
        (2450, 2024, 32),
        (2450.0001, 2024, 16),
        (2500, 2024, 16),
        (2500.0001, 2024, 0),
        # 2025・2026年: 9段階テーブル
        (132, 2025, 95),
        (132.0001, 2025, 88),
        (336, 2025, 88),
        (336.0001, 2025, 68),
        (489, 2025, 68),
        (489.0001, 2025, 63),
        (655, 2025, 63),
        (655.0001, 2025, 58),
        (2350, 2025, 58),
        (2350.0001, 2025, 48),
        (132, 2026, 95),
        (336.0001, 2026, 68),
        # 2027年以降: 経過措置終了、132万円超〜2,350万円以下は一律58万円
        (132, 2027, 95),
        (132.0001, 2027, 58),
        (2350, 2027, 58),
        (2350.0001, 2027, 48),
    ],
)
def test_kiso_kojo_kuni(income, year, expected):
    assert kiso_kojo_kuni(income, year) == expected


@pytest.mark.parametrize(
    "income, expected",
    [
        (0, 43),
        (2400, 43),
        (2400.0001, 29),
        (2450, 29),
        (2450.0001, 15),
        (2500, 15),
        (2500.0001, 0),
    ],
)
def test_kiso_kojo_chiho(income, expected):
    assert kiso_kojo_chiho(income) == expected
