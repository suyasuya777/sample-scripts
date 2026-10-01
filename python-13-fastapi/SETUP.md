# 環境構築手順 — FastAPI 実務スキルマップ（SRE 視点版）

教材（71ファイル）を実際に動かすための手順。所要 15〜20分。
この手順は Python 3.12 で実行確認済み。

---

## 0. 前提

| 項目 | 内容 |
|---|---|
| Python | 3.11 以上（`X \| None` 記法と `asyncio.to_thread` を使用） |
| Docker | 06_runtime と 07 の5日目課題で必要。Docker Desktop または Docker Engine |
| OS | macOS / Linux / **WSL2**。素の Windows は非推奨（理由は 6 章） |
| ネットワーク | 02・03・07 の一部が `jsonplaceholder.typicode.com` を叩く |

依存パッケージは **4つだけ**（実際の import を全ファイル走査して確認済み）:
`fastapi` / `uvicorn[standard]` / `httpx` / `prometheus-client`

`tracing_otel.py` は OpenTelemetry のコードがコメントアウトされた読み物なので、
OTel のパッケージは入れなくても動く。

---

## 1. 教材を展開して requirements.txt を置く

教材の zip は**トップレベルのディレクトリを持たない**（`01_lifecycle/` 〜 `07_integrated/`
が zip のルートに直接入っている）。そのまま `unzip` するとホーム直下に7つ散らばるので、
展開先を `-d` で指定する。`sandbox.zip` は `sandbox/` ごと入るので同じ場所へ。

```bash
mkdir -p ~/fastapi-sre
unzip -q -o -d ~/fastapi-sre "/mnt/c/Users/<Windowsのユーザ名>/Downloads/fastapi.zip"
unzip -q -o -d ~/fastapi-sre "/mnt/c/Users/<Windowsのユーザ名>/Downloads/sandbox.zip"
cd ~/fastapi-sre
ls      # 01_lifecycle 〜 07_integrated と sandbox が並べばOK
```

**`requirements.txt` はリポジトリのルートに無い。実体は `06_runtime/docker/requirements.txt`。
ルートへコピーする。**

```bash
cp 06_runtime/docker/requirements.txt .
```

venv で使うためだけではない。`sandbox/Dockerfile.dev` が `COPY requirements.txt /tmp/...`
を実行し、**そのビルドコンテキストは教材のルート**（`context: ..`）なので、ここに
置いておかないと 7 章の `docker compose build` が失敗する。

（README 側に `pip install -r requirements.txt` という記述は無い。`07_integrated/README.md`
は4パッケージを直接並べた `pip install` を書いている。どちらでも入るものは同じ）

あわせてルートに `.dockerignore` を置く。次章で作る `.venv` がビルドコンテキストに
含まれると、7章の build が数分単位で遅くなる。

```bash
printf '.venv\n__pycache__\n.git\n' > .dockerignore
```

---

