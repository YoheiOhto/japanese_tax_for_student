# # 関数化していない

# # 国保 https://www.city.bunkyo.lg.jp/b021/p000424.html
# # 年齢的に介護保険を支払う必要がないと想定
# kiso_kojo = kiso_kojo_chiho(all_salary)
# sante_kiso = all_salary - kyuyo_syotoku_kojo - kiso_kojo # 算定基礎額(所得) = 総所得(給与所得控除が計算済み) - 基礎控除

# if sante_kiso < 0:
#     sante_kiso = 0 # 基礎控除がマイナスになる場合は0として扱う

# syotoku_wari_kiso = sante_kiso * (8.69 / 100) #〔所得割額〕被保険者全員の令和6年度の算定基礎額 × 8.69％
# kinto_wari_kiso = 4.9100 * 1 # 〔均等割額〕49,100円 × 被保険者数 (独身想定の為1)
# kiso_hoken = syotoku_wari_kiso + kinto_wari_kiso

# print("基礎分保険料", kiso_hoken)

# syotoku_wari_sien = sante_kiso * (2.80 / 100) #〔所得割額〕被保険者全員の令和6年度の算定基礎額 × 2.80％
# kinto_wari_sien = 1.6500 * 1 # 〔均等割額〕16,500円 × 被保険者数(1)
# sien_hoken = syotoku_wari_sien + kinto_wari_sien

# print("支援金分保険料", sien_hoken)

# kokuho = kiso_hoken + sien_hoken
# monthly_kokuho = kokuho / 12

# print("国保", kokuho, "万円, 月額", monthly_kokuho, "万円")