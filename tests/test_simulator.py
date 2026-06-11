import pytest

from src.simulator import SimulationInput, compare_tax_by_year, simulate_tax


def test_working_student_pays_no_income_or_resident_tax():
    # 給与収入96万円・学生・20歳・2026年
    # 給与所得控除65万 -> 給与所得31万、勤労学生控除27万/26万、基礎控除95万/43万
    # いずれも課税所得が0以下になり、所得税・住民税ともに0円となるはず
    inp = SimulationInput(salaries=[96.0], is_student=True, age=20, year=2026)
    result = simulate_tax(inp)

    assert result["所得税額"] == 0.0
    assert result["住民税額（所得割）"] == 0.0
    assert result["勤労学生控除"]["適用"] is True
    assert result["勤労学生控除"]["控除額（所得税）"] == 27.0
    assert result["勤労学生控除"]["控除額（住民税）"] == 26.0


def test_fuyou_taisho_for_low_income_student():
    inp = SimulationInput(salaries=[96.0], is_student=True, age=20, year=2026)
    result = simulate_tax(inp)

    fuyou = result["扶養判定"]
    assert fuyou["扶養対象"] is True
    assert fuyou["区分"] == "特定扶養親族"


def test_scholarship_kyufugata_is_excluded_from_taxable_income():
    base = SimulationInput(salaries=[100.0], year=2025)
    with_scholarship = SimulationInput(salaries=[100.0], year=2025, scholarship_kyufugata=50.0)

    base_result = simulate_tax(base)
    scholarship_result = simulate_tax(with_scholarship)

    # 給付型奨学金は非課税のため、合計所得金額・税額には影響しない
    assert scholarship_result["合計所得金額"] == pytest.approx(base_result["合計所得金額"])
    assert scholarship_result["所得税額"] == pytest.approx(base_result["所得税額"])

    # ただし手取り（サマリーの総収入・手取り収入）には反映される
    assert scholarship_result["サマリー"]["総収入（非課税収入含む）"] == pytest.approx(
        base_result["サマリー"]["総収入（非課税収入含む）"] + 50.0
    )


def test_furusato_donation_reduces_total_tax():
    base = SimulationInput(salaries=[400.0], year=2025)
    with_donation = SimulationInput(salaries=[400.0], year=2025, furusato_kifu=4.0)

    base_result = simulate_tax(base)
    donation_result = simulate_tax(with_donation)

    assert donation_result["合計納税額"] < base_result["合計納税額"]

    furusato = donation_result["ふるさと納税控除"]
    assert furusato["控除合計"] > 0
    assert furusato["自己負担額"] == pytest.approx(0.2)


def test_compare_tax_by_year_returns_all_years():
    inp = SimulationInput(salaries=[200.0])
    results = compare_tax_by_year(inp, years=[2024, 2025, 2026, 2027])

    assert set(results.keys()) == {2024, 2025, 2026, 2027}
    for year, result in results.items():
        assert result["対象年"] == year
        assert "サマリー" in result


def test_validation_rejects_negative_salary():
    with pytest.raises(ValueError):
        simulate_tax(SimulationInput(salaries=[-1.0]))
