from __future__ import annotations

from .config import (
    DEFAULT_MUNICIPALITY,
    KOKUHO_RATES,
    KOKUHO_SANTEI_KOJO,
    resolve_year_with_fallback,
)


def kokumin_kenko_hoken(
    total_income: float,
    year: int,
    num_persons: int = 1,
    num_kaigo_persons: int = 0,
    municipality: str = DEFAULT_MUNICIPALITY,
) -> dict:
    """
    国民健康保険料（年額）を計算する。

    Parameters
    ----------
    total_income : float
        総所得金額等（万円）。世帯の合計所得を渡す。
    year : int
        課税対象年。`config.KOKUHO_RATES` に該当年度のデータが無い場合は
        最新の既知年度のレートで代用し、戻り値の `概算フラグ` を True にする。
    num_persons : int
        国民健康保険の被保険者数（世帯人数）。
    num_kaigo_persons : int
        被保険者のうち介護保険第2号被保険者（40〜64歳）の人数。
        0 の場合は介護分を計算しない。
    municipality : str
        自治体名。`config.KOKUHO_RATES` に対応するキーが必要。

    Returns
    -------
    dict
        年額・月額・内訳（万円）と、レートが代用値かどうかの概算フラグ。

    Notes
    -----
    - 所得割の算定基礎は「総所得金額等 - 住民税基礎控除相当額(43万円)」で計算する
      （実際の住民税基礎控除額が43万円でない高所得者層では簡略化となる）。
    - 介護分の所得割算定基礎も同じ `total_income` を用いる簡略化をしている
      （世帯内の介護対象者のみの所得で按分はしていない）。
    - 各区分（基礎分・支援金分・介護分）は「所得割＋均等割」の合計を
      区分ごとの賦課限度額でカットする。
    """
    if municipality not in KOKUHO_RATES:
        raise ValueError(
            f"未対応の自治体です: {municipality}. "
            f"対応自治体: {list(KOKUHO_RATES)}"
        )
    if num_kaigo_persons < 0 or num_kaigo_persons > num_persons:
        raise ValueError("num_kaigo_persons は 0 以上 num_persons 以下で指定してください。")

    table = KOKUHO_RATES[municipality]
    resolved_year, is_estimated = resolve_year_with_fallback(table, year)
    rates = table[resolved_year]

    sante_kiso = max(0.0, total_income - KOKUHO_SANTEI_KOJO)

    kiso_hoken = min(
        sante_kiso * rates.kiso_rate + rates.kiso_kinto * num_persons,
        rates.kiso_gendo,
    )
    sien_hoken = min(
        sante_kiso * rates.sien_rate + rates.sien_kinto * num_persons,
        rates.sien_gendo,
    )

    if num_kaigo_persons > 0 and rates.kaigo_rate is not None:
        kaigo_hoken = min(
            sante_kiso * rates.kaigo_rate + rates.kaigo_kinto * num_kaigo_persons,
            rates.kaigo_gendo,
        )
    else:
        kaigo_hoken = 0.0

    total = kiso_hoken + sien_hoken + kaigo_hoken

    return {
        "適用年度": resolved_year,
        "自治体": municipality,
        "概算フラグ": is_estimated,
        "出典": rates.source,
        "算定基礎所得": sante_kiso,
        "総保険料（年額）": total,
        "月額": total / 12,
        "基礎分": kiso_hoken,
        "支援金分": sien_hoken,
        "介護分": kaigo_hoken,
    }
