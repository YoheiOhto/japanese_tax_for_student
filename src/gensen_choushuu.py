from __future__ import annotations

from .config import GENSEN_OTSURAN_RATE


def gensen_choushuu_gaku(salaries: list[float], main_index: int = 0) -> dict:
    """
    給与収入に対する源泉徴収税額を概算する。

    Parameters
    ----------
    salaries : list[float]
        給与収入のリスト（万円）。
    main_index : int
        メインの勤務先（年末調整を受ける「甲欄」適用先）のインデックス。

    Returns
    -------
    dict
        - "内訳": 各給与の源泉徴収額・適用区分のリスト
        - "合計": 源泉徴収額の合計（万円）

    Notes
    -----
    簡易シミュレーションのための近似であり、実際の源泉徴収税額表とは異なる。

    - `main_index` で指定した給与は「甲欄」（扶養控除等申告書を提出）が
      適用され、年末調整によって年間の所得税額とほぼ一致する
      （＝この給与単独に起因する還付・追納は発生しない）ものとして
      源泉徴収額を 0 として扱う。
    - それ以外（掛け持ちの2社目以降）は「乙欄」が適用され、年末調整は
      行われず、給与収入額に対して一律 3.063%
      （所得税 + 復興特別所得税）が源泉徴収されるものとする。

    実際には甲欄適用先でも年の途中での収入変動により過不足が生じるが、
    本シミュレーターでは「乙欄適用分の源泉徴収税額が、確定申告によって
    精算（還付）される」という最も典型的なケースに絞って概算する。

    出典: 国税庁「給与所得の源泉徴収税額表」（月額表）乙欄
    https://www.nta.go.jp/publication/pamph/gensen/zeigaku2024/index.htm
    """
    if not salaries:
        raise ValueError("給与収入のリストが空です。")
    if not (0 <= main_index < len(salaries)):
        raise ValueError("main_index が salaries の範囲外です。")

    breakdown = []
    total = 0.0
    for i, s in enumerate(salaries):
        if i == main_index:
            gensen = 0.0
            kubun = "甲欄（年末調整済み想定）"
        else:
            gensen = round(s * GENSEN_OTSURAN_RATE, 4)
            kubun = "乙欄（一律3.063%）"
        breakdown.append({"給与収入": s, "区分": kubun, "源泉徴収額": gensen})
        total += gensen

    return {"内訳": breakdown, "合計": round(total, 4)}


def kanpu_tsuino_gaku(gensen_choushuu_total: float, sanshutsu_zeigaku: float) -> dict:
    """
    確定申告による所得税の還付額・追納額を計算する。

    Parameters
    ----------
    gensen_choushuu_total : float
        源泉徴収税額の合計（万円）。`gensen_choushuu_gaku()` の "合計"。
    sanshutsu_zeigaku : float
        `simulate_tax()` で計算した所得税の算出税額（万円）。

    Returns
    -------
    dict
        - "源泉徴収額合計": 万円
        - "算出所得税額": 万円
        - "還付額": 還付される場合の金額（万円。無ければ0）
        - "追納額": 追加で納税が必要な場合の金額（万円。無ければ0）
    """
    sa = gensen_choushuu_total - sanshutsu_zeigaku
    return {
        "源泉徴収額合計": round(gensen_choushuu_total, 4),
        "算出所得税額": round(sanshutsu_zeigaku, 4),
        "還付額": round(max(0.0, sa), 4),
        "追納額": round(max(0.0, -sa), 4),
    }
