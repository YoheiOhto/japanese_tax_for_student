from __future__ import annotations

from .config import (
    IRYOUHI_KOUJO_GENDO,
    IRYOUHI_KOUJO_TEIGAKU,
    IRYOUHI_KOUJO_WARIAI,
    SELF_MEDICATION_GENDO,
    SELF_MEDICATION_SHIKIRI,
)


def iryouhi_koujo(
    shiharai_gaku: float,
    hoken_hoten_gaku: float,
    gokei_shotoku: float,
) -> float:
    """
    医療費控除額（万円）を計算する。

    Parameters
    ----------
    shiharai_gaku : float
        年間に支払った医療費の総額（万円）。
    hoken_hoten_gaku : float
        生命保険の入院給付金・健康保険の高額療養費・出産育児一時金など、
        医療費を補填する目的で支給される金額（万円）。
    gokei_shotoku : float
        合計所得金額（万円）。足切り額の算定に使用する。

    Returns
    -------
    float
        医療費控除額（万円）。上限200万円。

    計算式
    ------
    控除額 = 支払医療費 − 保険金等補填額 − 足切り額
    足切り額 = min(10万円, 合計所得金額 × 5%)

    出典: 国税庁「No.1120 医療費を支払ったとき（医療費控除）」
    https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1120.htm
    """
    soko = max(0.0, shiharai_gaku - hoken_hoten_gaku)
    shikiri = min(IRYOUHI_KOUJO_TEIGAKU, gokei_shotoku * IRYOUHI_KOUJO_WARIAI)
    return min(IRYOUHI_KOUJO_GENDO, max(0.0, soko - shikiri))


def self_medication_koujo(otc_shiharai_gaku: float) -> float:
    """
    セルフメディケーション税制による控除額（万円）を計算する。

    Parameters
    ----------
    otc_shiharai_gaku : float
        健康の維持増進・疾病予防の取組として支払った
        特定一般用医薬品等（OTC医薬品）の購入額（万円）。

    Returns
    -------
    float
        控除額（万円）。

    計算式
    ------
    控除額 = min(支払額 − 1.2万円, 8.8万円)

    Notes
    -----
    通常の医療費控除との併用は不可（いずれか有利な方を選択）。
    適用には健康診断・予防接種等の「一定の取組」を行っていることが要件。

    出典: 国税庁「No.1131 セルフメディケーション税制の概要」
    https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1131.htm
    """
    return min(max(0.0, otc_shiharai_gaku - SELF_MEDICATION_SHIKIRI), SELF_MEDICATION_GENDO)


def select_iryouhi_koujo(
    shiharai_gaku: float,
    hoken_hoten_gaku: float,
    otc_shiharai_gaku: float,
    gokei_shotoku: float,
) -> dict:
    """
    通常の医療費控除とセルフメディケーション税制を両方計算し、
    有利な方（控除額が大きい方）を選択する。

    Returns
    -------
    dict
        - "通常の医療費控除": 控除額（万円）
        - "セルフメディケーション税制": 控除額（万円）
        - "採用": どちらを採用したか（"通常の医療費控除" / "セルフメディケーション税制" / "なし"）
        - "控除額": 採用した控除額（万円）
    """
    futsu = iryouhi_koujo(shiharai_gaku, hoken_hoten_gaku, gokei_shotoku)
    self_med = self_medication_koujo(otc_shiharai_gaku)

    if futsu <= 0.0 and self_med <= 0.0:
        adopted, amount = "なし", 0.0
    elif futsu >= self_med:
        adopted, amount = "通常の医療費控除", futsu
    else:
        adopted, amount = "セルフメディケーション税制", self_med

    return {
        "通常の医療費控除": round(futsu, 4),
        "セルフメディケーション税制": round(self_med, 4),
        "採用": adopted,
        "控除額": round(amount, 4),
    }
