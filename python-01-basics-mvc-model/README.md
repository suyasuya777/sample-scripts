# 🍽️ ranking_project 処理概要

## 🗺️ システム概要

レストランのランキングをCSVファイルで管理し、ロボットがユーザーと会話しながらレストランをおすすめするCLIアプリ。

---

## 📁 ディレクトリ・ファイル構成

```
ranking_project/
├── main.py                          # エントリーポイント
├── ranking.csv                      # ランキングデータ（永続化）
└── roboter/
    ├── controller/
    │   └── conversation.py          # 会話フロー制御
    ├── models/
    │   ├── robot.py                 # ロボットの振る舞い（メインロジック）
    │   └── ranking.py               # ランキングデータ操作
    ├── views/
    │   └── console.py               # テンプレート読み込み（表示担当）
    └── templates/
        ├── hello.txt                # 名前を聞くメッセージ
        ├── greeting.txt             # レストランをすすめるメッセージ
        ├── which_restaurant.txt     # 好きなレストランを聞くメッセージ
        └── good_by.txt              # 別れのメッセージ
```

## 📋 ファイル一覧

| ディレクトリ | ファイル名 | 説明 |
|---|---|---|
| ranking_project/ | [main.py](#mainpy--エントリーポイント) | エントリーポイント |
| | [ranking.csv](#rankingcsv--ランキングデータ永続化データ構造) | ランキングデータ（永続化） |
| roboter/controller/ | [conversation.py](#controllerconversationpy--会話フロー制御) | 会話フロー制御 |
| roboter/models/ | [robot.py](#modelsrobotpy--restaurantrobot-クラス) | ロボットの振る舞い（メインロジック） |
| | [ranking.py](#modelsrankingpy--rankingmodel-クラス) | ランキングデータ操作 |
| roboter/views/ | [console.py](#viewsconsolepy--テンプレート読み込み表示担当) | テンプレート読み込み（表示担当） |
| roboter/templates/ | [hello.txt](#テンプレートと変数) | 名前を聞くメッセージ |
| | [greeting.txt](#テンプレートと変数) | レストランをすすめるメッセージ |
| | [which_restaurant.txt](#テンプレートと変数) | 好きなレストランを聞くメッセージ |
| | [good_by.txt](#テンプレートと変数) | 別れのメッセージ |

---

## 🏗️ アーキテクチャ（MVC構成）

MVC は「各レイヤーが**何を知ってよいか／知ってはいけないか**」で責務を分ける考え方。一般論としての分割指針は次のとおり。

| レイヤー | 担当する責務 | 持ってはいけないもの |
|---|---|---|
| **Model** | 業務ロジック・データ・永続化（状態と業務ルール） | 画面表示・ユーザー入力（`print` / `input`）への依存 |
| **View** | 受け取ったデータの描画・整形のみ | 業務ロジック・状態（自分で計算や判断をしない） |
| **Controller** | 入力の受け取りと処理の交通整理（Model と View の仲介） | 業務ルールそのもの（肥大化させない） |

分割時に意識する原則：

1. **依存方向を一方向に保つ**。`Controller → Model / View` の向きだけにし、View は Model を参照しない／Model は View を知らない状態にする。
2. **ビジネスルールは Model に集約**する（並び替え・集計・保存など）。いわゆる「fat model, thin controller」。
3. **View は状態を持たない**。渡された値を文字列・画面に変換して出すだけにし、表示方法の差し替え（CLI → Web 等）が効くようにする。
4. **Controller は薄く保つ**。「次に何をするか」という順序制御に徹し、ロジックは Model に委ねる。

本プロジェクトへの当てはめ：

- **Model** = `RankingModel` … CSV の読み書き（永続化）、`get_most_popular()` の並び替え、`increment()` の集計という業務ルールを担当。表示も入力も知らない、教科書的な Model。
- **View** = `console.get_template()` … `templates/*.txt` を読み `string.Template` を返すだけ。状態もロジックも持たない純粋な表示担当。
- **Controller** = `conversation.talk_about_restaurant()` … `RestaurantRobot` を生成し `hello → recomend → ask → thank` の順に呼ぶだけの、薄い交通整理役。

> **厳密な MVC との差異（設計上の注意）**
> `models/robot.py` の `RestaurantRobot` は `models/` 配下に置かれているが、実際には `input()` でユーザー入力を受け取り、`console`（View）を直接呼び、会話の進行も担っている。これは純粋な Model ではなく、**Controller と Model/View をつなぐ中間層（プレゼンター／アプリケーションサービス）**に近い。
> より厳密に分けるなら、入力受付や会話フローの制御は Controller 側へ寄せ、`RestaurantRobot` は「`RankingModel` の操作」と「View の呼び出し」の調整役に専念させる整理になる。今回の規模では現状でも十分機能するが、**画面を Web 化する・自動テストを書く**段階になると、この入力／表示の責務が Model 寄りに混ざっている点が変更の起点になりやすい。

下図は実際の依存関係（呼び出しの向き）。

```
main.py
  └─→ controller/conversation.py   ← 処理の起点（Controllerレイヤー）
          └─→ models/robot.py      ← ビジネスロジック（Modelレイヤー）
                  ├─→ models/ranking.py    ← データ操作
                  └─→ views/console.py     ← 画面表示（Viewレイヤー）
                          └─→ templates/*.txt  ← メッセージテンプレート
```

---

## 🔄 処理フロー

```
START
  │
  ▼
① hello()
  └─ hello.txtテンプレートを表示
  └─ ユーザー名を入力させる（空文字の場合は再入力）
  │
  ▼
② recomend_restaurant()
  └─ ranking.csvから最もcountが高いレストランを取得
  └─ greeting.txtで「〇〇はどう？」と表示
  └─ y → ② 終了
  └─ n → 別のレストランを取得して再提示
        （おすすめ済みリストを除外して次の候補を選ぶ）
        候補がなくなったら終了
  │
  ▼
③ ask_user_favorite()
  └─ which_restaurant.txtでお気に入りを聞く
  └─ 入力されたレストラン名のcountを+1してCSVに保存
  │
  ▼
④ thank_you()
  └─ good_by.txtでお礼メッセージを表示
  │
  ▼
END
```

---

## 📄 Python ソース詳細

<a id="mainpy--エントリーポイント"></a>

### 🚪 `main.py` ─ エントリーポイント

**📥 インポートするモジュール**
```python
from roboter.controller import conversation
```


| 処理 | 内容 |
|------|------|
| `conversation.talk_about_restaurant()` を呼び出す | アプリのエントリーポイント |

---

<a id="controllerconversationpy--会話フロー制御"></a>

### 🎛️ `controller/conversation.py` ─ 会話フロー制御

**📥 インポートするモジュール**
```python
from roboter.models import robot
```


| 関数 | 内容 |
|------|------|
| `talk_about_restaurant()` | `RestaurantRobot` を生成し、4つのメソッドを順番に呼び出す |

---

<a id="modelsrobotpy--restaurantrobot-クラス"></a>

### 🤖 `models/robot.py` ─ `RestaurantRobot` クラス

**📥 インポートするモジュール**
```python
from roboter.models import ranking
from roboter.views import console
```


| メソッド | 内容 |
|----------|------|
| `__init__(name, user_name)` | ロボット名（デフォルト: `"Robo"`）、ユーザー名、`Ranking_Model` を初期化 |
| `hello()` | ユーザー名を入力させる。空文字はループで再入力 |
| `recomend_restaurant()` | 人気順でレストランを提案。`n` のたびに次の候補を提示し、おすすめ済みリストで重複を排除 |
| `ask_user_favorite()` | お気に入りレストランを入力させ、`ranking_model.increment()` でカウントアップ |
| `thank_you()` | お礼メッセージを表示して終了 |

---

<a id="modelsrankingpy--rankingmodel-クラス"></a>

### 📊 `models/ranking.py` ─ `RankingModel` クラス

**📥 インポートするモジュール**
```python
import collections  # defaultdict によるランキングデータの初期化
import csv          # DictReader / DictWriter による CSV 読み書き
import os           # os.path.abspath, os.path.join による CSV パス解決
```


| メソッド | 内容 |
|----------|------|
| `__init__(csv_file)` | CSVファイルパスを解決し、`defaultdict(int)` にデータを読み込む |
| `load_data()` | CSVを読み込み `{name: count}` 形式の辞書に格納 |
| `save()` | 辞書の内容をCSVに上書き保存 |
| `get_most_popular(not_list)` | countの降順でソートし、`not_list` に含まれないもので最上位の名前を返す |
| `increment(name)` | 指定レストランのcountを+1し、即座に `save()` |

---

<a id="viewsconsolepy--テンプレート読み込み表示担当"></a>

### 🖥️ `views/console.py` ─ テンプレート読み込み（表示担当）

**📥 インポートするモジュール**
```python
import os      # os.path.abspath, os.path.join によるテンプレートパス解決
import string  # string.Template によるプレースホルダー置換
```


| 関数 | 内容 |
|------|------|
| `get_template(template_file)` | `templates/` フォルダのテキストファイルを読み込み、`string.Template` オブジェクトで返す |

---

<a id="rankingcsv--ランキングデータ永続化データ構造"></a>

### 🗃️ `ranking.csv` ─ ランキングデータ（永続化）・データ構造

| カラム | 内容 |
|--------|------|
| `name` | レストラン名 |
| `count` | 推薦された回数（人気度スコア） |

```csv
name,count
osho,2
gast,1
sky,1
blue,1
```

---

<a id="テンプレートと変数"></a>

## 🧩 テンプレートと変数

| ファイル | 変数 | 用途 |
|----------|------|------|
| [`hello.txt`](roboter/templates/hello.txt) | `$robot_name` | ロボットの自己紹介＋名前入力プロンプト |
| [`greeting.txt`](roboter/templates/greeting.txt) | `$restaurant` | レストランのおすすめ文 |
| [`which_restaurant.txt`](roboter/templates/which_restaurant.txt) | `$user_name` | お気に入りレストランを聞く文 |
| [`good_by.txt`](roboter/templates/good_by.txt) | `$robot_name`, `$user_name` | お礼・別れのメッセージ |

テンプレートは `string.Template` の `substitute()` で変数を埋め込む方式。

---

## ⚠️ 注意点・気になる箇所

| 項目 | 内容 | 対応 |
|------|------|------|
| **保存タイミング** | `increment()` のたびに毎回 `save()` を呼ぶため、呼び出し頻度が高い場合はI/Oコストが増大する | 今回は対象外（設計判断） |


