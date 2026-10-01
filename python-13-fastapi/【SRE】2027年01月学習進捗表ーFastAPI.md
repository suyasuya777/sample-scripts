# FastAPI（SRE視点）学習進捗表

対象期間：2027/1/15（金）〜 1/31（日）。土曜を除く **全14日**（うち予備日1日）

教材：
- **アプリ** … `【SRE】FastAPI演習.html`（7ジャンル・95問）
- **教材本体** … `FastAPI 実務スキルマップ（SRE 視点版）`（全7カテゴリ・21サンプル・合格基準44項目＝各章 README の33項目＋07の課題11項目）
- **環境構築手順** … `SETUP.md`（10章。1/15 の準備はこれに沿って進める）
- **サンドボックス** … `sandbox/`（下流ダミー＋ALB代役の nginx。02・03 の実機作業で使う）

想定時間：平日 45〜75分／日曜 2時間。日曜が3日（1/17・1/24・1/31）あるので、重い章はそこに置いています。

---

## タスク種別のラベル

| ラベル | 作業の中身 | 開くもの |
|---|---|---|
| **【アプリ】** | 四択を解く。指定の出題パターンで回す | アプリ（Windows のブラウザ） |
| **【実機】** | サンプルコードを動かし、挙動を自分の目で見る | WSL2 の Ubuntu |
| **【実装】** | サンプルに手を入れる／自分で書く（語尾が「実装した」「書いた」の項目） | エディタ ＋ WSL2 |
| **【調査】** | 担当システムの実値を調べ、表を埋める・検算する | マネジメントコンソール／AWS CLI |
| **【メモ】** | その日の結果を1行で記録する | 記録用ファイル |
| **【記録】** | 「学習成績」から JSON を書き出して保管する | アプリ |

---

## 実行環境：Windows ＋ WSL2（Ubuntu）

コマンド系の作業は、**すべて WSL2 の Ubuntu 上で実行します。** PowerShell やコマンドプロンプトは使いません。

| 用途 | 使う場所 |
|---|---|
| アプリ（`【SRE】FastAPI演習.html`） | Windows のブラウザ |
| Python・uvicorn・curl・kill | WSL2 の Ubuntu |
| Docker | Docker Desktop（WSL2 バックエンド）を、WSL2 の Ubuntu から操作する |
| 教材の置き場所 | WSL2 側のホーム（例：`~/fastapi-sre/`）。`/mnt/c/...` 配下には置かない |
| 担当システムの実値の取得 | AWS マネジメントコンソール、または WSL2 に入れた AWS CLI |

### ディレクトリ構成（1/15 でこの形にする）

```
~/fastapi-sre/
├── requirements.txt          ← 06_runtime/docker/ からコピーする（ルートには無い）
├── 01_lifecycle/ … 07_integrated/
├── SETUP.md
└── sandbox/
    ├── docker-compose.yml    app / downstream / lb（nginx）の3サービス
    ├── Dockerfile.dev
    ├── downstream/app.py     下流ダミー（遅延・500・429・無応答・障害注入）
    └── nginx/nginx.conf      ALB の代役
```

| 役割 | URL |
|---|---|
| 統合アプリ（直接） | http://localhost:8000 |
| 統合アプリ（ALB 代役 nginx 経由） | http://localhost:8080 |
| 下流ダミー | http://localhost:9001 |

### サンドボックスと venv の使い分け（ポート 8000 の衝突に注意）

**衝突するのは `app` だけです。** `app` は 8000 を公開し、教材のサンプルも既定が 8000 なので、両方を同時に上げると `Address already in use` になります。`downstream`（9001）と `lb`（8080）はぶつからないので、**`downstream` は期間中ずっと上げっぱなしで構いません**（`lb` も上げたままでよく、`app` が無い間は 502 を返すだけです）。

覚えるのは1行です。**venv で教材のサンプルを動かす前に `app` を止める。**

```bash
docker compose -f sandbox/docker-compose.yml stop app      # venv を使う前
docker compose -f sandbox/docker-compose.yml start app     # 戻すとき
```

