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

1.  このリポジトリをローカル環境にクローンします。
2.  Pythonの実行環境（Anacondaなど）をセットアップし、必要なライブラリをインストールします。
3.  Jupyter Notebookを開き、`241205_insei_tedori.ipynb` を実行します。
4.  ノートブック内の変数を自分の収入に合わせて変更することで、手取り額をシミュレーションできます。
