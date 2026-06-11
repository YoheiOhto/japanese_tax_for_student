"""
総合納税額シミュレーター（統合版）

【計算フロー】
  給与収入 → 給与所得（給与所得控除を差し引き）
  雑所得   = 収入 − 経費（青色申告特別控除を含む）
  合計所得 = 給与所得 + 雑所得

  ── 社会保険料 ──
  国民健康保険・国民年金を合計所得から自動計算し、社会保険料控除に算入する。

  ── 所得控除 ──
  基礎控除・社会保険料控除・iDeCo控除・勤労学生控除・医療費控除（or
  セルフメディケーション税制）・生命保険料控除・地震保険料控除・配偶者控除

  ── 所得税 ──
  課税所得 = 合計所得 − 各種所得控除
  所得税額 = calculate_income_tax(課税所得) − ふるさと納税の所得税控除額

  ── 住民税 ──
  課税所得（住民税） = 合計所得 − 各種所得控除（住民税ベース）
  住民税所得割       = 課税所得 × 10% − 調整控除 − ふるさと納税の住民税控除額

  ── 還付・追納 ──
  源泉徴収額（概算）と算出所得税額の差額から還付・追納見込額を計算する。

【出典】
  国税庁「確定申告書等作成コーナー」計算ロジック準拠
  https://www.nta.go.jp/taxes/shiraberu/shinkoku/kakutei.htm
"""

from __future__ import annotations

import csv
import dataclasses
import datetime
import json
from dataclasses import dataclass
from pathlib import Path

from .config import DEFAULT_INSURED_TYPE, DEFAULT_MUNICIPALITY, IDECO_MAX_GETSU
from .fuyou_koujo import fuyou_taisho_hantei, haigusha_koujo
from .gensen_choushuu import gensen_choushuu_gaku, kanpu_tsuino_gaku
from .hoken_koujo import jishin_hoken_koujo, seimei_hoken_koujo
from .ideco import ideco_kojo
from .income_tax import calculate_income_tax
from .iryouhi_koujo import select_iryouhi_koujo
from .jumin_zei import tyosei_koujo
from .kifukin_koujo import furusato_nouzei_koujo
from .kinrou_gakusei import kinrou_gakusei_koujo
from .kiso_koujo import kiso_kojo_chiho, kiso_kojo_kuni
from .kokuho import kokumin_kenko_hoken
from .kokumin_nenkin import kokumin_nenkin_payment
from .kyuyosyotoku_koujo import kyuyo_syotoku_kojo
from .validation import validate_inputs
from .zassyotoku import scholarship_breakdown, zassyotoku


@dataclass
class SimulationInput:
    """`simulate_tax()` への入力をまとめたデータクラス。"""

    salaries: list[float]
    main_salary_index: int = 0

    zassyotoku_revenue: float = 0.0
    zassyotoku_expenses: float = 0.0
    aoiro_tokubetsu_kojo: bool = False

    scholarship_kyufugata: float = 0.0
    """給付型奨学金（非課税・年額・万円）。合計所得には含めない。"""

    year: int = 2025
    include_fukkou: bool = False

    # 社会保険
    municipality: str = DEFAULT_MUNICIPALITY
    num_persons: int = 1
    age: int = 22
    num_kaigo_persons: int = 0
    nenkin_frequency: str = "毎月納付"
    nenkin_method: str = "口座振替"

    # iDeCo
    ideco_getsu: float = 0.0
    insured_type: str = DEFAULT_INSURED_TYPE

    # 勤労学生控除
    is_student: bool = False

    # 医療費控除 / セルフメディケーション税制
    iryouhi_shiharai: float = 0.0
    iryouhi_hoken_hoten: float = 0.0
    otc_shiharai: float = 0.0

    # 生命保険料控除
    seimei_hoken_ippan: float = 0.0
    seimei_hoken_kaigo_iryou: float = 0.0
    seimei_hoken_kojin_nenkin: float = 0.0

    # 地震保険料控除
    jishin_hoken: float = 0.0

    # ふるさと納税
    furusato_kifu: float = 0.0

    # 配偶者控除（配偶者がいない場合は None）
    spouse_gokei_shotoku: float | None = None


