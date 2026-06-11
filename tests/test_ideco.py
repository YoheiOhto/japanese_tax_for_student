import pytest

from src.ideco import ideco_kojo


def test_ideco_kojo_basic():
    assert ideco_kojo(1.0, "自営業・フリーランス・学生（第1号被保険者）") == pytest.approx(12.0)


def test_ideco_kojo_capped_by_insured_type():
    # 会社員（DB等の他制度あり）または公務員: 上限1.2万円/月
    result = ideco_kojo(2.0, "会社員（DB等の他制度あり）または公務員")
    assert result == pytest.approx(1.2 * 12)


def test_ideco_kojo_zero():
    assert ideco_kojo(0.0) == 0.0


def test_ideco_kojo_negative_raises():
    with pytest.raises(ValueError):
        ideco_kojo(-1.0)


def test_ideco_kojo_unknown_insured_type_raises():
    with pytest.raises(ValueError):
        ideco_kojo(1.0, "unknown")
