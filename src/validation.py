from __future__ import annotations


def validate_inputs(
    salaries: list[float],
    zassyotoku_revenue: float,
    zassyotoku_expenses: float,
    ideco_getsu: float,
    ideco_max_getsu: float,
    iryouhi_shiharai: float,
    iryouhi_hoken_hoten: float,
    otc_shiharai: float,
    seimei_hoken_payments: list[float],
    jishin_hoken: float,
    furusato_kifu: float,
    num_persons: int,
    num_kaigo_persons: int,
) -> None:
    """
    `simulate_tax()` への入力値の妥当性を検証する。

    不正な値の場合は `ValueError` を送出する。
    """
    if not salaries:
        raise ValueError(
            "給与収入のリストが空です。収入が無い場合も [0.0] のように指定してください。"
        )
    if any(s < 0 for s in salaries):
        raise ValueError("給与収入は0以上で指定してください。")

    if zassyotoku_revenue < 0 or zassyotoku_expenses < 0:
        raise ValueError("雑所得の収入・必要経費は0以上で指定してください。")
    if zassyotoku_expenses > zassyotoku_revenue:
        raise ValueError("雑所得の必要経費が収入を超えています。")

    if ideco_getsu < 0:
        raise ValueError("iDeCoの月額掛金は0以上で指定してください。")
    if ideco_getsu > ideco_max_getsu:
        raise ValueError(
            f"iDeCoの月額掛金が被保険者区分の上限（{ideco_max_getsu}万円/月）を超えています。"
        )

    if iryouhi_shiharai < 0 or iryouhi_hoken_hoten < 0:
        raise ValueError("医療費の支払額・保険金等補填額は0以上で指定してください。")
    if iryouhi_hoken_hoten > iryouhi_shiharai:
        raise ValueError("医療費の保険金等補填額が支払額を超えています。")
    if otc_shiharai < 0:
        raise ValueError("OTC医薬品の購入額は0以上で指定してください。")

    if any(p < 0 for p in seimei_hoken_payments):
        raise ValueError("生命保険料の支払額は0以上で指定してください。")
    if jishin_hoken < 0:
        raise ValueError("地震保険料の支払額は0以上で指定してください。")
    if furusato_kifu < 0:
        raise ValueError("ふるさと納税の寄附額は0以上で指定してください。")

    if num_persons < 1:
        raise ValueError("num_persons（世帯人数）は1以上で指定してください。")
    if num_kaigo_persons < 0 or num_kaigo_persons > num_persons:
        raise ValueError("num_kaigo_persons は0以上 num_persons以下で指定してください。")
