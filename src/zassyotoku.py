from __future__ import annotations


def zassyotoku(
    revenue: float,
    expenses: float,
    aoiro_tokubetsu_kojo: bool = False,
) -> float:
    """
    雑所得を計算する（副業・フリーランス・貸与型奨学金などを想定）。

    Parameters
    ----------
    revenue : float
        雑所得の収入金額（万円）。給付型奨学金は非課税のためここには含めない
        （`scholarship_kyufugata_gaku` で別途扱う）。
    expenses : float
        必要経費（万円）。収入に直接対応する費用のみ算入可。
    aoiro_tokubetsu_kojo : bool
        True = 青色申告特別控除（65万円）を適用する。
        雑所得は本来青色申告の対象外だが、令和2年以降、一定要件を満たす
        事業的規模の副業（帳簿保存・e-Tax申告）は事業所得として65万円控除が
        可能。ここでは「雑所得扱いのまま65万円控除」として簡易的にシミュレート。
        ※ 実務上は税理士への確認を推奨。

    Returns
    -------
    float
        雑所得金額（万円）。マイナスは 0 として扱う（他の所得との損益通算不可）。

    Notes
    -----
    - 副業・フリーランスの報酬や貸与型奨学金（雑所得として扱われる場合）は
      原則「雑所得」に該当する。
    - 給与所得との損益通算は不可（雑所得のマイナスは切り捨て）。
    """
    shotoku = revenue - expenses
    if aoiro_tokubetsu_kojo:
        shotoku -= 65  # 青色申告特別控除 65万円
    return max(0.0, shotoku)


def scholarship_breakdown(
    kyufugata_gaku: float = 0.0,
    taiyogata_gaku: float = 0.0,
) -> dict:
    """
    奨学金を課税区分ごとに振り分ける。

    Parameters
    ----------
    kyufugata_gaku : float
        給付型奨学金の年間受給額（万円）。所得税法上非課税
        （所得税法9条1項15号）のため、合計所得金額には算入しない。
    taiyogata_gaku : float
        貸与型奨学金の年間受給額（万円）。
        貸与型は「借入金」であり原則として所得には該当しないが、
        給与代わりに支給される一部の制度では雑所得扱いとなる場合がある。
        本シミュレーターでは「雑所得として課税対象になる金額」として
        `zassyotoku_revenue` に加算することを想定している。

    Returns
    -------
    dict
        非課税収入・課税対象収入の内訳（万円）。

    Notes
    -----
    実際にどちらの区分に該当するかは奨学金制度・契約内容によって異なるため、
    最終的な判断は各自の奨学金規定・税理士への確認が必要。
    """
    return {
        "非課税収入（給付型奨学金）": kyufugata_gaku,
        "課税対象収入（貸与型奨学金等・雑所得扱い）": taiyogata_gaku,
    }
