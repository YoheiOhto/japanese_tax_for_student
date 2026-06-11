from __future__ import annotations

from .config import DEFAULT_INSURED_TYPE, IDECO_MAX_GETSU


def ideco_kojo(getsu_kakkin: float, insured_type: str = DEFAULT_INSURED_TYPE) -> float:
    """
    iDeCo（小規模企業共済等掛金控除）の年間控除額を計算する。

    Parameters
    ----------
    getsu_kakkin : float
        月額掛金（万円）。0.0 を渡した場合は控除なし（0を返す）。
    insured_type : str
        被保険者区分。`config.IDECO_MAX_GETSU` のキーのいずれか。
        区分ごとの月額上限（万円）:

        - 自営業・フリーランス・学生（第1号被保険者）: 6.8万円
        - 会社員（企業年金なし）: 2.3万円
        - 会社員（企業型DCのみ加入）: 2.0万円
        - 会社員（DB等の他制度あり）または公務員: 1.2万円
        - 専業主婦・主夫（第3号被保険者）: 2.3万円

    Returns
    -------
    float
        年間控除額（万円）。掛金全額が所得控除になる。

    Notes
    -----
    - iDeCo 掛金は全額「小規模企業共済等掛金控除」として所得税・住民税の両方から控除。
    - 国保の算定基礎（合計所得）には影響しない点に注意
      （国保は社会保険料控除前の所得で計算するため）。
    """
    if getsu_kakkin < 0:
        raise ValueError("月額掛金は0以上で指定してください。")
    if insured_type not in IDECO_MAX_GETSU:
        raise ValueError(
            f"未対応の被保険者区分です: {insured_type}. "
            f"対応区分: {list(IDECO_MAX_GETSU)}"
        )
    capped = min(getsu_kakkin, IDECO_MAX_GETSU[insured_type])
    return round(capped * 12, 4)