| 日 | `app` | `downstream` | `lb` |
|---|---|---|---|
| 1/17（疎通確認） | ○ | ○ | ○ |
| 1/21 | **×** | ○ | －（上げたままでも可） |
| 1/24 前半（サーバ3本） | **×** | ○ | － |
| 1/24 後半（XFF・突合） | **○** | ○ | **○** |
| 1/25・1/26・1/27 | **×** | ○ | － |
| 1/28（教材の compose を 07 側で使う） | **×** | ○ | － |
| 1/31 前半（venv）／中盤（07 の compose） | **×** | ○ | － |
| 1/31 後半（502 の再現） | **○** | ○ | **○** |

※`app` を `up -d --build` で作り直すと IP が変わり、`lb` が古い IP を掴んだままになることがあります。nginx がずっと 502 を返す場合は `docker compose -f sandbox/docker-compose.yml restart lb` で直ります。

### 環境まわりで先に知っておくこと（SETUP.md より）

1. **ルートに `requirements.txt` が無い。** 実体は `06_runtime/docker/requirements.txt`（4パッケージ）で、これをルートへコピーします。venv 用だけでなく、**`sandbox/Dockerfile.dev` がルートをビルドコンテキストにして `COPY requirements.txt` するため**、置いていないとサンドボックスの build が失敗します
2. **`06_runtime/docker/` でそのまま `docker compose build` しても 07 のアプリは入らない。** `COPY . .` のビルドコンテキストに `app/` が無いため。1/15 の疎通確認は `sandbox/` 側で行い、教材の Dockerfile は 1/28 にコンテキストを直して使う
3. **SIGTERM 後の `/readyz` は 503 にならない。** uvicorn がリッスンソケットを先に閉じるため、直叩きは接続拒否、nginx 経由なら **502** になります。**503 はログの `shutdown 1/4` でしか観測できません。** そしてこの 502 こそが 01-02「デプロイのたびに 502 が出る」の再現です
4. **`ps` が使えるのはサンドボックスだけ。** 教材の Dockerfile（`python:3.12-slim`）には procps が入っていないため、PID 1 の確認は `cat /proc/1/cmdline` を使います。`sandbox/Dockerfile.dev` には procps を入れてあるので、そちらでは `ps` も使えます
5. **ルートに `.dockerignore` を置く。** `.venv` がビルドコンテキストに含まれると build が数分単位で遅くなります

### ローカル確認の可否の表記

各タスクに、PC のローカル環境（WSL2）だけで確認できるかどうかを付けています。

| 表記 | 意味 |
|---|---|
| 〔ローカル○〕 | PC（WSL2・ブラウザ）だけで確認できる |
| 〔ローカル△：〜〕 | サンドボックスで**近似**できる。本物（ALB・NAT GW）とは挙動が違う点を意識して見る |
| 〔ローカル×：〜〕 | 担当システムの実値や実環境が必要。「〜」に何が要るかを書いている |

---

# 第1期：1/15（金）〜 1/20（水）
## 【アプリ主体】全7ジャンル95問を1周 ─ 現在地の可視化

**この期は全項目〔ローカル○〕です。** 担当システムには触れません。

