import pytest

from src.kyuyosyotoku_koujo import kyuyo_syotoku_kojo


@pytest.mark.parametrize(
    "income, year, expected",
    [
        # 2024年以前: 最低保障額55万円
        (100, 2024, 55),
        (162.5, 2024, 55),
        (180, 2024, 180 * 0.40 - 10),  # 62
        (360, 2024, 360 * 0.30 + 8),  # 116
        (660, 2024, 660 * 0.20 + 44),  # 176
        (850, 2024, 850 * 0.10 + 110),  # 195
        (900, 2024, 195),  # 850万円超は一律195万円
        # 2025年以降: 最低保障額65万円
        (100, 2025, 65),
        (162.5, 2025, 65),
        (180, 2025, max(65, 180 * 0.40 - 10)),  # 65（最低保障額が上回る）
        (360, 2025, 360 * 0.30 + 8),  # 116
        (660, 2025, 660 * 0.20 + 44),  # 176
        (850, 2025, 850 * 0.10 + 110),  # 195
        (900, 2025, 195),
    ],
)
def test_kyuyo_syotoku_kojo(income, year, expected):
    assert kyuyo_syotoku_kojo(income, year) == pytest.approx(expected, abs=1e-6)
