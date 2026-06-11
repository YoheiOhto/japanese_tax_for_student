import pytest

from src.kifukin_koujo import furusato_nouzei_koujo


def test_no_donation():
    result = furusato_nouzei_koujo(kifu_gaku=0, kazei_shotoku_kuni=300, juminzei_shotokuwari_mae=20)
    assert result["控除合計"] == 0.0
    assert result["自己負担額"] == 0.0


def test_donation_within_limit():
    # 課税所得300万円 -> 限界税率10%
    # 自己負担を除いた額 = 4 - 0.2 = 3.8
    result = furusato_nouzei_koujo(kifu_gaku=4, kazei_shotoku_kuni=300, juminzei_shotokuwari_mae=20)
    base = 4 - 0.2
    assert result["所得税控除額"] == pytest.approx(base * 0.10, abs=1e-4)
    assert result["住民税控除額（基本分）"] == pytest.approx(base * 0.10, abs=1e-4)
    # 特例分上限 = 住民税所得割額20% = 4
    assert result["住民税控除額（特例分）"] == pytest.approx(base * (0.90 - 0.10), abs=1e-4)
    assert result["自己負担額"] == 0.2


def test_donation_special_portion_capped_by_juminzei_gendo():
    # 住民税所得割額が小さく、特例分の上限（20%）に張り付くケース
    result = furusato_nouzei_koujo(kifu_gaku=10, kazei_shotoku_kuni=300, juminzei_shotokuwari_mae=2)
    gendo = 2 * 0.20
    assert result["住民税控除額（特例分）"] == pytest.approx(gendo, abs=1e-4)


def test_donation_with_fukkou():
    base = furusato_nouzei_koujo(kifu_gaku=4, kazei_shotoku_kuni=300, juminzei_shotokuwari_mae=20, include_fukkou=False)
    with_fukkou = furusato_nouzei_koujo(kifu_gaku=4, kazei_shotoku_kuni=300, juminzei_shotokuwari_mae=20, include_fukkou=True)
    # 復興税込みの方が所得税控除額がわずかに大きく、住民税特例分はわずかに小さくなる
    assert with_fukkou["所得税控除額"] > base["所得税控除額"]
    assert with_fukkou["住民税控除額（特例分）"] < base["住民税控除額（特例分）"]
