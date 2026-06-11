"""
年度・自治体・被保険者区分などに依存するレート表をまとめた設定モジュール。

新しい年度や自治体に対応する場合は、このファイルにテーブルを追記するだけで済むようにする。
"""

from __future__ import annotations

from dataclasses import dataclass


# ============================================================
# 所得税率表（超過累進課税）
# ============================================================
# 出典: 国税庁「No.2260 所得税の税率」
# https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2260.htm
# (threshold[万円], 税率, 控除額[万円])

INCOME_TAX_BRACKETS: list[tuple[float, float, float]] = [
    (195, 0.05, 0.00),
    (330, 0.10, 9.75),
    (695, 0.20, 42.75),
    (900, 0.23, 63.60),
    (1800, 0.33, 153.60),
    (4000, 0.40, 279.60),
    (float("inf"), 0.45, 479.60),
]

# 復興特別所得税率（2037年まで）
FUKKOU_RATE = 0.021


# ============================================================
# iDeCo（個人型確定拠出年金）掛金上限（万円/月）
# ============================================================
# 出典: iDeCo公式サイト「加入対象者・掛金限度額」
# https://www.ideco-koushiki.jp/start/

IDECO_MAX_GETSU: dict[str, float] = {
    "自営業・フリーランス・学生（第1号被保険者）": 6.8,
    "会社員（企業年金なし）": 2.3,
    "会社員（企業型DCのみ加入）": 2.0,
    "会社員（DB等の他制度あり）または公務員": 1.2,
    "専業主婦・主夫（第3号被保険者）": 2.3,
}

DEFAULT_INSURED_TYPE = "自営業・フリーランス・学生（第1号被保険者）"


# ============================================================
# 国民健康保険 料率テーブル（自治体・年度別）
# ============================================================
# 介護分は40〜64歳（介護保険第2号被保険者）に該当する世帯員がいる場合のみ加算する。
# 各区分の「年額 = 所得割 + 均等割」を賦課限度額（gendo）でカットする。

@dataclass(frozen=True)
class KokuhoRateSet:
    kiso_rate: float
    kiso_kinto: float
    kiso_gendo: float
    sien_rate: float
    sien_kinto: float
    sien_gendo: float
    kaigo_rate: float | None
    kaigo_kinto: float | None
    kaigo_gendo: float | None
    source: str


KOKUHO_RATES: dict[str, dict[int, KokuhoRateSet]] = {
    "文京区": {
        2025: KokuhoRateSet(
            kiso_rate=0.0771, kiso_kinto=4.73, kiso_gendo=66,
            sien_rate=0.0269, sien_kinto=1.68, sien_gendo=26,
            kaigo_rate=0.0223, kaigo_kinto=1.66, kaigo_gendo=17,
            source=(
                "文京区「国民健康保険税（保険料）」"
                "https://www.city.bunkyo.lg.jp/b021/p000424.html"
            ),
        ),
        2026: KokuhoRateSet(
            kiso_rate=0.0751, kiso_kinto=4.76, kiso_gendo=67,
            sien_rate=0.0280, sien_kinto=1.76, sien_gendo=26,
            kaigo_rate=0.0243, kaigo_kinto=1.78, kaigo_gendo=17,
            source=(
                "文京区「国民健康保険税（保険料）」"
                "https://www.city.bunkyo.lg.jp/b021/p000424.html"
            ),
        ),
    },
}

DEFAULT_MUNICIPALITY = "文京区"

# 国保の所得割算定基礎から控除する額（住民税基礎控除相当額・万円）
KOKUHO_SANTEI_KOJO = 43.0


# ============================================================
# 勤労学生控除
# ============================================================
# 出典: 国税庁「No.1175 勤労学生控除」
# https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1175.htm

KINROU_GAKUSEI_KOUJO_KUNI = 27.0   # 所得税
KINROU_GAKUSEI_KOUJO_CHIHO = 26.0  # 住民税
KINROU_GAKUSEI_GOKEI_SHOTOKU_GENDO = 85.0   # 合計所得金額の上限
KINROU_GAKUSEI_SONOTA_SHOTOKU_GENDO = 10.0  # 給与所得等以外の所得の上限