## 2. 仮想環境を作る

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows(PowerShell): .venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
```

確認:

```bash
python -c "import fastapi, httpx, prometheus_client, uvicorn; print('ok')"
```

---

## 3. サーバ不要のスクリプトで動作確認（ここまでで 1・2 日目の半分が動く）

```bash
python 02_outbound/timeout_layers/timeout_layers.py     # → 「逆転: 外部API(5s) <= DB(10s)」
python 04_failure/sli_error_budget/sli_error_budget.py  # → SLO ごとの許容ダウンタイム表
python 05_async_pitfalls/pool_sizing/pool_sizing.py     # → 使用見込み/利用可能とタスク上限
python 03_observability/json_logging/json_logging.py    # → JSON 1行ログ
python 03_observability/log_masking/log_masking.py      # → マスク済みの dict
```

5本とも実行確認済み。ここが通れば Python 環境の構築は完了。

---

## 4. 単体サンプルの起動

各サンプルは自分のディレクトリで `uvicorn <ファイル名>:app` で起動する。

```bash
cd 01_lifecycle/graceful_shutdown
uvicorn graceful_shutdown:app --port 8000 --timeout-graceful-shutdown 60
```

複数を同時に立てるときは `--port` をずらす（既定は全部 8000）。
`--reload` は SIGTERM の挙動が変わるので、**シャットダウン系の検証では付けない**。

---

## 5. 統合アプリ（07）の起動と確認

```bash
cd 07_integrated
uvicorn app.main:app --port 8000 --timeout-graceful-shutdown 60
```

README の6項目は、別ターミナルから以下で確認できる（すべて実行確認済み）:

```bash
curl -i localhost:8000/                             # x-request-id が返る
curl -i -H 'x-request-id: mytest' localhost:8000/   # mytest がそのまま返る
curl -i localhost:8000/boom                         # 500。本文に ValueError の詳細は出ない
curl -s localhost:8000/metrics | grep http_requests_total
curl -s localhost:8000/readyz                       # {"status":"ready","inflight":0}
```

graceful shutdown（6項目目）は、uvicorn の PID が要るので1つのシェルでまとめて実行する:

```bash
uvicorn app.main:app --port 8000 --timeout-graceful-shutdown 60 > /tmp/07.log 2>&1 &
PID=$!
sleep 3
curl -s "localhost:8000/slow?seconds=15" &
sleep 2
kill -TERM $PID
wait $PID
grep shutdown /tmp/07.log
```

期待される出力（実測値）:

```
shutdown 1/4 readiness -> 503
shutdown 2/4 drain wait done          ← 1/4 の 20秒後
shutdown 3/4 inflight drained         ← remaining=0, waited_s=0.0
shutdown 4/4 resources closed
```

`/slow` は `{"slept":15}` を返して完走する。**全体で 40秒前後**（実測38秒）。

**`shutdown 1/4` は SIGTERM の直後には出ない。** uvicorn は先に処理中リクエストの完走を
待ち、それから lifespan の shutdown に入る。上の例なら `/slow` が終わる t=18 秒あたりで
ようやく 1/4 が出るので、その前の十数秒は**ログが止まったように見える**が正常。

```
[t=5s]  SIGTERM 送信
[t=18s] shutdown 1/4 readiness -> 503     ← /slow の完走を待ってから
[t=38s] shutdown 2/4 drain wait done      ← 1/4 の20秒後
[t=38s] shutdown 3/4 / 4/4 → uvicorn 終了
```

`DRAIN_WAIT_SECONDS 20` + `INFLIGHT_WAIT_SECONDS 30` = 50秒は**最大値**で、処理中
リクエストがドレイン待機中に終わっていれば `waited_s=0.0` になるため 30秒は縮む。

### ここで引っかかる点

- **SIGTERM 後に `/readyz` を curl しても 503 は返らない**（接続拒否になる）。
  uvicorn は SIGTERM でリッスンソケットを先に閉じるため、①の「readiness を 503」は
  **ログでしか観測できない**。nginx 経由（7章）で叩いても、上流への接続が拒否される
  ので返るのは **502** で、503 ではない。**この 502 こそが 01-02「デプロイのたびに
  502 が出る」の再現**なので、503 を探すのではなく 502 を見て、コードは 503 を返す
  状態なのに外から見えないのはなぜか、を説明できる状態にする。
- **毎回 20秒待たされる**（01 の `graceful_shutdown.py` は `/slow` が固定10秒なので全体33秒）。`07_integrated/app/lifecycle.py` の
  `DRAIN_WAIT_SECONDS = 20.0` を一時的に `2.0` にすると検証が回しやすい。
  ただし 5日目の課題5（`stop_grace_period` との検算）では元の値に戻すこと。
- **`/downstream/{post_id}` は外部インターネットに出る**
  （`https://jsonplaceholder.typicode.com`）。社内 PC やプロキシ配下で塞がれている
  場合はここだけ失敗するので、7 章のダミー下流に向け先を差し替える。

