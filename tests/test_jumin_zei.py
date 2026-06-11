import pytest

from src.jumin_zei import tyosei_koujo


def test_tyosei_koujo_under_200man():
    # 課税所得 ≤ 200万円: min(差額, 課税所得) × 5%
    # 所得税基礎控除95万 - 住民税基礎控除43万 = 差額52万
    # 課税所得100万 < 差額52万 -> min(52, 100) * 0.05 = 2.6
    assert tyosei_koujo(100, kokuzei_kiso_kojo=95, chihouzei_kiso_kojo=43) == pytest.approx(2.6)


def test_tyosei_koujo_at_200man_boundary():
    # 課税所得ちょうど200万円も「以下」の式が適用される
    assert tyosei_koujo(200, kokuzei_kiso_kojo=95, chihouzei_kiso_kojo=43) == pytest.approx(
        min(52, 200) * 0.05
    )


def test_tyosei_koujo_over_200man():
    # 課税所得 > 200万円: max(差額 - (課税所得 - 200), 0) * 5%
    # 差額52万、課税所得300万 -> max(52 - 100, 0) * 0.05 = 0
    assert tyosei_koujo(300, kokuzei_kiso_kojo=95, chihouzei_kiso_kojo=43) == pytest.approx(0.0)


def test_tyosei_koujo_over_200man_partial():
    # 差額52万、課税所得240万 -> max(52 - 40, 0) * 0.05 = 0.6
    assert tyosei_koujo(240, kokuzei_kiso_kojo=95, chihouzei_kiso_kojo=43) == pytest.approx(0.6)


def test_tyosei_koujo_no_diff_when_kiso_kojo_equal():
    # 2024年以前は所得税・住民税の基礎控除がともに48万/43万で固定差5万
    assert tyosei_koujo(100, kokuzei_kiso_kojo=48, chihouzei_kiso_kojo=43) == pytest.approx(
        min(5, 100) * 0.05
    )
