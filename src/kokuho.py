# 国保 https://www.city.bunkyo.lg.jp/b021/p000424.html
# 年齢的に介護保険を支払う必要がないと想定

def kokumin_kenko_hoken(all_salary, kyuyo_syotoku_kojo, kiso_kojo):
    """
    国民健康保険料を計算（文京区・令和6年度想定）。
    
    Parameters:
        all_salary (float): 給与収入（万円単位）
        kyuyo_syotoku_kojo (float): 給与所得控除（万円単位）
        kiso_kojo (float): 住民税基礎控除（万円単位）
    
    Returns:
        dict: 総保険料、月額、基礎分、支援金分（すべて万円単位）
    """
    # 算定基礎額（所得割対象）
    sante_kiso = max(0, all_salary - kyuyo_syotoku_kojo - kiso_kojo)
    
    # 基礎分保険料
    syotoku_wari_kiso = sante_kiso * 0.0869
    kinto_wari_kiso = 4.91  # 均等割
    kiso_hoken = syotoku_wari_kiso + kinto_wari_kiso
    
    # 支援金分保険料
    syotoku_wari_sien = sante_kiso * 0.028
    kinto_wari_sien = 1.65
    sien_hoken = syotoku_wari_sien + kinto_wari_sien
    
    # 合計・月額
    total = kiso_hoken + sien_hoken
    monthly = total / 12
    
    return {
        "総保険料": total,
        "月額": monthly,
        "基礎分": kiso_hoken,
        "支援金分": sien_hoken
    }
