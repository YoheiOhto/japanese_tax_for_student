import pytest

from src.fuyou_koujo import fuyou_taisho_hantei, haigusha_koujo


def test_fuyou_taisho_old_rule_boundary():
    # 2024年以前: 所得要件48万円以下
    assert fuyou_taisho_hantei(48, year=2024, age=22)["扶養対象"] is True
    assert fuyou_taisho_hantei(48.0001, year=2024, age=22)["扶養対象"] is False


def test_fuyou_taisho_new_rule_boundary():
    # 2025年以降: 所得要件58万円以下
    assert fuyou_taisho_hantei(58, year=2025, age=22)["扶養対象"] is True
    assert fuyou_taisho_hantei(58.0001, year=2025, age=22)["扶養対象"] is False


@pytest.mark.parametrize("age", [19, 22])
def test_fuyou_taisho_tokutei_fuyou(age):
    result = fuyou_taisho_hantei(50, year=2025, age=age)
    assert result["区分"] == "特定扶養親族"
    assert result["親が受けられる扶養控除額（所得税）"] == 63
    assert result["親が受けられる扶養控除額（住民税）"] == 45


@pytest.mark.parametrize("age", [18, 23])
def test_fuyou_taisho_ippan_fuyou(age):
    result = fuyou_taisho_hantei(50, year=2025, age=age)
    assert result["区分"] == "一般扶養親族"
    assert result["親が受けられる扶養控除額（所得税）"] == 38
    assert result["親が受けられる扶養控除額（住民税）"] == 33


def test_haigusha_koujo_full_deduction():
    # 配偶者の合計所得48万円以下 -> 配偶者控除（38万/33万）
    result = haigusha_koujo(my_gokei_shotoku=300, spouse_gokei_shotoku=48)
    assert result["所得税"] == 38.0
    assert result["住民税"] == 33.0
    assert result["備考"] == "配偶者控除"


def test_haigusha_koujo_special_deduction_phaseout():
    # 配偶者所得95万円以下は配偶者特別控除でも38万/33万を維持
    result = haigusha_koujo(my_gokei_shotoku=300, spouse_gokei_shotoku=95)
    assert result["所得税"] == 38.0
    assert result["備考"] == "配偶者特別控除"

    # 130万円超133万円以下は3万円
    result = haigusha_koujo(my_gokei_shotoku=300, spouse_gokei_shotoku=133)
    assert result["所得税"] == 3.0


def test_haigusha_koujo_over_133man():
    result = haigusha_koujo(my_gokei_shotoku=300, spouse_gokei_shotoku=133.0001)
    assert result["所得税"] == 0.0
    assert result["住民税"] == 0.0


def test_haigusha_koujo_my_income_too_high():
    result = haigusha_koujo(my_gokei_shotoku=900.0001, spouse_gokei_shotoku=0)
    assert result["所得税"] == 0.0
    assert result["住民税"] == 0.0
