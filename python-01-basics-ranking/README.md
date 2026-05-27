# ranking_project 処理概要

## システム概要

レストランのランキングをCSVファイルで管理し、ロボットがユーザーと会話しながらレストランをおすすめするCLIアプリ。

---

## ディレクトリ構成

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

---

## アーキテクチャ（MVC構成）

```
main.py
  └─→ controller/conversation.py   ← 処理の起点（Controllerレイヤー）
          └─→ models/robot.py      ← ビジネスロジック（Modelレイヤー）
                  ├─→ models/ranking.py    ← データ操作
                  └─→ views/console.py     ← 画面表示（Viewレイヤー）
                          └─→ templates/*.txt  ← メッセージテンプレート
```

---

## 処理フロー

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

## クラス・関数の詳細

### `main.py`

**インポートするモジュール**
```python
from roboter.controller import conversation
```


| 処理 | 内容 |
|------|------|
| `conversation.talk_about_restaurant()` を呼び出す | アプリのエントリーポイント |

---

### `controller/conversation.py`

**インポートするモジュール**
```python
from roboter.models import robot
```


| 関数 | 内容 |
|------|------|
| `talk_about_restaurant()` | `RestaurantRobot` を生成し、4つのメソッドを順番に呼び出す |

---

### `models/robot.py` ─ `RestaurantRobot` クラス

**インポートするモジュール**
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

### `models/ranking.py` ─ `RankingModel` クラス

**インポートするモジュール**
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

### `views/console.py`

**インポートするモジュール**
```python
import os      # os.path.abspath, os.path.join によるテンプレートパス解決
import string  # string.Template によるプレースホルダー置換
```


| 関数 | 内容 |
|------|------|
| `get_template(template_file)` | `templates/` フォルダのテキストファイルを読み込み、`string.Template` オブジェクトで返す |

---

### `ranking.csv` ─ データ構造

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

## テンプレートと変数

| ファイル | 変数 | 用途 |
|----------|------|------|
| `hello.txt` | `$robot_name` | ロボットの自己紹介＋名前入力プロンプト |
| `greeting.txt` | `$restaurant` | レストランのおすすめ文 |
| `which_restaurant.txt` | `$user_name` | お気に入りレストランを聞く文 |
| `good_by.txt` | `$robot_name`, `$user_name` | お礼・別れのメッセージ |

テンプレートは `string.Template` の `substitute()` で変数を埋め込む方式。

---

## 注意点・気になる箇所

| 項目 | 内容 | 対応 |
|------|------|------|
| **保存タイミング** | `increment()` のたびに毎回 `save()` を呼ぶため、呼び出し頻度が高い場合はI/Oコストが増大する | 今回は対象外（設計判断） |


