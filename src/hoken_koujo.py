from __future__ import annotations

from .config import (
    JISHIN_HOKEN_CHIHO_GENDO,
    JISHIN_HOKEN_KUNI_GENDO,
    SEIMEI_HOKEN_CHIHO_GENDO_GOKEI,
    SEIMEI_HOKEN_CHIHO_GENDO_PER_KUBUN,
    SEIMEI_HOKEN_KUNI_GENDO_GOKEI,
    SEIMEI_HOKEN_KUNI_GENDO_PER_KUBUN,
)


def _seimei_hoken_kojo_kubun(shiharai: float) -> tuple[float, float]:
    """
    生命保険料控除（新制度・2012年以降契約）の1区分あたりの控除額を計算する。

    Returns
    -------
    (所得税控除額, 住民税控除額) （いずれも万円）
    """
    if shiharai <= 0:
        return 0.0, 0.0

    # 所得税
    if shiharai <= 2:
        kuni = shiharai
    elif shiharai <= 4:
        kuni = shiharai / 2 + 1
    elif shiharai <= 8:
        kuni = shiharai / 4 + 2
    else:
        kuni = SEIMEI_HOKEN_KUNI_GENDO_PER_KUBUN

    # 住民税
    if shiharai <= 1.2:
        chiho = shiharai
    elif shiharai <= 3.2:
        chiho = shiharai / 2 + 0.6
    elif shiharai <= 5.6:
        chiho = shiharai / 4 + 1.4
    else:
        chiho = SEIMEI_HOKEN_CHIHO_GENDO_PER_KUBUN

    return kuni, chiho


def seimei_hoken_koujo(
    ippan_shiharai: float = 0.0,
    kaigo_iryou_shiharai: float = 0.0,
    kojin_nenkin_shiharai: float = 0.0,
) -> dict:
    """
    生命保険料控除額（新制度・2012年以降契約）を計算する。

    Parameters
    ----------
    ippan_shiharai : float
        一般生命保険料の年間支払額（万円）。
    kaigo_iryou_shiharai : float
        介護医療保険料の年間支払額（万円）。
    kojin_nenkin_shiharai : float
        個人年金保険料の年間支払額（万円）。

    Returns
    -------
    dict
        所得税・住民税それぞれの控除額（万円）。

    Notes
    -----
    各区分の控除額は以下の式で計算する（新制度）。

    所得税:
        支払額 ≤ 2万円      → 全額
        2万円 < 支払額 ≤ 4万円 → 支払額 × 1/2 + 1万円
        4万円 < 支払額 ≤ 8万円 → 支払額 × 1/4 + 2万円
        8万円超             → 一律4万円

    住民税:
        支払額 ≤ 1.2万円     → 全額
        1.2万円 < 支払額 ≤ 3.2万円 → 支払額 × 1/2 + 0.6万円
        3.2万円 < 支払額 ≤ 5.6万円 → 支払額 × 1/4 + 1.4万円
        5.6万円超            → 一律2.8万円

    3区分の合計に対し、所得税は12万円、住民税は7万円を上限とする。
    2011年以前契約の「旧制度」には対応していない。

    出典: 国税庁「No.1140 生命保険料控除」
    https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1140.htm
    """
    kuni_total = chiho_total = 0.0
    for shiharai in (ippan_shiharai, kaigo_iryou_shiharai, kojin_nenkin_shiharai):
        kuni, chiho = _seimei_hoken_kojo_kubun(shiharai)
        kuni_total += kuni
        chiho_total += chiho

    return {
        "所得税": round(min(kuni_total, SEIMEI_HOKEN_KUNI_GENDO_GOKEI), 4),
        "住民税": round(min(chiho_total, SEIMEI_HOKEN_CHIHO_GENDO_GOKEI), 4),
    }


def jishin_hoken_koujo(shiharai: float) -> dict:
    """
    地震保険料控除額を計算する。

    Parameters
    ----------
    shiharai : float
        年間の地震保険料支払額（万円）。

    Returns
    -------
    dict
        所得税・住民税それぞれの控除額（万円）。

    計算式
    ------
    所得税: min(支払額, 5万円)
    住民税: min(支払額 × 1/2, 2.5万円)

    出典: 国税庁「No.1145 地震保険料控除」
    https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1145.htm
    """
    if shiharai <= 0:
        return {"所得税": 0.0, "住民税": 0.0}

    return {
        "所得税": round(min(shiharai, JISHIN_HOKEN_KUNI_GENDO), 4),
        "住民税": round(min(shiharai / 2, JISHIN_HOKEN_CHIHO_GENDO), 4),
    }