- □ **1/15（金）｜環境構築＋アプリ21問**　※**`SETUP.md` の 0〜3章・7章に沿って進める**
  - □ **【実機】** WSL2 を準備する（SETUP.md 0章・6章）
    - □ PowerShell（管理者）で `wsl --install -d Ubuntu-24.04`。入っていれば `wsl -l -v` で VERSION が 2 であることを確認
    - □ Ubuntu で `python3 --version` が 3.11 以上であることを確認（Ubuntu 22.04 は 3.10 なので 24.04 を使う）
    - □ `sudo apt update && sudo apt install -y python3-venv curl`
    - □ Docker Desktop の Settings → Resources → WSL integration で Ubuntu を有効にし、Ubuntu から `docker version` が通ることを確認
  - □ **【実機】** 教材とサンドボックスを配置する（SETUP.md 1章）
    - □ 教材の zip を `~/fastapi-sre/` に展開する（`/mnt/c/...` には置かない）。**`fastapi.zip` はトップレベルのディレクトリを持たない**ので、展開先を `-d` で指定しないとホーム直下に7つ散らばります
      ```bash
      mkdir -p ~/fastapi-sre
      unzip -q -o -d ~/fastapi-sre "/mnt/c/Users/<ユーザ名>/Downloads/fastapi.zip"
      unzip -q -o -d ~/fastapi-sre "/mnt/c/Users/<ユーザ名>/Downloads/sandbox.zip"
      cd ~/fastapi-sre && ls    # 01_lifecycle 〜 07_integrated と sandbox が並べばOK
      ```
    - □ `sandbox/` が同じ階層にあることを確認する
    - □ `cp 06_runtime/docker/requirements.txt .` ← **ルートに無いので必ず先にコピー**
  - □ **【実機】** 依存を入れる（SETUP.md 2章）
    - □ `python3 -m venv .venv && source .venv/bin/activate`
    - □ `pip install -r requirements.txt`（fastapi / uvicorn[standard] / httpx / prometheus-client の4つ）
    - □ `python -c "import fastapi, httpx, prometheus_client, uvicorn; print('ok')"` が通る
  - □ **【実機】** サーバ不要の5本を流す（SETUP.md 3章。ここが通れば Python 環境は完成）
    - □ `python 02_outbound/timeout_layers/timeout_layers.py` → 「逆転: 外部API(5s) <= DB(10s)」
    - □ `python 04_failure/sli_error_budget/sli_error_budget.py` → SLO ごとの許容ダウンタイム表
    - □ `python 05_async_pitfalls/pool_sizing/pool_sizing.py` → 使用見込み／利用可能とタスク上限
    - □ `python 03_observability/json_logging/json_logging.py` → JSON 1行ログ
    - □ `python 03_observability/log_masking/log_masking.py` → マスク済みの dict
  - □ **【実機】** ルートに `.dockerignore` を作る（`printf '.venv\n__pycache__\n.git\n' > .dockerignore`）← 無いと `.venv` ごと送られて build が遅い
  - □ **【実機】** **`docker compose -f sandbox/docker-compose.yml build` を今日流しておく** ← ここが通らないと 1/28 と 1/31 が丸ごと潰れる
  - □ **【アプリ】** 01 ライフサイクル（11問）／出題パターン「全て」
  - □ **【アプリ】** 06 コンテナ化と実行環境（10問）／「全て」
  - ※旧版の `cd 06_runtime/docker && docker compose build` は、そのイメージに 07 のアプリが入らないため疎通確認になりません。**build の疎通は sandbox 側で取り、教材の Dockerfile は 1/28 にコンテキストを直して使います**
  - ※準備が溢れたらアプリの 06（10問）を 1/17 へ回し、環境構築を優先してください
- □ **1/17（日・2時間）｜アプリ21問＋サンドボックス疎通**
  - □ **【アプリ】** 02 外向き通信（21問）／「全て」
  - □ **【実機】** `docker compose -f sandbox/docker-compose.yml up -d` で3サービスを起動し、疎通を確認（10分）
    - □ `curl -s localhost:8000/readyz` → `{"status":"ready",...}`
    - □ `curl -s -o /dev/null -w '%{http_code}\n' localhost:8080/` → 200（nginx 経由）
    - □ `curl -s localhost:9001/ok` → `{"ok":true,...}`（下流ダミー）
  - □ **【実機】** 確認できたら `docker compose -f sandbox/docker-compose.yml stop` で落とす（8000 番を空けておく）
  - □ **【実機】** 1/15 で終わらなかった準備・アプリを片付ける
  - ※ここで 3つとも応答すれば、第2期の実機作業はすべて動きます
- □ **1/18（月）｜アプリ19問**
  - □ **【アプリ】** 03 観測可能性（19問）／「全て」
- □ **1/19（火）｜アプリ26問**
  - □ **【アプリ】** 04 失敗の表現（16問）／「全て」
  - □ **【アプリ】** 05 非同期処理の落とし穴（10問）／「全て」
- □ **1/20（水）｜アプリ8問＋記録＋2周目**
  - □ **【アプリ】** 07 統合アプリ（8問）／「全て」
  - □ **【メモ】** 「学習成績」のジャンル別ミス数を書き写す
  - □ **【記録】** JSON書き出し
  - □ **【アプリ】** 01・02 を「コンボを除く」で2周目（最大32問）← 1/21 の実機に備える

---