---

## 6. Windows の場合の注意

`kill -TERM` が使えないため、**01・06・07 のシャットダウン検証が成立しない**。
Ctrl+C（SIGINT）でも lifespan の shutdown は動くが、教材が扱う SIGTERM とは
別の経路になる。以下のいずれかを推奨する。

1. WSL2 の Ubuntu 上に教材を置き、そこで venv を作る（いちばん素直）
2. すべて Docker の中で動かす（7 章の compose）

---

## 7. サンドボックス（任意・02 と 03 を深くやるなら推奨）

教材の下流は `jsonplaceholder.typicode.com` 固定で、**429 も 503 も無応答も返せない**。
リトライ・サーキットブレーカ・タイムアウトを実際に発火させるには、
こちらの都合で壊れる下流が要る。同梱の `sandbox/` がそれ。

```
<教材のルート>/
├── requirements.txt
├── 01_lifecycle/ ... 07_integrated/
└── sandbox/
    ├── docker-compose.yml
    ├── Dockerfile.dev
    ├── downstream/app.py     下流ダミー（遅延・500・429・無応答・障害注入）
    ├── drive.py              教材のリトライ／ブレーカを下流ダミーに対して動かす
    └── nginx/nginx.conf      ALB の代役
```

**ポート 8000 の衝突に注意**。衝突するのは `app` だけで、`downstream`（9001）と
`lb`（8080）はぶつからない。**`downstream` は上げっぱなしで構わない**（`lb` も同様で、
`app` が居ない間は 502 を返すだけ）。教材のサンプルを venv で動かす前に `app` を止める。

```bash
docker compose -f sandbox/docker-compose.yml stop app     # venv を使う前
docker compose -f sandbox/docker-compose.yml start app    # 戻すとき
```

`app` を `up -d --build` で作り直すと IP が変わり、`lb` が古い IP を掴んだままになる
ことがある。nginx がずっと 502 を返すなら `restart lb`。

起動:

```bash
docker compose -f sandbox/docker-compose.yml up --build
```

| 役割 | URL |
|---|---|
| 統合アプリ（直接） | http://localhost:8000 |
| 統合アプリ（ALB 代役 nginx 経由） | http://localhost:8080 |
| 下流ダミー | http://localhost:9001 |

### 下流ダミーでできること

```bash
curl localhost:9001/ok                        # 正常。受け取った x-request-id を返す
curl localhost:9001/slow?seconds=8            # read タイムアウト（5秒）の発火
curl localhost:9001/hang                      # 応答が返らない。read 未設定の怖さ
curl localhost:9001/status/503                # リトライ対象
curl localhost:9001/status/404                # リトライしてはいけない側
curl localhost:9001/throttle?retry_after=3    # 429 + Retry-After
curl -XPOST 'localhost:9001/control?outage=true'   # 以後ずっと 503（サーキットブレーカ用）
curl -XPOST 'localhost:9001/control?outage=false&fail_rate=0.5'  # 5割で失敗
```

### 教材のリトライとサーキットブレーカを動かす（`sandbox/drive.py`）

`retry_backoff.py` は関数、`circuit_breaker.py` はクラスだけで、**呼び出し側が無い**
（前者の `__main__` は掛け算の検算を表示するだけ）。`curl` で下流ダミーを叩いても
下流の応答が見えるだけで、教材のリトライやブレーカは動かない。呼び出し側が `drive.py`。

```bash
python sandbox/drive.py retry http://localhost:9001/status/503   # 3回で打ち切り（約0.9秒）
python sandbox/drive.py retry http://localhost:9001/status/404   # リトライせず即終了（0.1秒）
python sandbox/drive.py retry http://localhost:9001/throttle     # Retry-After に従い約4秒
python sandbox/drive.py retry "http://localhost:9001/slow?seconds=8"  # read 5秒×3で約16秒
python sandbox/drive.py breaker                                  # 3状態の一巡
```