# ============================================================
# 医療費控除・セルフメディケーション税制
# ============================================================
# 出典: 国税庁「No.1120 医療費を支払ったとき（医療費控除）」
#       「No.1131 セルフメディケーション税制の概要」

IRYOUHI_KOUJO_GENDO = 200.0          # 医療費控除の上限（万円）
IRYOUHI_KOUJO_TEIGAKU = 10.0         # 足切り額（万円）の上限
IRYOUHI_KOUJO_WARIAI = 0.05          # 合計所得金額に対する足切り割合
SELF_MEDICATION_SHIKIRI = 1.2        # セルフメディケーション税制の足切り額（万円）
SELF_MEDICATION_GENDO = 8.8          # セルフメディケーション税制の上限（万円）


# ============================================================
# 生命保険料控除・地震保険料控除（新制度・2012年以降契約）
# ============================================================
# 出典: 国税庁「No.1140 生命保険料控除」「No.1145 地震保険料控除」

SEIMEI_HOKEN_KUNI_GENDO_PER_KUBUN = 4.0   # 1区分あたりの所得税控除上限
SEIMEI_HOKEN_KUNI_GENDO_GOKEI = 12.0      # 所得税控除合計の上限
SEIMEI_HOKEN_CHIHO_GENDO_PER_KUBUN = 2.8  # 1区分あたりの住民税控除上限
SEIMEI_HOKEN_CHIHO_GENDO_GOKEI = 7.0      # 住民税控除合計の上限

JISHIN_HOKEN_KUNI_GENDO = 5.0     # 地震保険料控除（所得税）の上限
JISHIN_HOKEN_CHIHO_GENDO = 2.5    # 地震保険料控除（住民税）の上限


# ============================================================
# 扶養控除（控除対象扶養親族の所得要件）
# ============================================================
# 出典: 国税庁「No.1180 扶養控除」（令和7年度改正で所得要件 48万円→58万円）

FUYOU_TAISHO_GOKEI_SHOTOKU_GENDO_OLD = 48.0  # 2024年以前
FUYOU_TAISHO_GOKEI_SHOTOKU_GENDO_NEW = 58.0  # 2025年以降

FUYOU_KOUJO_TOKUTEI_KUNI = 63.0   # 特定扶養親族（19〜22歳）所得税
FUYOU_KOUJO_TOKUTEI_CHIHO = 45.0  # 特定扶養親族（19〜22歳）住民税
FUYOU_KOUJO_IPPAN_KUNI = 38.0     # 一般扶養親族（16〜18歳・23〜69歳）所得税
FUYOU_KOUJO_IPPAN_CHIHO = 33.0    # 一般扶養親族（16〜18歳・23〜69歳）住民税


# ============================================================
# 源泉徴収（乙欄）の概算税率
# ============================================================
# 複数の勤務先を掛け持ちする場合、メイン以外の給与は「乙欄」が適用され、
# 給与収入に対し一律 3.063%（所得税 + 復興特別所得税）が源泉徴収される。
# 出典: 国税庁「給与所得の源泉徴収税額表（月額表）」乙欄

GENSEN_OTSURAN_RATE = 0.03063


# ============================================================
# 共通ヘルパー
# ============================================================

def resolve_year_with_fallback(table: dict[int, object], year: int) -> tuple[int, bool]:
    """
    year に対応するデータが table に無い場合、最新の既知年度で代用する。

    Returns
    -------
    (採用した年度, 概算フラグ)
        概算フラグ True の場合、本来の year 用データが存在せず、
        最新の既知年度の値で代用していることを示す。
    """
    if year in table:
        return year, False
    latest = max(table)
    return latest, True


def marginal_income_tax_rate(taxable_income: float) -> float:
    """課税所得（万円）に対応する所得税の限界税率を返す。"""
    for threshold, rate, _ in INCOME_TAX_BRACKETS:
        if taxable_income <= threshold:
            return rate
    return INCOME_TAX_BRACKETS[-1][1]
