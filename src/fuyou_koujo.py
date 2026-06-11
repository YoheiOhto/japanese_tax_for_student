from __future__ import annotations

from .config import (
    FUYOU_KOUJO_IPPAN_CHIHO,
    FUYOU_KOUJO_IPPAN_KUNI,
    FUYOU_KOUJO_TOKUTEI_CHIHO,
    FUYOU_KOUJO_TOKUTEI_KUNI,
    FUYOU_TAISHO_GOKEI_SHOTOKU_GENDO_NEW,
    FUYOU_TAISHO_GOKEI_SHOTOKU_GENDO_OLD,
)


def fuyou_taisho_hantei(gokei_shotoku: float, year: int, age: int) -> dict:
    """
    自分が「親などの控除対象扶養親族」に該当するかを判定する。

    自分自身の所得税・住民税には影響しないが、
    扶養している親（納税者）の控除額・税額に影響するため、
    「扶養から外れる収入ライン」を確認する目的で使用する。

    Parameters
    ----------
    gokei_shotoku : float
        自分の合計所得金額（万円）。
    year : int
        課税対象年。所得要件は令和7年度改正により
        2024年以前: 48万円以下 → 2025年以降: 58万円以下 に緩和された。
    age : int
        12月31日時点の年齢。19〜22歳は「特定扶養親族」として
        控除額が大きくなる。

    Returns
    -------
    dict
        - "扶養対象": 所得要件を満たすか（bool）
        - "所得要件（合計所得金額）": 適用される所得要件の閾値（万円）
        - "区分": "特定扶養親族" / "一般扶養親族" / "対象外"
        - "親が受けられる扶養控除額（所得税）"
        - "親が受けられる扶養控除額（住民税）"

    Notes
    -----
    - 控除対象扶養親族となるにはこの所得要件に加え、生計を一にしていること等の
      要件も必要（ここでは所得要件のみを判定）。
    - 16歳未満は扶養控除の対象外（児童手当の対象）のためこの関数の対象としない。

    出典: 国税庁「No.1180 扶養控除」
    https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1180.htm
    """
    gendo = (
        FUYOU_TAISHO_GOKEI_SHOTOKU_GENDO_OLD
        if year <= 2024
        else FUYOU_TAISHO_GOKEI_SHOTOKU_GENDO_NEW
    )

    if gokei_shotoku > gendo:
        return {
            "扶養対象": False,
            "所得要件（合計所得金額）": gendo,
            "区分": "対象外",
            "親が受けられる扶養控除額（所得税）": 0.0,
            "親が受けられる扶養控除額（住民税）": 0.0,
        }

    if 19 <= age <= 22:
        return {
            "扶養対象": True,
            "所得要件（合計所得金額）": gendo,
            "区分": "特定扶養親族",
            "親が受けられる扶養控除額（所得税）": FUYOU_KOUJO_TOKUTEI_KUNI,
            "親が受けられる扶養控除額（住民税）": FUYOU_KOUJO_TOKUTEI_CHIHO,
        }

    return {
        "扶養対象": True,
        "所得要件（合計所得金額）": gendo,
        "区分": "一般扶養親族",
        "親が受けられる扶養控除額（所得税）": FUYOU_KOUJO_IPPAN_KUNI,
        "親が受けられる扶養控除額（住民税）": FUYOU_KOUJO_IPPAN_CHIHO,
    }


def haigusha_koujo(my_gokei_shotoku: float, spouse_gokei_shotoku: float) -> dict:
    """
    配偶者控除・配偶者特別控除額を計算する（簡易版）。

    Parameters
    ----------
    my_gokei_shotoku : float
        納税者本人の合計所得金額（万円）。
    spouse_gokei_shotoku : float
        配偶者の合計所得金額（万円）。

    Returns
    -------
    dict
        所得税・住民税の控除額（万円）。

    Notes
    -----
    本関数は「納税者本人の合計所得金額が900万円以下」の場合のみを
    対象とした簡易版。900万円超では控除額が逓減・消失するが、
    本プロジェクトの想定ユーザー（学生・院生）では稀なケースのため未対応。

    出典: 国税庁「No.1191 配偶者控除」「No.1195 配偶者特別控除」
    https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1191.htm
    https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1195.htm
    """
    if my_gokei_shotoku > 900:
        return {
            "所得税": 0.0,
            "住民税": 0.0,
            "備考": "納税者本人の合計所得金額が900万円超のため未対応（要確認）。",
        }

    # 配偶者控除（配偶者の合計所得金額48万円以下）
    if spouse_gokei_shotoku <= 48:
        return {"所得税": 38.0, "住民税": 33.0, "備考": "配偶者控除"}

    # 配偶者特別控除（配偶者の合計所得金額48万円超133万円以下で逓減）
    # 簡易テーブル（本人所得900万円以下の場合）
    table = [
        (95, 38.0, 33.0),
        (100, 36.0, 33.0),
        (105, 31.0, 31.0),
        (110, 26.0, 26.0),
        (115, 21.0, 21.0),
        (120, 16.0, 16.0),
        (125, 11.0, 11.0),
        (130, 6.0, 6.0),
        (133, 3.0, 3.0),
    ]
    for gendo, kuni, chiho in table:
        if spouse_gokei_shotoku <= gendo:
            return {"所得税": kuni, "住民税": chiho, "備考": "配偶者特別控除"}

    return {"所得税": 0.0, "住民税": 0.0, "備考": "配偶者の所得が133万円を超えるため対象外"}