`breaker` の実測出力:

```
 1〜4 失敗  state=closed  failures=1..4
 5    失敗  state=open                      ← threshold=5 で開く
 6〜7 遮断  state=open  (circuit open: call skipped)
 HALF_OPEN の試行が失敗 → state=open        ← 1回の失敗で即 OPEN に戻る
 成功 status=200 → state=closed             ← 下流復旧後
```

**できないこと**: `/echo` は受け取った値を返すだけで、`Idempotency-Key` による重複排除は
しない（`served_at` は毎回変わる）。冪等キーの確認は教材側の `idempotency_key.py` で行う。

```bash
uvicorn idempotency_key:app --port 8000
curl -XPOST localhost:8000/orders -H 'Idempotency-Key: k1' \
  -H 'Content-Type: application/json' -d '{"item_id":1,"quantity":2}'
# 同じキー・同じボディ → 同じ order_id / 同じキー・違うボディ → 409 / キー無し → 400
```

**外部（jsonplaceholder）に出るファイルは3つある。**塞がれている環境では、いずれも
呼び出し先を下流ダミーに書き換える。

| ファイル | 書き換え先 |
|---|---|
| `02_outbound/shared_client/shared_client.py` の `/posts/{post_id}` | `http://localhost:9001/ok` |
| `03_observability/request_id/request_id.py` の `/downstream` | `http://localhost:9001/ok` |
| `07_integrated/app/main.py` の `/downstream/{post_id}` | `http://localhost:9001/status/503`（リトライを走らせる場合） |

`03_observability/request_id/request_id.py` の `/downstream` については、
**例外で終わると `x-request-id` ヘッダも付かない**（ミドルウェアの後処理を通らないため）
ので、採番ロジックの不具合に見えてしまう点に注意。

`07_integrated/app/main.py` の URL を
`http://downstream:9001/status/503`（コンテナ内から）または
`http://localhost:9001/...`（venv から）に書き換えると、リトライが実際に走る。

### nginx（ALB 代役）でできること

- **XFF の連結**（03-07）: `curl -H 'X-Forwarded-For: 203.0.113.9' localhost:8080/`
  → アプリには `203.0.113.9, 172.x.x.x` が届く。**教材（`access_log_middleware.py` と
  `07_integrated/app/observability.py`）は `xff.split(",")[-1]` で右端＝直近のホップを
  採る**ので、ログの `client_ip` は `203.0.113.9` ではなく nginx の `172.x.x.x` になる。
  先頭はクライアントが好きに詐称できるため、信用するのは自分が追記した位置だけ、という判断
- **デプロイ時 502 の再現**（01-02）: `docker compose stop app` の最中に
  `curl localhost:8080/` を叩くと、nginx が 502 を返す様子が見える
- **アクセスログの突合**（03-03）: nginx のログに `req_id` と `trace`、
  アプリの JSON ログに `request_id` が出るので、同じ値で追えるか確認できる

---

## 8. 06_runtime のコンテナ化（5日目の課題2）

`06_runtime/docker/Dockerfile` は `COPY . .` を使うため、**ビルドコンテキストに
`app/` がある必要がある**。docker ディレクトリのままビルドしても 07 のアプリは入らない。
次のどちらかにする。なおこの compose も 8000 を公開するので、
**サンドボックスの `app` は止めておく**こと。

```bash
# 方法A: 07_integrated 側に Dockerfile を持ち込む（教材の意図に近い）
cp 06_runtime/docker/Dockerfile 06_runtime/docker/requirements.txt \
   06_runtime/docker/docker-compose.yml 07_integrated/
cd 07_integrated
docker compose build && docker compose up -d

# 方法B: コンテキストだけ 07 に向ける
docker build -f 06_runtime/docker/Dockerfile -t sre-sample 07_integrated/
```