# 第2期：1/21（木）〜 1/28（木）
## 【実機主体・アプリは冒頭の潰し込み】手を動かす合格基準を☑にする

- □ **1/21（木）｜01 ライフサイクル ＋ 02 外向き通信（ローカルで動かす分）**
  - □ **【アプリ】**〔ローカル○〕 01・02 を「コンボを除く」でコンプリート
  - □ **【実機】**〔ローカル○〕 **下流ダミーだけ起動する**：`docker compose -f sandbox/docker-compose.yml up -d downstream`（`app` を上げると 8000 番が埋まって次が起動できない）
  - □ **【実機】**〔ローカル○〕 `uvicorn graceful_shutdown:app --port 8000` で起動する（`--reload` は付けない。付けると SIGTERM を受けるのがリロード監視側のプロセスになる）
  - □ **【実機】**〔ローカル○〕 **合格基準**：`graceful_shutdown.py` を起動し、`/slow` 実行中に SIGTERM を送って挙動を確認した（別ターミナルで `curl localhost:8000/slow &` の直後に `kill -TERM $(pgrep -f 'graceful_shutdown:app')`）
  - □ **【実機】**〔ローカル○〕 ②のドレイン待機中に `curl -i localhost:8000/readyz` を叩き、**503 ではなく接続拒否になる**ことを確認する（07-07 の論点）
  - □ **【実機】**〔ローカル○〕 上で 503 が返らない理由を、`shutdown 1/4 readiness -> 503` のログと突き合わせて説明できるようにする（コードは 503 を返す状態にしているが、受け口がもう閉じている）
  - □ **【実機】**〔ローカル○〕 `python 02_outbound/timeout_layers/timeout_layers.py` を実行
  - □ **【実機】**〔ローカル○〕 `shared_client.py` を起動して共有クライアントの形を読む　※**`/posts/{post_id}` は jsonplaceholder を叩きます。**外部に出られない環境では呼び出し先を `http://localhost:9001/ok` に書き換えてから起動してください（SETUP.md 7章の差し替え表）
  - □ **【実機】**〔ローカル○〕 下流ダミーに対して**教材のリトライを実際に走らせる**（`sandbox/drive.py`。実測値は右）
    - □ `python sandbox/drive.py retry http://localhost:9001/status/503` → 3回で打ち切り（約0.9秒。ジッタで毎回変わる）
    - □ `python sandbox/drive.py retry http://localhost:9001/status/404` → **リトライせず即座に** `HTTPStatusError`（0.1秒）
    - □ `python sandbox/drive.py retry http://localhost:9001/throttle` → `Retry-After: 2` に従うので約4秒（02-16）
    - □ `python sandbox/drive.py retry "http://localhost:9001/slow?seconds=8"` → read タイムアウト5秒 × 3回で約16秒
    - ※`retry_backoff.py` は関数だけで呼び出し側がありません（`__main__` は掛け算の検算を表示するだけ）。`curl` で叩いても下流の応答が見えるだけでリトライは走らないので、このドライバを使います
  - □ **【メモ】** シャットダウン4段階のログ、`/readyz` の直叩きと nginx 経由の違いを記録
  - ※シャットダウン実験は**1回あたり30秒前後**かかります（`/slow` の固定10秒 ＋ ドレイン待機20秒。実測33秒）。**`shutdown 1/4` は SIGTERM の直後には出ません。** uvicorn が処理中リクエストの完走を待ってから lifespan の shutdown に入るので、その間の十数秒はログが止まったように見えますが正常です。何度も回すなら `DRAIN_WAIT_SECONDS` を一時的に `2.0` に下げ、**1/31 の検算前に必ず戻す**こと。**同名の定数が2か所にあります**。この日に編集するのは `01_lifecycle/graceful_shutdown/graceful_shutdown.py`、1/31 に効くのは `07_integrated/app/lifecycle.py` です
  - ※`/slow` は引数を取らず固定10秒です（07 の `/slow?seconds=15` とは別物）