def simulate_tax(inp: SimulationInput) -> dict:
    """
    給与・雑所得・各種控除をもとに所得税・住民税を計算する。

    Parameters
    ----------
    inp : SimulationInput
        シミュレーション条件一式。

    Returns
    -------
    dict
        所得・控除・税額・還付見込額などの内訳（万円単位）。
        トップレベルの "サマリー" キーに主要な数値をまとめている。
    """
    if inp.insured_type not in IDECO_MAX_GETSU:
        raise ValueError(
            f"未対応の被保険者区分です: {inp.insured_type}. "
            f"対応区分: {list(IDECO_MAX_GETSU)}"
        )

    validate_inputs(
        salaries=inp.salaries,
        zassyotoku_revenue=inp.zassyotoku_revenue,
        zassyotoku_expenses=inp.zassyotoku_expenses,
        ideco_getsu=inp.ideco_getsu,
        ideco_max_getsu=IDECO_MAX_GETSU[inp.insured_type],
        iryouhi_shiharai=inp.iryouhi_shiharai,
        iryouhi_hoken_hoten=inp.iryouhi_hoken_hoten,
        otc_shiharai=inp.otc_shiharai,
        seimei_hoken_payments=[
            inp.seimei_hoken_ippan,
            inp.seimei_hoken_kaigo_iryou,
            inp.seimei_hoken_kojin_nenkin,
        ],
        jishin_hoken=inp.jishin_hoken,
        furusato_kifu=inp.furusato_kifu,
        num_persons=inp.num_persons,
        num_kaigo_persons=inp.num_kaigo_persons,
    )

    # ── 1. 給与所得 ──────────────────────────────────────────
    # 複数給与は各給与に控除を適用してから合算（合算後控除ではない）
    # 給与所得控除は収入を超えない（最低0）
    kyuyo_shotoku_list = [
        max(0.0, s - kyuyo_syotoku_kojo(s, inp.year)) for s in inp.salaries
    ]
    kyuyo_shotoku_total = sum(kyuyo_shotoku_list)

    # ── 2. 雑所得（青色申告特別控除を含む）──────────────────
    zasso = zassyotoku(inp.zassyotoku_revenue, inp.zassyotoku_expenses, inp.aoiro_tokubetsu_kojo)
    aoiro_kojo_actual = max(0.0, inp.zassyotoku_revenue - inp.zassyotoku_expenses) - zasso

    # ── 3. 合計所得金額 ────────────────────────────────────────
    gokei_shotoku = kyuyo_shotoku_total + zasso

    # ── 4. 社会保険料控除（国保＋年金）────────────────────────
    kokuho = kokumin_kenko_hoken(
        gokei_shotoku,
        year=inp.year,
        num_persons=inp.num_persons,
        num_kaigo_persons=inp.num_kaigo_persons,
        municipality=inp.municipality,
    )
    nenkin = kokumin_nenkin_payment(
        inp.nenkin_frequency, inp.nenkin_method, fiscal_year=inp.year
    )

    kokuho_nen = kokuho["総保険料（年額）"]
    nenkin_nen = nenkin["年換算額（万円）"]
    shakai_hoken = kokuho_nen + nenkin_nen

    # ── 5. iDeCo 控除 ─────────────────────────────────────────
    ideco_kojo_nen = ideco_kojo(inp.ideco_getsu, inp.insured_type)

    # ── 6. 基礎控除 ───────────────────────────────────────────
    kiso_kuni = kiso_kojo_kuni(gokei_shotoku, inp.year)
    kiso_chiho = kiso_kojo_chiho(gokei_shotoku, inp.year)

    # ── 7. 勤労学生控除 ───────────────────────────────────────
    kinrou = kinrou_gakusei_koujo(inp.is_student, gokei_shotoku, kyuyo_shotoku_total)

    # ── 8. 医療費控除 / セルフメディケーション税制 ─────────────
    iryouhi = select_iryouhi_koujo(
        inp.iryouhi_shiharai, inp.iryouhi_hoken_hoten, inp.otc_shiharai, gokei_shotoku
    )

    # ── 9. 生命保険料控除・地震保険料控除 ──────────────────────
    seimei = seimei_hoken_koujo(
        inp.seimei_hoken_ippan, inp.seimei_hoken_kaigo_iryou, inp.seimei_hoken_kojin_nenkin
    )
    jishin = jishin_hoken_koujo(inp.jishin_hoken)

    # ── 10. 配偶者控除 ──────────────────────────────────────────
    if inp.spouse_gokei_shotoku is None:
        haigusha = {"所得税": 0.0, "住民税": 0.0, "備考": "配偶者なし"}
    else:
        haigusha = haigusha_koujo(gokei_shotoku, inp.spouse_gokei_shotoku)

    # ── 11. 所得控除合計（所得税・住民税で別計算）───────────────
    sonota_kojo_kuni = (
        ideco_kojo_nen
        + kinrou["控除額（所得税）"]
        + iryouhi["控除額"]
        + seimei["所得税"]
        + jishin["所得税"]
        + haigusha["所得税"]
    )
    sonota_kojo_chiho = (
        ideco_kojo_nen
        + kinrou["控除額（住民税）"]
        + iryouhi["控除額"]
        + seimei["住民税"]
        + jishin["住民税"]
        + haigusha["住民税"]
    )

    # ── 12. 所得税の課税所得・税額 ─────────────────────────────
    kazei_shotoku_kuni = max(
        0.0,
        gokei_shotoku - kiso_kuni - shakai_hoken - sonota_kojo_kuni,
    )
    zei_kuni_mae = calculate_income_tax(kazei_shotoku_kuni, inp.include_fukkou)

    # ── 13. 住民税の課税所得・税額 ─────────────────────────────
    kazei_shotoku_chiho = max(
        0.0,
        gokei_shotoku - kiso_chiho - shakai_hoken - sonota_kojo_chiho,
    )
    juminzei_mae_chosei = kazei_shotoku_chiho * 0.10
    chosei = tyosei_koujo(kazei_shotoku_chiho, kiso_kuni, kiso_chiho)
    juminzei_mae = max(0.0, juminzei_mae_chosei - chosei)

    # ── 14. ふるさと納税（寄附金控除）─────────────────────────
    furusato = furusato_nouzei_koujo(
        inp.furusato_kifu, kazei_shotoku_kuni, juminzei_mae, inp.include_fukkou
    )
    zei_kuni = max(0.0, zei_kuni_mae - furusato["所得税控除額"])
    juminzei = max(
        0.0,
        juminzei_mae - furusato["住民税控除額（基本分）"] - furusato["住民税控除額（特例分）"],
    )

    # ── 15. 扶養判定（自分が親などの扶養に入れるか）─────────────
    fuyou = fuyou_taisho_hantei(gokei_shotoku, inp.year, inp.age)

    # ── 16. 源泉徴収・還付/追納の概算 ───────────────────────────
    gensen = gensen_choushuu_gaku(inp.salaries, inp.main_salary_index)
    kanpu = kanpu_tsuino_gaku(gensen["合計"], zei_kuni)

    # ── 17. サマリー ────────────────────────────────────────────
    scholarship = scholarship_breakdown(inp.scholarship_kyufugata, inp.zassyotoku_revenue)

    sotai_total = sum(inp.salaries) + inp.zassyotoku_revenue + inp.scholarship_kyufugata
    total_zei = zei_kuni + juminzei
    take_home = sotai_total - inp.zassyotoku_expenses - shakai_hoken - total_zei
    effective_rate = (
        (shakai_hoken + total_zei) / (sotai_total - inp.zassyotoku_expenses) * 100
        if sotai_total - inp.zassyotoku_expenses > 0
        else 0.0
    )

    return {
        # 入力サマリ
        "対象年": inp.year,
        "自治体": inp.municipality,
        "給与収入合計": sum(inp.salaries),
        "給与収入内訳": inp.salaries,
        "雑所得収入": inp.zassyotoku_revenue,
        "雑所得経費": inp.zassyotoku_expenses,
        "奨学金内訳": scholarship,

        # 所得計算
        "給与所得合計": round(kyuyo_shotoku_total, 4),
        "給与所得内訳": [round(x, 4) for x in kyuyo_shotoku_list],
        "雑所得": round(zasso, 4),
        "合計所得金額": round(gokei_shotoku, 4),

        # 社会保険料（自動計算）
        "国民健康保険": kokuho,
        "国民年金": nenkin,
        "社会保険料控除": round(shakai_hoken, 4),

        # 各種控除
        "iDeCo控除（年額）": ideco_kojo_nen,
        "iDeCo月額掛金": min(inp.ideco_getsu, IDECO_MAX_GETSU[inp.insured_type]),
        "青色申告特別控除": round(aoiro_kojo_actual, 4),
        "勤労学生控除": kinrou,
        "医療費控除": iryouhi,
        "生命保険料控除": seimei,
        "地震保険料控除": jishin,
        "配偶者控除": haigusha,
        "ふるさと納税控除": furusato,

        # 基礎控除・調整控除
        "基礎控除（所得税）": kiso_kuni,
        "基礎控除（住民税）": kiso_chiho,
        "調整控除（住民税）": round(chosei, 4),

        # 課税所得
        "課税所得（所得税）": round(kazei_shotoku_kuni, 4),
        "課税所得（住民税）": round(kazei_shotoku_chiho, 4),

        # 税額
        "所得税額（寄附金控除前）": round(zei_kuni_mae, 4),
        "所得税額": round(zei_kuni, 4),
        "住民税額（所得割・寄附金控除前）": round(juminzei_mae, 4),
        "住民税額（所得割）": round(juminzei, 4),
        "合計納税額": round(total_zei, 4),

        # 扶養判定
        "扶養判定": fuyou,

        # 源泉徴収・還付/追納
        "源泉徴収": gensen,
        "還付追納": kanpu,

        # フラグ
        "復興特別所得税込み": inp.include_fukkou,

        # サマリー
        "サマリー": {
            "総収入（非課税収入含む）": round(sotai_total, 4),
            "手取り収入": round(take_home, 4),
            "税金合計": round(total_zei, 4),
            "社会保険料合計": round(shakai_hoken, 4),
            "実効負担率(%)": round(effective_rate, 2),
            "還付見込額": kanpu["還付額"],
            "追納見込額": kanpu["追納額"],
        },
    }


