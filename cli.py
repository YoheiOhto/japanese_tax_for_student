"""
日本の税金シミュレーター CLI

Examples
--------
$ uv run python cli.py --salary 200 --salary 50 --year 2026

$ uv run python cli.py --salary 96 --student --age 20

$ uv run python cli.py --salary 400 --furusato-kifu 4 --save --label case1
"""

from __future__ import annotations

import argparse
import json

from src import DEFAULT_INSURED_TYPE, DEFAULT_MUNICIPALITY, IDECO_MAX_GETSU
from src import SimulationInput, save_result, simulate_tax


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="日本の税金シミュレーター（学生向け）")

    parser.add_argument(
        "--salary", type=float, action="append", default=[],
        help="給与収入（万円）。勤務先ごとに複数回指定できる（例: --salary 200 --salary 50）。"
        " 一度も指定しない場合は 0 として扱う。",
    )
    parser.add_argument("--main-salary-index", type=int, default=0, help="年末調整（甲欄）を受ける給与のインデックス（0始まり）")

    parser.add_argument("--zassyotoku-revenue", type=float, default=0.0, help="雑所得の収入（万円）")
    parser.add_argument("--zassyotoku-expenses", type=float, default=0.0, help="雑所得の必要経費（万円）")
    parser.add_argument("--aoiro", action="store_true", help="青色申告特別控除（65万円）を適用する")

    parser.add_argument("--scholarship-kyufugata", type=float, default=0.0, help="給付型奨学金（非課税・万円）")

    parser.add_argument("--year", type=int, default=2025, help="課税対象年")
    parser.add_argument("--fukkou", action="store_true", help="復興特別所得税（2.1%）を含める")

    parser.add_argument("--municipality", type=str, default=DEFAULT_MUNICIPALITY, help="自治体名（国民健康保険料の算定に使用）")
    parser.add_argument("--num-persons", type=int, default=1, help="国民健康保険の被保険者数（世帯人数）")
    parser.add_argument("--age", type=int, default=22, help="年齢（扶養判定・介護分判定に使用）")
    parser.add_argument("--num-kaigo-persons", type=int, default=0, help="介護保険第2号被保険者（40〜64歳）の人数")
    parser.add_argument(
        "--nenkin-frequency", type=str, default="毎月納付",
        choices=["毎月納付", "当月末振替", "6カ月前納", "1年前納", "2年前納"],
        help="国民年金の支払い頻度",
    )
    parser.add_argument(
        "--nenkin-method", type=str, default="口座振替",
        choices=["口座振替", "納付書払い", "クレジットカード払い"],
        help="国民年金の支払い方法",
    )

    parser.add_argument("--ideco", type=float, default=0.0, dest="ideco_getsu", help="iDeCo月額掛金（万円）")
    parser.add_argument(
        "--insured-type", type=str, default=DEFAULT_INSURED_TYPE,
        choices=list(IDECO_MAX_GETSU),
        help="iDeCoの被保険者区分",
    )

    parser.add_argument("--student", action="store_true", help="勤労学生控除の対象（学生）として計算する")

    parser.add_argument("--iryouhi-shiharai", type=float, default=0.0, help="医療費の年間支払額（万円）")
    parser.add_argument("--iryouhi-hoken-hoten", type=float, default=0.0, help="医療費に対する保険金等補填額（万円）")
    parser.add_argument("--otc-shiharai", type=float, default=0.0, help="OTC医薬品の年間購入額（セルフメディケーション税制、万円）")

    parser.add_argument("--seimei-hoken-ippan", type=float, default=0.0, help="一般生命保険料の年間支払額（万円）")
    parser.add_argument("--seimei-hoken-kaigo-iryou", type=float, default=0.0, help="介護医療保険料の年間支払額（万円）")
    parser.add_argument("--seimei-hoken-kojin-nenkin", type=float, default=0.0, help="個人年金保険料の年間支払額（万円）")
    parser.add_argument("--jishin-hoken", type=float, default=0.0, help="地震保険料の年間支払額（万円）")

    parser.add_argument("--furusato-kifu", type=float, default=0.0, help="ふるさと納税の年間寄附額（万円）")

    parser.add_argument("--spouse-income", type=float, default=None, help="配偶者の合計所得金額（万円）。指定時のみ配偶者控除を計算する")

    parser.add_argument("--save", action="store_true", help="結果を ./output に保存する")
    parser.add_argument("--label", type=str, default="cli", help="保存時のファイル名プレフィックス")
    parser.add_argument("--summary-only", action="store_true", help="サマリーのみを表示する")

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    inp = SimulationInput(
        salaries=args.salary or [0.0],
        main_salary_index=args.main_salary_index,
        zassyotoku_revenue=args.zassyotoku_revenue,
        zassyotoku_expenses=args.zassyotoku_expenses,
        aoiro_tokubetsu_kojo=args.aoiro,
        scholarship_kyufugata=args.scholarship_kyufugata,
        year=args.year,
        include_fukkou=args.fukkou,
        municipality=args.municipality,
        num_persons=args.num_persons,
        age=args.age,
        num_kaigo_persons=args.num_kaigo_persons,
        nenkin_frequency=args.nenkin_frequency,
        nenkin_method=args.nenkin_method,
        ideco_getsu=args.ideco_getsu,
        insured_type=args.insured_type,
        is_student=args.student,
        iryouhi_shiharai=args.iryouhi_shiharai,
        iryouhi_hoken_hoten=args.iryouhi_hoken_hoten,
        otc_shiharai=args.otc_shiharai,
        seimei_hoken_ippan=args.seimei_hoken_ippan,
        seimei_hoken_kaigo_iryou=args.seimei_hoken_kaigo_iryou,
        seimei_hoken_kojin_nenkin=args.seimei_hoken_kojin_nenkin,
        jishin_hoken=args.jishin_hoken,
        furusato_kifu=args.furusato_kifu,
        spouse_gokei_shotoku=args.spouse_income,
    )

    result = simulate_tax(inp)

    if args.summary_only:
        print(json.dumps(result["サマリー"], ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.save:
        save_result(result, output_dir="./output", label=args.label, fmt="both")


if __name__ == "__main__":
    main()