- □ **1/22（金）｜01・02（担当システムの実値を集める）**　※**この日は全項目〔ローカル×〕**
  - □ **【調査】**〔ローカル×：担当システムの ALB〕 ALB ヘルスチェック間隔 × 異常閾値
  - □ **【調査】**〔ローカル×：担当システムの ALB〕 ALB 登録解除遅延（deregistration delay）
  - □ **【調査】**〔ローカル×：担当システムのアプリ設定〕 アプリのドレイン待機 ＋ 処理中待機
  - □ **【調査】**〔ローカル×：担当システムの ECS タスク定義〕 ECS stopTimeout（Fargate 最大120秒）
  - □ **【調査】**〔ローカル×：上の実値〕 **合格基準**：アプリ所要時間 ＜ stopTimeout を検算し、逆転がないことを確認した
  - □ **【調査】**〔ローカル×：担当システムの依存構成〕 **合格基準**：readiness に DB 疎通を含めるべきかを、自分のシステムについて判断し理由を言える
  - □ **【調査】**〔ローカル×：クライアント・ALB・uvicorn・アプリ・外部API・DB の実値〕 **合格基準**：タイムアウト階層の表を担当システムの実値で埋め、逆転がないか確認した
  - □ **【調査】**〔ローカル×：担当システムの ALB と uvicorn の実値〕 uvicorn の Keep-Alive だけは **ALB の idle timeout より長い**ことを確認する（外側＞内側の例外）
  - □ **【メモ】** 噛み合わせ表とタイムアウト階層表を記録
  - ※1/21 に nginx 代役で挙動そのものは見ているので、この日は**数字を埋める作業に集中**できます。サンドボックスの値（nginx `keepalive_timeout 60s` / compose `stop_grace_period 90s`）を、担当システムの実値と並べて比べると差が見えます
- □ **1/24（日・2時間）｜03 観測可能性**
  - □ **【アプリ】**〔ローカル○〕 03 をコンプリート
  - ※**この日は前半と後半で環境が変わります。** 前半は 8000 番でサーバを3本順に立てるので `app` を止めておき（1本終わるごとに Ctrl+C）、後半の XFF と突合では逆に `app` と `lb` を上げます
  - □ **【実機】**〔ローカル○〕 `python 03_observability/json_logging/json_logging.py` を実行し、JSON 1行に `request_id` が入ることを確認（スクリプト。サーバ不要）
  - □ **【実機】**〔ローカル○〕 **1本目**：`request_id.py` を起動し、`curl -i -H 'X-Amzn-Trace-Id: Root=1-abc-def' localhost:8000/downstream` で `x-request-id: 1-abc-def` が返ることを確認（`Root=` は剥がされる）
    - ※`/downstream` は jsonplaceholder を叩きます。**外部に出られない環境では 500 になり、しかも `x-request-id` ヘッダも付きません**（例外時はミドルウェアの後処理を通らないため）。その場合は呼び出し先を `http://localhost:9001/ok` に書き換え、下流ダミーだけ起動して確認します
  - □ **【実機】**〔ローカル○〕 **2本目**：`access_log_middleware.py` を起動し、`/boom` を叩いて、例外で終わったリクエストもアクセスログに `status: 500` で残ることを確認
  - □ **【実機】**〔ローカル○〕 `python 03_observability/log_masking/log_masking.py` を実行（スクリプト。サーバ不要）
  - □ **【実機】**〔ローカル○〕 **3本目**：`red_metrics.py` を起動し、`/items/1` と `/items/2` を叩いて、ラベルが `/items/{item_id}` にまとまることを確認
  - □ **【実装】**〔ローカル○〕 **合格基準**：`/metrics` を実装し、RED の3つ（Rate / Errors / Duration）を公開した
    - ※`red_metrics.py` は完成形なので、動かすだけでは「実装した」になりません。**07 の `observability.py` 側に同じものが入っていることを読んで確かめる**か、自分で書き写すところまでやって☑にします
  - □ **【実機】** ここで3本目を止め、`docker compose -f sandbox/docker-compose.yml up -d`（`app` と `lb` を上げる）
  - □ **【実機】**〔ローカル△：nginx 代役〕 XFF の連結を見る（03-07）：`curl -H 'X-Forwarded-For: 203.0.113.9' localhost:8080/` → アプリには `203.0.113.9, 172.x.x.x` が届く
    - □ `docker compose -f sandbox/docker-compose.yml logs app` の `client_ip` が **`203.0.113.9` ではなく `172.x.x.x`（nginx）**になることを確認する。教材は `xff.split(",")[-1]`＝**右端（直近のホップ）**を採っている。自分が追記した位置だけが信用できる、という判断がコードに出ている箇所
    - ※本物の ALB でも同じく右端が ALB の1つ手前になります。CloudFront を前段に置くと段数が変わる点は 12/9 の論点と同じです
  - □ **【実機】**〔ローカル△：nginx 代役〕 突合の予行：nginx のアクセスログの `req_id` と、アプリの JSON ログの `request_id` を同じ値で追えることを確認する
  - □ **【調査】**〔ローカル×：ALB を通した環境と、その ALB アクセスログ（S3）〕 **合格基準**：ALB のアクセスログとアプリログを同じIDで突き合わせた経験がある
  - □ **【メモ】** `/metrics` の出力と、突き合わせに使ったクエリを記録
  - □ **【記録】** JSON書き出し
  - ※nginx 代役で手順は一通り踏めますが、**本物の ALB アクセスログは S3 にスペース区切りで出力され、項目も `trace_id`・`target_processing_time` など固有**です。合格基準の☑は実環境で突合したときに付けてください
