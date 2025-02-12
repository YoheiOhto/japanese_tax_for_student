# 住民税の基礎控除
def kiso_kojo_kuni(income):
    if income <= 2400:
        return 48
    elif income <= 2450:
        return 32
    elif income <= 2500:
        return 16
    else:
        return 0

# 玉木が石破に勝った場合 (所得税)
def kiso_kojo_kuni_tamaki(income):
    if income <= 2400:
        return 123
    elif income <= 2450:
        return 32
    elif income <= 2500:
        return 16
    else:
        return 0

# 宮沢が最強だった場合 (所得税)
def kiso_kojo_kuni_miyazawa(income):
    if income <= 2400:
        return 58
    elif income <= 2450:
        return 32
    elif income <= 2500:
        return 16
    else:
        return 0
    
# 住民税の基礎控除（住民税） (宮沢案も同じ) 
def kiso_kojo_chiho(income):
    if income <= 2400:
        return 43
    elif income <= 2450:
        return 29
    elif income <= 2500:
        return 15
    else:
        return 0

# 玉木が石破に勝った場合 (所得税)
def kiso_kojo_chiho_tamaki(income):
    if income <= 2400:
        return 118
    elif income <= 2450:
        return 29
    elif income <= 2500:
        return 15
    else:
        return 0