確認（README の課題3・4）:

```bash
docker compose exec app cat /proc/1/cmdline | tr '\0' ' '   # PID 1 が uvicorn であること
docker compose stop                          # shutdown 1/4〜4/4 が最後まで出ること
docker compose logs app | grep shutdown
```

**`ps` は使えない。** 教材の Dockerfile が使う `python:3.12-slim` には procps が入って
いないため、README の `ps -eo pid,comm` は `executable file not found` になる。
`/usr/local/bin/python /usr/local/bin/uvicorn ...` と出れば OK、`/bin/sh -c ...` なら NG。
なお `sandbox/Dockerfile.dev` には procps を入れてあるので、サンドボックス側では `ps` が使える。

課題5の検算: `DRAIN_WAIT_SECONDS 20` + `INFLIGHT_WAIT_SECONDS 30` = 50秒 <
`stop_grace_period: 90s` < Fargate の stopTimeout 上限 120秒。成立している。

---

## 9. この環境では確認できないもの

演習95問のうち約12問は AWS 実機でないと体感できない。ローカルは代役まで。

| 論点 | ローカルでできること | 実機が要る理由 |
|---|---|---|
| 登録解除遅延・ヘルスチェック間隔 | ログで4段階を見る | ALB のターゲット状態遷移は nginx では作れない |
| SNAT ポート枯渇 / ErrorPortAllocation | `ss -s` で接続数は見える | NAT Gateway のメトリクスが必要 |
| ALB アイドルタイムアウトと 502 | nginx の `keepalive_timeout` で近似 | ALB 固有の挙動は実機でしか出ない |
| X-Amzn-Trace-Id | nginx で模擬ヘッダを付与 | ALB が採番する本物ではない |
| ALB アクセスログとの突合 | nginx ログで代用 | S3 出力の項目は ALB 固有 |

AWS 側は Terraform で ALB + Fargate + NAT Gateway を立て、
検証が終わったら destroy する運用を推奨（NAT Gateway の消し忘れに注意）。

---

## 10. 詰まったときの切り分け

| 症状 | 原因 |
|---|---|
| `ModuleNotFoundError: app` | `07_integrated` の中で `uvicorn app.main:app` を実行していない |
| shutdown ログが出ない | `--reload` 付き、またはシェル形式 CMD で SIGTERM が届いていない（06章） |
| `/downstream/1` や `/posts/1` が失敗する | 外部インターネットに出られない。7章の表の3ファイルをダミー下流へ差し替える |
| `TypeError` が `JSONResponse` で出る | 第1引数は `content`。`JSONResponse(503, {...})` は誤り（07-03 の論点） |
| `Address already in use` | サンドボックスの `app`、または別のサンプルが 8000 を掴んでいる。`docker compose -f sandbox/docker-compose.yml stop app`、または `--port` をずらす |
| ログの `client_ip` が nginx の IP になる | 仕様どおり。教材は XFF の右端を採る（7章） |
| nginx がずっと 502 | `app` を作り直して IP が変わった。`restart lb`（7章） |
| SIGTERM 後に 503 を探しても出ない | 仕様どおり。ログの `shutdown 1/4` で見る。外から見えるのは 502（5章） |
| `x-request-id` が返らない | `/downstream` が外部に出られず例外で終わっている。呼び出し先をダミーに差し替える（7章） |
| 冪等キーが効かない | 下流ダミーの `/echo` を叩いている。教材の `POST /orders` で確認する（7章） |
| `ps` が見つからない | 教材のイメージに procps が無い。`cat /proc/1/cmdline` を使う（8章） |
| build が異様に遅い | `.dockerignore` が無く `.venv` を送っている（1章） |
| `curl` してもリトライが走らない | 教材には呼び出し側が無い。`sandbox/drive.py` を使う（7章） |