- □ **1/25（月）｜04 失敗の表現（1回目）**
  - □ **【アプリ】**〔ローカル○〕 04 を「コンボを除く」で1回
  - □ **【実装】**〔ローカル○〕 **合格基準**：スタックトレースをレスポンスに漏らさず、ログには残す実装を書いた
  - □ **【実機】**〔ローカル○〕 `/boom` の本文に例外メッセージが出ず、ログに `exception` が出ることを確認
  - □ **【実機】**〔ローカル○〕 `/rate-limited` を `curl -i` で叩き、429 と `Retry-After: 30` を確認
  - □ **【実機】**〔ローカル○〕 下流ダミーの `curl -i 'localhost:9001/throttle?retry_after=3'` と見比べ、**429 を受けた側がどう振る舞うべきか**を確認（04-04）※`downstream` が上がっていること
- □ **1/26（火）｜04 SLI 定義文**
  - □ **【アプリ】**〔ローカル○〕 04 をコンプリート
  - □ **【実機】**〔ローカル○〕 `python 04_failure/sli_error_budget/sli_error_budget.py` を実行
  - □ **【調査】**〔ローカル×：担当システムの ALB・ターゲットグループ・SLO〕 **合格基準**：担当システムの SLI 定義文（6項目）を実際に書いた
  - □ **【調査】**〔ローカル×：担当システムの CloudWatch メトリクス〕 「成功」の定義と「計測」のメトリクスが対応しているか確認（ELB 自身の 5xx を数えるなら `HTTPCode_ELB_5XX_Count` も要る。04-15 の論点）
  - □ **【メモ】** SLI 定義文6項目を記録
  - □ **【記録】** JSON書き出し
- □ **1/27（水）｜05 非同期処理の落とし穴**
  - □ **【アプリ】**〔ローカル○〕 05 をコンプリート
  - □ **【実機】**〔ローカル○〕 **合格基準**：`uvicorn blocking_event_loop:app --workers 1` で起動し、ブロッキングが他リクエストに波及することを実際に観測した（`curl localhost:8000/blocking &` の直後に `time curl localhost:8000/sync-def`）
  - □ **【実機】**〔ローカル○〕 `/blocking` を `/non-blocking` に変えて、待たされないことも確認
  - □ **【実機】**〔ローカル○〕 `python 05_async_pitfalls/pool_sizing/pool_sizing.py` を実行
  - □ **【調査】**〔ローカル×：担当システムの DB の `SHOW max_connections` と ECS のタスク数〕 **合格基準**：担当システムの実値で「ワーカー数 × タスク数 × プール上限 ≦ max_connections」を検算した
  - □ **【メモ】** 観測したレイテンシの伸びと、検算の結果を記録
