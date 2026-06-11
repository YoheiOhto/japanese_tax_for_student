import pytest

from src.hoken_koujo import jishin_hoken_koujo, seimei_hoken_koujo


@pytest.mark.parametrize(
    "shiharai, expected_kuni, expected_chiho",
    [
        (0, 0.0, 0.0),
        (2, 2.0, 2.0),  # 所得税: 2万円以下は全額、住民税: 2万円超1.2万超なので 2/2+0.6=1.6
        (8, 4.0, 2.8),  # 所得税: 8万円超で一律4万円・住民税: 5.6万円超で一律2.8万円
        (1.2, 1.2, 1.2),  # 住民税: 1.2万円以下は全額
    ],
)
def test_seimei_hoken_single_kubun(shiharai, expected_kuni, expected_chiho):
    result = seimei_hoken_koujo(ippan_shiharai=shiharai)
    assert result["所得税"] == pytest.approx(expected_kuni, abs=1e-4)
    if shiharai == 2:
        # 住民税: 2万円は 1.2 < 2 <= 3.2 -> shiharai/2 + 0.6 = 1.6
        assert result["住民税"] == pytest.approx(1.6, abs=1e-4)
    else:
        assert result["住民税"] == pytest.approx(expected_chiho, abs=1e-4)


def test_seimei_hoken_total_capped():
    # 3区分すべて上限超過 -> 所得税12万円・住民税7万円が上限
    result = seimei_hoken_koujo(ippan_shiharai=10, kaigo_iryou_shiharai=10, kojin_nenkin_shiharai=10)
    assert result["所得税"] == 12.0
    assert result["住民税"] == 7.0


def test_jishin_hoken_koujo():
    assert jishin_hoken_koujo(0) == {"所得税": 0.0, "住民税": 0.0}
    assert jishin_hoken_koujo(3) == {"所得税": 3.0, "住民税": 1.5}
    # 所得税は5万円、住民税は2.5万円が上限
    result = jishin_hoken_koujo(10)
    assert result["所得税"] == 5.0
    assert result["住民税"] == 2.5
