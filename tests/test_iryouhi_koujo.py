import pytest

from src.iryouhi_koujo import iryouhi_koujo, select_iryouhi_koujo, self_medication_koujo


def test_iryouhi_koujo_basic():
    # 支払額30万、保険補填5万、合計所得300万 -> 足切り10万（所得の5%=15万との小さい方）
    # 控除額 = (30 - 5) - 10 = 15
    assert iryouhi_koujo(30, 5, 300) == pytest.approx(15)


def test_iryouhi_koujo_low_income_uses_5percent_floor():
    # 合計所得100万円なら足切り額は min(10, 100*0.05=5) = 5
    # 控除額 = (20 - 0) - 5 = 15
    assert iryouhi_koujo(20, 0, 100) == pytest.approx(15)


def test_iryouhi_koujo_below_floor_is_zero():
    assert iryouhi_koujo(5, 0, 300) == 0.0


def test_iryouhi_koujo_capped_at_200man():
    assert iryouhi_koujo(300, 0, 1000) == 200.0


def test_self_medication_koujo():
    # 控除額 = min(支払額 - 1.2, 8.8)
    assert self_medication_koujo(5) == pytest.approx(5 - 1.2)
    assert self_medication_koujo(1.0) == 0.0  # 1.2万円以下は0
    assert self_medication_koujo(20) == 8.8  # 上限


def test_select_iryouhi_koujo_chooses_larger():
    # 通常の医療費控除の方が大きい場合
    result = select_iryouhi_koujo(
        shiharai_gaku=30, hoken_hoten_gaku=0, otc_shiharai_gaku=2, gokei_shotoku=300
    )
    assert result["採用"] == "通常の医療費控除"
    assert result["控除額"] == result["通常の医療費控除"]


def test_select_iryouhi_koujo_self_medication():
    result = select_iryouhi_koujo(
        shiharai_gaku=0, hoken_hoten_gaku=0, otc_shiharai_gaku=5, gokei_shotoku=300
    )
    assert result["採用"] == "セルフメディケーション税制"
    assert result["控除額"] == pytest.approx(5 - 1.2)


def test_select_iryouhi_koujo_neither():
    result = select_iryouhi_koujo(
        shiharai_gaku=0, hoken_hoten_gaku=0, otc_shiharai_gaku=0, gokei_shotoku=300
    )
    assert result["採用"] == "なし"
    assert result["控除額"] == 0.0