- □ **1/28（木）｜06 コンテナ化と実行環境**
  - □ **【アプリ】**〔ローカル○〕 06 をコンプリート
  - □ **【実機】**〔ローカル○〕 **教材の Dockerfile をビルドコンテキストごと直す**（SETUP.md 8章）← `06_runtime/docker/` には `app/` がないため、そのまま `up` すると `app.main:app` を読み込めず再起動を繰り返す
    - □ 方法A：`cp 06_runtime/docker/{Dockerfile,requirements.txt,docker-compose.yml} 07_integrated/` → `cd 07_integrated && docker compose up -d --build`
    - □ 方法B：`docker build -f 06_runtime/docker/Dockerfile -t sre-sample 07_integrated/`
  - □ **【実機】**〔ローカル○〕 **合格基準**：`docker compose exec app cat /proc/1/cmdline | tr '\0' ' '` で PID 1 が uvicorn であることを確かめた（`/usr/local/bin/python /usr/local/bin/uvicorn ...` なら OK、`/bin/sh -c ...` なら NG。`python:3.12-slim` には `ps` が入っていないため README の `ps -eo pid,comm` は使えない）
  - □ **【実機】**〔ローカル○〕 `docker compose stop` で graceful shutdown のログが出ることを確認（`docker compose logs app`）
  - □ **【実装】**〔ローカル○〕 **合格基準**：非 root で動かす Dockerfile を書き、起動を確認した（`docker compose exec app id` で uid=10001）
  - ※`sandbox/Dockerfile.dev` は**学習用の土台**（root・シングルステージ）で、この章の答えではありません。マルチステージ・非 root・exec 形式は教材側の Dockerfile で確認します

---

# 予備日：1/29（金）
## 【繰り越しの吸収】溢れた分をここで消化する

- □ **1/29（金）｜繰り越し**
  - □ **【調査】** 1/22・1/24・1/26・1/27 のローカル×項目のうち、未消化のものを消化する
  - □ **【アプリ】** コンプリートに届かなかった章を「コンボを除く」で回す
  - □ **【メモ】** それでも残った項目を、1/31 の締めへ送る
  - □ **【実機】**〔ローカル○〕 *繰り越しが無ければ*：下流ダミーで 02 の残りを発火させる
    - □ `python sandbox/drive.py breaker` でサーキットブレーカの一巡を追う（02-17）。`circuit_breaker.py` もクラスだけなので、呼び出し側はドライバ側にある
      - □ 失敗5回で `closed` → `open`、以降は呼び出し自体が `circuit open: call skipped` で遮断される
      - □ `recovery_seconds` 経過後の `half_open` での試行が失敗すると、**1回で `open` に戻る**
      - □ 下流を復旧させて待つと `closed` に戻る（ドライバが `/control` で自動的に戻します）
    - □ 冪等キーは**教材側**で確認する（下流ダミーの `/echo` は重複排除をしないので、これでは確認できない）。`uvicorn idempotency_key:app --port 8000` を起動し、
      - □ 同じキー・同じボディで2回 POST → 同じ `order_id` が返る
      - □ 同じキー・違うボディで POST → 409
      - □ `curl -XPOST localhost:8000/orders -H 'Idempotency-Key: k1' -H 'Content-Type: application/json' -d '{"item_id":1,"quantity":2}'`（`Idempotency-Key` が無いと 400）
    - □ 終わったら `curl -XPOST 'localhost:9001/control?outage=false'` で戻す

---

# 第3期：1/31（日）
## 【統合動作確認＋総ざらい】07 を通しで動かして締める

**この日は〔ローカル○〕と〔ローカル△〕だけです。**

