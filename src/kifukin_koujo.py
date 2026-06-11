from __future__ import annotations

from .config import FUKKOU_RATE, marginal_income_tax_rate


def furusato_nouzei_koujo(
    kifu_gaku: float,
    kazei_shotoku_kuni: float,
    juminzei_shotokuwari_mae: float,
    include_fukkou: bool = False,
) -> dict:
    """
    ふるさと納税（確定申告でワンストップ特例を使わない場合）の
    控除額を概算する。

    Parameters
    ----------
    kifu_gaku : float
        ふるさと納税（自治体への寄附金）の年間合計額（万円）。
    kazei_shotoku_kuni : float
        所得税の課税所得（万円）。寄附金控除を適用する**前**の値を渡す。
        所得税の限界税率の判定に使用する。
    juminzei_shotokuwari_mae : float
        住民税所得割額（調整控除後・寄附金控除適用前、万円）。
        住民税特例分の上限（所得割額の20%）の算定に使用する。
    include_fukkou : bool
        True = 復興特別所得税を所得税の限界税率に加味する。

    Returns
    -------
    dict
        - "所得税控除額": 所得税からの控除額（寄附金控除、万円）
        - "住民税控除額（基本分）": 住民税の寄附金税額控除（基本分、万円）
        - "住民税控除額（特例分）": 住民税の寄附金税額控除（特例分、万円）
        - "控除合計": 上記3つの合計（万円）
        - "自己負担額": 2,000円（0.2万円）

    計算式（ワンストップ特例を使わない場合）
    ----------------------------------------
    自己負担を除いた額 = 寄附金額 − 2,000円
    所得税控除額       = 自己負担を除いた額 × 所得税の限界税率
    住民税控除額(基本分) = 自己負担を除いた額 × 10%
    住民税控除額(特例分) = 自己負担を除いた額 × (90% − 所得税の限界税率)
                         ただし住民税所得割額の20%が上限

    上記の上限の範囲内であれば、自己負担2,000円を除く全額が控除される。

    出典: 総務省「ふるさと納税のしくみ」控除額の計算
    https://www.soumu.go.jp/main_sosiki/jichi_zeisei/czaisei/czaisei_seido/furusato/mechanism/deduction.html
    """
    JIKO_FUTAN = 0.2  # 2,000円

    if kifu_gaku <= 0:
        return {
            "所得税控除額": 0.0,
            "住民税控除額（基本分）": 0.0,
            "住民税控除額（特例分）": 0.0,
            "控除合計": 0.0,
            "自己負担額": 0.0,
        }

    base = max(0.0, kifu_gaku - JIKO_FUTAN)

    rate = marginal_income_tax_rate(kazei_shotoku_kuni)
    if include_fukkou:
        rate *= 1 + FUKKOU_RATE

    shotoku_zei = base * rate
    juminzei_kihon = base * 0.10
    juminzei_tokurei = base * (0.90 - rate)

    tokurei_gendo = juminzei_shotokuwari_mae * 0.20
    juminzei_tokurei = max(0.0, min(juminzei_tokurei, tokurei_gendo))

    return {
        "所得税控除額": round(shotoku_zei, 4),
        "住民税控除額（基本分）": round(juminzei_kihon, 4),
        "住民税控除額（特例分）": round(juminzei_tokurei, 4),
        "控除合計": round(shotoku_zei + juminzei_kihon + juminzei_tokurei, 4),
        "自己負担額": JIKO_FUTAN,
    }
