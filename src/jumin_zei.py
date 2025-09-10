# 住民税　https://biz.moneyforward.com/tax_return/basic/49732/#1　https://www.city.bunkyo.lg.jp/b008/p000357.html#sonota　

def tyosei_koujo(kazei_taisyo_not_tyosei, kokuzei_kiso_kojo, chihouzei_kiso_kojo):
    if kazei_taisyo_not_tyosei <= 200:
        a = abs(kokuzei_kiso_kojo - chihouzei_kiso_kojo)
        b = kazei_taisyo_not_tyosei
        koujo = min(a, b) * 0.05
    else:
        a = abs(kokuzei_kiso_kojo - chihouzei_kiso_kojo)
        b = kazei_taisyo_not_tyosei - 200
        koujo = (a - b) * 0.05
        if koujo < 0:
            koujo = 0
    return koujo