- □ **1/31（日・2時間）｜07 統合アプリ＋総ざらい**
  - □ **【実機】** 準備：`07_integrated/app/lifecycle.py` の `DRAIN_WAIT_SECONDS` を 1/21 に下げたままなら **20.0 に戻す**（検算の前提が変わる）
  - ※**この日は環境が3回変わります。** ①前半＝venv の 07（`app` は止め、`downstream` は上げる）②中盤＝1/28 で作った `07_integrated/` の compose ③後半＝サンドボックス全部。いずれも 8000 番を使うので、**次に進む前に必ず前のものを止めます**
  - □ **【アプリ】** 07 をコンプリート
  - □ **【実機】** 確認表の6項目
    - □ `curl -i localhost:8000/` で `x-request-id` が返る
    - □ `curl -i -H 'x-request-id: mytest' localhost:8000/` で `mytest` が返る
    - □ 標準出力に JSON 1行、`request_id` 入りで出る
    - □ `curl -i localhost:8000/boom` が500。本文に内部詳細が出ず、ログにはトレースが残る
    - □ `curl localhost:8000/metrics` に `http_requests_total` と `http_request_duration_seconds`
    - □ `/slow?seconds=15` 実行中に `kill -TERM $(pgrep -f 'app.main:app')` → `/slow` が完走し、ログの `shutdown 1/4` 〜 `shutdown 4/4` が順に出る（`--reload` は付けずに起動）
  - □ **【実機】**〔ローカル○〕 `/downstream/{post_id}` の向け先を下流ダミー（`http://localhost:9001/status/503`）に差し替え、**リトライが3回で打ち切られること**を確認する。外部インターネットに出られない環境でもここが動く
  - □ **【実機】** ②中盤へ：venv の 07 を Ctrl+C で止め、`cd 07_integrated && docker compose up -d`（1/28 で置いた教材の compose）
  - □ **【実機】** 5日目の課題（1/28 でコンテナ化は済んでいる前提）
    - □ `06_runtime/docker/` の Dockerfile でこのアプリをコンテナ化した
    - □ コンテナ内で PID 1 が uvicorn であることを確認した（1/28 と同じ `cat /proc/1/cmdline`）
    - □ `docker compose stop` で graceful shutdown のログが最後まで出た
  - □ **【調査】** `DRAIN_WAIT_SECONDS` と compose の `stop_grace_period` の関係を検算した（07-08 の論点）
    - □ 20秒 ＋ 30秒 ＝ 50秒 ＜ `stop_grace_period: 90s` ＜ Fargate の stopTimeout 上限 120秒
  - □ **【実機】**〔ローカル△：nginx 代役〕 ③後半へ：`cd 07_integrated && docker compose stop` で中盤の環境を落とし、`docker compose -f sandbox/docker-compose.yml up -d` に切り替える
  - □ **【実機】**〔ローカル△：nginx 代役〕 `docker compose -f sandbox/docker-compose.yml stop app` の最中に `curl -i localhost:8080/readyz` を叩き、**503 ではなく 502 が返る**ことを確認する。1/21 でログに見た `shutdown 1/4 readiness -> 503` と、外から見える 502 のずれが 01-02 の答えそのもの
  - □ **【アプリ】** 全ジャンルを「コンボを除く」で回し、残りを潰す（**目標：95問すべてコンボ**）
  - □ **【記録】** JSON書き出し
  - □ **【メモ】** 引き継ぎメモを作る（下記4点。boto3 はこれを入力として始める）
    - □ `□` のまま残った合格基準の章と項目番号
    - □ ローカル×で確認できなかった実値と、その理由
    - □ 〔ローカル△〕で代用した項目（AWS 実機で再確認する候補：ALB アクセスログ突合、X-Amzn-Trace-Id、ALB アイドルタイムアウト、SNAT ポート枯渇）
    - □ 07 を自分で書き直すか、boto3 に進むかの判断（書き直すなら 07-06 の「下流の 404 が 500 になる」も直す）

---

## 環境が壊れたときの戻し方

| 症状 | 戻し方 |
|---|---|
| サンドボックスが起動しない | `docker compose -f sandbox/docker-compose.yml down` → `up -d --build` で作り直す。教材のコードはボリュームマウントなので消えない |
| 下流ダミーが常に 503 を返す | 1/29 の `control?outage=true` を戻し忘れている。`curl -XPOST 'localhost:9001/control?outage=false'` |
| `Address already in use` | サンドボックスの `app` が 8000 を掴んでいる。`docker compose -f sandbox/docker-compose.yml stop app`（使い分け表を参照） |
| `x-request-id` が返らない | `/downstream` が外部に出られず例外で終わっている。呼び出し先を `http://localhost:9001/ok` に差し替える |
| 冪等キーが効かない | 下流ダミーの `/echo` を叩いている。教材の `idempotency_key.py` の `POST /orders` で確認する |
| build が異様に遅い | `.dockerignore` が無く `.venv` を送っている |
| shutdown のログが出ない | `--reload` 付きで起動している、またはシェル形式の CMD で SIGTERM が届いていない（06章） |
| `ModuleNotFoundError: app` | `07_integrated` の中で `uvicorn app.main:app` を実行していない |