def compare_tax_by_year(
    base: SimulationInput,
    years: list[int] = [2024, 2025, 2026, 2027],
) -> dict[int, dict]:
    """
    `base` の条件のうち年度のみを変えて複数年度の結果を一括比較する。

    Parameters
    ----------
    base : SimulationInput
        比較条件のベース。`year` 以外の項目は全年度共通で適用される。
    years : list[int]
        比較したい年度のリスト。デフォルトは 2024〜2027。

    Returns
    -------
    dict[int, dict]
        { year: simulate_tax() の戻り値 } の辞書。

    Example
    -------
    >>> base = SimulationInput(salaries=[400.0])
    >>> results = compare_tax_by_year(base)
    >>> for year, r in results.items():
    ...     print(year, r["合計納税額"])
    """
    results = {}
    for y in years:
        inp = _replace_year(base, y)
        results[y] = simulate_tax(inp)
    return results


def _replace_year(base: SimulationInput, year: int) -> SimulationInput:
    return dataclasses.replace(base, year=year)


# ============================================================
# 結果の保存
# ============================================================

def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def save_result(
    result: dict,
    output_dir: str = ".",
    label: str = "",
    fmt: str = "both",
) -> dict[str, Path]:
    """
    `simulate_tax()` の結果を JSON・CSV に保存する。

    Parameters
    ----------
    result : dict
        `simulate_tax()` の戻り値。
    output_dir : str
        保存先ディレクトリ。存在しない場合は自動作成。
    label : str
        ファイル名のプレフィックス（例: "case1"）。省略時はタイムスタンプのみ。
    fmt : str
        "json" / "csv" / "both"

    Returns
    -------
    dict[str, Path]
        保存したファイルのパス。例: {"json": Path(...), "csv": Path(...)}
    """
    base_dir = Path(output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    ts = _timestamp()
    prefix = f"{label}_{ts}" if label else ts
    saved = {}

    if fmt in ("json", "both"):
        path = base_dir / f"{prefix}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        saved["json"] = path
        print(f"保存しました: {path}")

    if fmt in ("csv", "both"):
        path = base_dir / f"{prefix}.csv"
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["項目", "値"])
            for k, v in result.items():
                writer.writerow([k, v])
        saved["csv"] = path
        print(f"保存しました: {path}")

    return saved


