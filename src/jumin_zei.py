# 住民税　https://biz.moneyforward.com/tax_return/basic/49732/#1　https://www.city.bunkyo.lg.jp/b008/p000357.html#sonota　

def tyosei_koujo(kazei_taisyo_not_tyosei, kokuzei_kiso_kojo, chihouzei_kiso_kojo):
    """
    住民税の調整控除
    単位：
      - kazei_taisyo_not_tyosei : 課税所得（万円）
      - kokuzei_kiso_kojo      : 所得税の基礎控除（万円）
      - chihouzei_kiso_kojo    : 住民税の基礎控除（万円）
    戻り値：
      - 調整控除額（万円）
    """
    diff = abs(kokuzei_kiso_kojo - chihouzei_kiso_kojo)

    if kazei_taisyo_not_tyosei <= 200:
        # 課税所得200万円以下
        koujo = min(diff, kazei_taisyo_not_tyosei) * 0.05
    else:
        # 課税所得200万円超
        koujo = max(diff - (kazei_taisyo_not_tyosei - 200), 0) * 0.05

    return koujo
