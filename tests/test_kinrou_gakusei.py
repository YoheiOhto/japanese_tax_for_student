from src.kinrou_gakusei import kinrou_gakusei_koujo


def test_not_a_student():
    result = kinrou_gakusei_koujo(is_student=False, gokei_shotoku=50, kyuyo_shotoku=50)
    assert result["適用"] is False
    assert result["控除額（所得税）"] == 0.0
    assert result["控除額（住民税）"] == 0.0


def test_eligible_student_within_limits():
    result = kinrou_gakusei_koujo(is_student=True, gokei_shotoku=85, kyuyo_shotoku=85)
    assert result["適用"] is True
    assert result["控除額（所得税）"] == 27.0
    assert result["控除額（住民税）"] == 26.0


def test_student_over_income_limit():
    # 合計所得金額が85万円を超えると不適用
    result = kinrou_gakusei_koujo(is_student=True, gokei_shotoku=85.0001, kyuyo_shotoku=85.0001)
    assert result["適用"] is False
    assert result["控除額（所得税）"] == 0.0


def test_student_over_other_income_limit():
    # 給与所得等以外の所得（雑所得など）が10万円を超えると不適用
    result = kinrou_gakusei_koujo(is_student=True, gokei_shotoku=85, kyuyo_shotoku=70)
    assert result["適用"] is False
    assert "万円を超えている" in result["判定理由"]


def test_student_at_other_income_boundary():
    # 給与所得等以外の所得がちょうど10万円なら適用
    result = kinrou_gakusei_koujo(is_student=True, gokei_shotoku=85, kyuyo_shotoku=75)
    assert result["適用"] is True