def save_compare_result(
    results: dict[int, dict],
    output_dir: str = ".",
    label: str = "",
    fmt: str = "both",
) -> dict[str, Path]:
    """
    `compare_tax_by_year()` の結果を JSON・CSV に保存する。

    Parameters
    ----------
    results : dict[int, dict]
        `compare_tax_by_year()` の戻り値。
    output_dir : str
        保存先ディレクトリ。存在しない場合は自動作成。
    label : str
        ファイル名のプレフィックス（例: "compare_case1"）。
    fmt : str
        "json" / "csv" / "both"

    Returns
    -------
    dict[str, Path]
        保存したファイルのパス。

    Notes
    -----
    CSV は年度を列方向に並べた横持ち形式で出力する。
    各行が「項目」、各列が「年度」に対応する。
    """
    base_dir = Path(output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    ts = _timestamp()
    prefix = f"{label}_{ts}" if label else ts
    saved = {}

    if fmt in ("json", "both"):
        path = base_dir / f"{prefix}.json"
        serializable = {str(y): v for y, v in results.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
        saved["json"] = path
        print(f"保存しました: {path}")

    if fmt in ("csv", "both"):
        path = base_dir / f"{prefix}.csv"
        years = list(results.keys())
        keys = list(next(iter(results.values())).keys())

        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["項目"] + [f"{y}年" for y in years])
            for k in keys:
                row = [k] + [results[y].get(k, "") for y in years]
                writer.writerow(row)
        saved["csv"] = path
        print(f"保存しました: {path}")

    return saved
