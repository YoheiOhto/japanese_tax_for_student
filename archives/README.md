# archives/

このディレクトリには、現在の `src/` 以下の実装に統合される前に使われていた
古いノートブック・スクリプトを保管しています。**現行の計算ロジックではないため、
参照のみとし、新規開発には使用しないでください。**

## ファイル一覧

| ファイル | 内容 | 状態 |
| --- | --- | --- |
| `241205_insei_tedori.ipynb` | 院生の手取り計算シミュレーションの初期版ノートブック | 旧版（`src/simulator.py` に統合済み） |
| `241213_zatushotoku.ipynb` | 奨学金の雑所得区分に関する解説ノートブック | 旧版（解説内容は `src/zassyotoku.py` のdocstringに反映済み） |
| `260102_simulater.ipynb` | シミュレーターのノートブック版 | 旧版（`src/simulator.py` に統合済み） |
| `simulater.py` | 旧シミュレーター本体 | 旧版（`src/simulator.py` に統合・置き換え済み） |
| `syotoku_zei.py` | 所得税計算の旧実装 | 旧版（`src/income_tax.py` に統合済み） |

## 現行の実装

最新の計算ロジックは以下を参照してください。

- `src/` — 各種控除・税金計算ロジック（モジュール一覧は `src/__init__.py` を参照）
- `src/simulator.py` — `SimulationInput` / `simulate_tax()` による統合シミュレーション
- `app.py` — Streamlit Web アプリ
- `cli.py` — コマンドラインインターフェース
- `ohto_simulate.py` — `src.simulator` を使った実行例
