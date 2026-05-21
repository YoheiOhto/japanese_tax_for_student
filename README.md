# japanese_tax_for_student

## 概要

このプロジェクトは、日本の税金制度、特に大学生や大学院生が直面する可能性のある税金について、Pythonで理解を深めることを目的としています。Jupyter NotebookとPythonスクリプトを用いて、給与所得者や奨学金受給者の手取り額をシミュレーションできます。

## 主な機能

* **手取り計算シミュレーション**: `241205_insei_tedori.ipynb` では、給与、奨学金、雑所得を合算した総収入から、所得税、住民税、国民年金、国民健康保険などの控除・税金を差し引いた手取り額を計算します。
* **各種控除・税金の計算**: `src` ディレクトリには、以下の計算ロジックを実装したPythonスクリプトが含まれています。
    * **所得税**: 以下の国税庁の情報を参考にしています。
        * [No.2260 所得税の税率](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2260.htm)
        * [定額減税特設サイト](https://www.nta.go.jp/users/gensen/teigakugenzei/01.htm)
    * **住民税**: 以下の情報を参考にしています。
        * [税金・控除の計算方法まとめ](https://biz.moneyforward.com/tax_return/basic/49732/#1)
        * [住民税について（文京区）](https://www.city.bunkyo.lg.jp/b008/p000357.html#sonota)
    * **国民健康保険**: 文京区のウェブサイトを参考にしています。
        * [国民健康保険税（文京区）](https://www.city.bunkyo.lg.jp/b021/p000424.html)
    * **国民年金**: 日本年金機構のウェブサイトを参考にしています。
        * [国民年金前納](https://www.nenkin.go.jp/service/kokunen/hokenryo/zenno.html)
    * **給与所得控除**: 各種手当については、こちらの記事を参考にしています。
        * [従業員向けの給与手当とは？種類や導入するメリット・デメリットを解説](https://edenred.jp/article/employee-benefits/119/#chapter-7)
    * **その他**
        * [国保加入のタイミング](https://mynavi-ms.jp/magazine/detail/001339.html)

* **奨学金の雑所得に関する解説**: `241213_zatushotoku.ipynb` では、一部の奨学金が雑所得として扱われる場合の、給与所得との違いや確定申告の必要性について解説しています。

## 想定ユーザーとシナリオ

このプロジェクトは、特に以下の状況にある大学生・大学院生を主な対象としています。

* 文京区在住
* 39歳以下
* 独身の一人暮らし
* バイト先が1つ

## ファイル構成

* `README.md`: このファイル
* `241205_insei_tedori.ipynb`: 手取り計算シミュレーション
* `241213_zatushotoku.ipynb`: 奨学金の雑所得に関する解説
* `src/`: 各税金・控除の計算ロジックを実装したPythonスクリプト群

## 使い方

### A. Web アプリ（推奨）

ブラウザ上で収入を入力するだけでリアルタイムに手取りを確認できます。

```bash
git clone https://github.com/YoheiOhto/japanese_tax_for_student.git
cd japanese_tax_for_student
uv sync
uv run streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

**機能:**
- サイドバーで給与収入・雑所得・年金の支払い方法・iDeCo を入力
- 収入→手取りのウォーターフォールグラフ・支出割合の円グラフを表示
- 収入額を動かしたときの手取り変化（103万・130万・160万・201万の壁を表示）
- 2024〜2027年の年度別比較

### B. Python スクリプト（自分で回す場合）

1. このリポジトリをクローンします
2. `uv sync` で環境を構築します
3. `ohto_simulate.py` の末尾の `simulate_tax()` 呼び出し部分を自分の収入に書き換えて実行します

```bash
uv run python ohto_simulate.py
```

結果は `output/` ディレクトリに JSON・CSV で保存されます。

---

## 今後の機能拡張

以下の機能追加を検討しています。

* **居住地の柔軟な設定**: 文京区以外の市区町村に住むユーザーも利用できるよう、国民健康保険料の計算を汎用化します。
* **控除項目の追加**: 扶養控除、生命保険料控除、医療費控除などを追加し、より正確な手取り計算を可能にします。
* **計算結果の可視化**: 収入と手取り額の関係をグラフで表示し、視覚的な理解を助けます。（Web アプリに実装済み）
