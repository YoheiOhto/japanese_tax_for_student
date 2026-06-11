from __future__ import annotations

from .config import (
    KINROU_GAKUSEI_GOKEI_SHOTOKU_GENDO,
    KINROU_GAKUSEI_KOUJO_CHIHO,
    KINROU_GAKUSEI_KOUJO_KUNI,
    KINROU_GAKUSEI_SONOTA_SHOTOKU_GENDO,
)


def kinrou_gakusei_koujo(
    is_student: bool,
    gokei_shotoku: float,
    kyuyo_shotoku: float,
) -> dict:
    """
    勤労学生控除の判定と控除額を計算する。

    Parameters
    ----------
    is_student : bool
        学校教育法に規定する学校（大学・大学院・専門学校等）の
        学生・生徒・児童であるかどうか。
    gokei_shotoku : float
        合計所得金額（万円）。
    kyuyo_shotoku : float
        給与所得の金額（万円）。合計所得金額のうち
        「給与所得等以外の所得」を判定するために使用する。

    Returns
    -------
    dict
        - "適用": 適用可否（bool）
        - "控除額（所得税）": 適用時27万円、非適用時0
        - "控除額（住民税）": 適用時26万円、非適用時0
        - "判定理由": 非適用の場合の理由（適用時は空文字）

    適用要件（すべて満たす場合に適用）
    --------------------------------
    1. 学校教育法に規定する学校等の学生・生徒であること
    2. 合計所得金額が85万円以下であること
    3. 給与所得等以外の所得（雑所得など）が10万円以下であること

    出典: 国税庁「No.1175 勤労学生控除」
    https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1175.htm
    """
    sonota_shotoku = max(0.0, gokei_shotoku - kyuyo_shotoku)

    if not is_student:
        return _result(False, "学生に該当しない")
    if gokei_shotoku > KINROU_GAKUSEI_GOKEI_SHOTOKU_GENDO:
        return _result(
            False,
            f"合計所得金額が{KINROU_GAKUSEI_GOKEI_SHOTOKU_GENDO}万円を超えている",
        )
    if sonota_shotoku > KINROU_GAKUSEI_SONOTA_SHOTOKU_GENDO:
        return _result(
            False,
            f"給与所得等以外の所得が{KINROU_GAKUSEI_SONOTA_SHOTOKU_GENDO}万円を超えている",
        )
    return _result(True, "")


def _result(eligible: bool, reason: str) -> dict:
    return {
        "適用": eligible,
        "控除額（所得税）": KINROU_GAKUSEI_KOUJO_KUNI if eligible else 0.0,
        "控除額（住民税）": KINROU_GAKUSEI_KOUJO_CHIHO if eligible else 0.0,
        "判定理由": reason,
    }
