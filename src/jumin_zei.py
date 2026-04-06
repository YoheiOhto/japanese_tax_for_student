# 住民税　https://biz.moneyforward.com/tax_return/basic/49732/#1　https://www.city.bunkyo.lg.jp/b008/p000357.html#sonota　


def tyosei_koujo(
    kazei_taisyo_not_tyosei: float,
    kokuzei_kiso_kojo: float,
    chihouzei_kiso_kojo: float,
) -> float:
    """
    住民税の調整控除（万円単位）
 
    所得税と住民税で基礎控除額が異なるため、その差額に起因する
    住民税の過大負担を調整するための控除。
 
    Parameters
    ----------
    kazei_taisyo_not_tyosei : float
        調整控除前の住民税の課税所得（万円）
    kokuzei_kiso_kojo : float
        所得税の基礎控除額（万円）。kiso_kojo_kuni() の戻り値を渡す。
    chihouzei_kiso_kojo : float
        住民税の基礎控除額（万円）。kiso_kojo_chiho() の戻り値を渡す。
 
    Returns
    -------
    float
        調整控除額（万円）
 
    計算ロジック
    ------------
    差額 = |所得税基礎控除 − 住民税基礎控除|
 
    課税所得 ≤ 200万円:
        控除額 = min(差額, 課税所得) × 5%
 
    課税所得 > 200万円:
        控除額 = max(差額 − (課税所得 − 200), 0) × 5%
 
    ※ 令和7年度改正で所得税基礎控除が引き上げられた一方、住民税基礎控除は据え置き。
       差額が拡大するため、高所得でない限り調整控除額が増加する。
 
    出典:
    - 文京区「住民税の控除」https://www.city.bunkyo.lg.jp/b008/p000357.html
    """
 
    diff = abs(kokuzei_kiso_kojo - chihouzei_kiso_kojo)
 
    if kazei_taisyo_not_tyosei <= 200:
        koujo = min(diff, kazei_taisyo_not_tyosei) * 0.05
    else:
        koujo = max(diff - (kazei_taisyo_not_tyosei - 200), 0) * 0.05
 
    return round(koujo, 6)