# TODO — japanese_tax_for_student 実装・修正リスト

すべての項目は実装済みです。詳細は `src/` 配下の各モジュールおよび `tests/` を参照してください。

---

## 🔴 計算が壊れているバグ（修正済み）

- [x] **iDeCo の上限が自営業前提になっている** — `src/config.py` の `IDECO_MAX_GETSU` で被保険者区分ごとの上限を定義し、`src/ideco.py` の `ideco_kojo()` で区分に応じてキャップするように修正
- [x] **国民健康保険が40〜64歳の介護分を計算していない** — `src/kokuho.py` の `kokumin_kenko_hoken()` が `num_kaigo_persons` を受け取り、介護分を別途計算するように修正
- [x] **2026年以降の健康保険料率がハードコード** — `src/config.py` の `KOKUHO_RATES` / `resolve_year_with_fallback()` により、年度ごとの料率を設定から読み込み、未対応年度は最新年度の値で概算（`概算フラグ` を出力）

---

## 🟡 計算の正確性に関わる未実装機能（実装済み）

- [x] **市区町村ごとの国民健康保険料率に対応する** — `src/config.py` の `KOKUHO_RATES` に自治体ごとの料率テーブルを定義し、`kokumin_kenko_hoken(municipality=...)` で指定可能に
- [x] **入力バリデーションを追加する** — `src/validation.py` の `validate_inputs()` で負の収入・上限超過などをチェックし `ValueError` を送出
- [x] **奨学金の課税区分を分ける** — `src/zassyotoku.py` の `scholarship_breakdown()` で給付型（非課税）・貸与型（雑所得）を区別

---

## 🟢 学生が実際に使いたい控除・計算（実装済み）

- [x] **扶養控除・配偶者控除を追加する** — `src/fuyou_koujo.py` の `fuyou_taisho_hantei()` / `haigusha_koujo()`。Web アプリの収入別シミュレーションで「扶養から外れる収入ライン」を可視化
- [x] **医療費控除を追加する** — `src/iryouhi_koujo.py`（通常の医療費控除とセルフメディケーション税制を比較し有利な方を採用）
- [x] **生命保険料控除・地震保険料控除を追加する** — `src/hoken_koujo.py`
- [x] **勤労学生控除を追加する** — `src/kinrou_gakusei.py`
- [x] **寄附金控除（ふるさと納税）を追加する** — `src/kifukin_koujo.py`
- [x] **源泉徴収額と実際の納税額の差分を出力する** — `src/gensen_choushuu.py` の `kanpu_tsuino_gaku()` で還付額/追納額を計算

---

## 🔵 UX・出力の改善（実装済み）

- [x] **サマリー出力を追加する** — `simulate_tax()` の戻り値の `"サマリー"` キーに、手取り・税金合計・社会保険料合計・実効負担率・還付/追納見込額をまとめて出力
- [x] **CLI インターフェースを追加する** — `cli.py`（argparse）。`uv run python cli.py --salary 200 --ideco 2` のように実行可能
- [x] **ファイル保存時にパスを表示する** — `src/simulator.py` の `save_result()` / `save_compare_result()` が `print(f"保存しました: {path}")` を出力
- [x] **グラフ出力を追加する** — `app.py` のTab2で収入額に対する手取り・税金・社会保険料の推移と、103/130/160/201万円の壁・扶養から外れるラインを折れ線グラフで表示

---

## ⚙️ コード品質（実装済み）

- [x] **`simulate.py` と `ohto_simulate.py` の重複を解消する** — 共通ロジックを `src/simulator.py` に統合し、`simulate.py` を削除、`ohto_simulate.py` は実行例スクリプトに簡素化
- [x] **マジックナンバーを定数化する** — 税率ブラケット・保険料率・控除額などを `src/config.py` に名前付き定数として集約
- [x] **型ヒントを追加する** — 新規モジュール（`src/config.py`、`src/simulator.py` 等）は `from __future__ import annotations` と型ヒント付きで実装
- [x] **テストを書く** — `tests/` に国税庁の計算例（税率ブラケット境界値195万・330万・695万・900万・1,800万・4,000万円等）と照合する単体テストを追加（`uv run pytest`）
- [x] **`requirements.txt` を作成する** — 依存ライブラリ（streamlit・plotly・pandas・numpy）を明記済み。開発用依存（pytest）は `pyproject.toml` の `dependency-groups.dev` に定義

---

## 📋 ドキュメント（実装済み）

- [x] **`archives/` フォルダに README を追加する** — `archives/README.md` に旧ファイルの一覧と現行実装への対応関係を記載
- [x] **出力項目の説明を追加する** — `README.md` に「出力項目の説明（用語集）」セクションを追加
- [x] **動作確認済みの年度を README に明記する** — `README.md` に「動作確認済みの年度」セクションを追加

---

## 今後の拡張候補（未着手）

- [ ] 文京区以外の自治体の国民健康保険料率データの追加
- [ ] 旧制度（2011年以前契約）の生命保険料控除への対応
- [ ] 配偶者の合計所得900万円超の場合の配偶者控除逓減への対応
- [ ] `src/kokuho.py`・`src/jumin_zei.py` 以外の既存モジュールへの型ヒント追加
