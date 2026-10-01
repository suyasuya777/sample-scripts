# FastAPI 実務スキルマップ（SRE 視点版）

障害調査でアプリのコードを読んだときに「ここが原因だ」と言えるようになるための
教材です。API の作り方ではなく、**動いている API が壊れたときに何を疑うか**を扱います。

---

## 🗺 カテゴリ一覧

| # | カテゴリ | この章の問い |
|---|---|---|
| 01 | `lifecycle` | デプロイのたびに 502 が出るのはなぜか |
| 02 | `outbound` | 呼び出し先が遅いとき、自分も道連れになる構造をどう断つか |
| 03 | `observability` | 障害の最中に「どのリクエストが、どこで、どれだけ遅かったか」を特定できるか |
| 04 | `failure` | 4xx と 5xx の切り分けが、そのまま可用性 SLI の分母と分子になる |
| 05 | `async_pitfalls` | 「速くするため」に書いた非同期処理が、なぜ障害の原因になるのか |
| 06 | `runtime` | イメージと起動構成が、ロールバックの速さと障害時の挙動を決める |
| 07 | `integrated` | 01〜06 を1つのアプリに統合する（5日目の課題） |

---

## 📁 ディレクトリ構成

| カテゴリ | ファイル | 内容 |
|---|---|---|
| **01_lifecycle** | [`lifespan_basics/`](01_lifecycle/lifespan_basics/lifespan_basics.py) | 共有リソースの生成と破棄、起動時に疎通確認をしない理由 |
| | [`health_endpoints/`](01_lifecycle/health_endpoints/health_endpoints.py) | livez / readyz / startupz の分離、readiness に依存を含める判断 |
| | [`graceful_shutdown/`](01_lifecycle/graceful_shutdown/graceful_shutdown.py) | シャットダウン4段階、処理中リクエストの待機 |
| **02_outbound** | [`shared_client/`](02_outbound/shared_client/shared_client.py) | クライアントの生成場所、コネクションプール上限 |
| | [`timeout_layers/`](02_outbound/timeout_layers/timeout_layers.py) | connect/read/write/pool、階層の逆転チェック |
| | [`retry_backoff/`](02_outbound/retry_backoff/retry_backoff.py) | リトライ対象の選別、指数バックオフ＋ジッタ、リトライ予算 |
| | [`circuit_breaker/`](02_outbound/circuit_breaker/circuit_breaker.py) | Closed / Open / Half-Open の3状態 |
| | [`idempotency_key/`](02_outbound/idempotency_key/idempotency_key.py) | 非冪等処理を安全にリトライする |
| **03_observability** | [`request_id/`](03_observability/request_id/request_id.py) | X-Amzn-Trace-Id の受け取り、ContextVar、下流への伝搬 |
| | [`json_logging/`](03_observability/json_logging/json_logging.py) | 必須フィールド、request_id の自動差し込み、出力先の判断 |
| | [`access_log_middleware/`](03_observability/access_log_middleware/access_log_middleware.py) | try/finally、ヘルスチェック除外、XFF からのクライアントIP |
| | [`log_masking/`](03_observability/log_masking/log_masking.py) | ログに載せてはいけないもの、マスク関数 |
| | [`red_metrics/`](03_observability/red_metrics/red_metrics.py) | Rate / Errors / Duration、ヒストグラム、カーディナリティ |
| | [`tracing_otel/`](03_observability/tracing_otel/tracing_otel.py) | トレース・スパン・伝搬、ログ/メトリクスとの役割分担 |
| **04_failure** | [`exception_handlers/`](04_failure/exception_handlers/exception_handlers.py) | 統一エラー形式、未捕捉例外を外に出さず内に残す |
| | [`status_code_policy/`](04_failure/status_code_policy/status_code_policy.py) | ステータスコードの判断表、429 と Retry-After |
| | [`sli_error_budget/`](04_failure/sli_error_budget/sli_error_budget.py) | SLI 定義文、SLO からエラーバジェットを計算する |
| **05_async_pitfalls** | [`blocking_event_loop/`](05_async_pitfalls/blocking_event_loop/blocking_event_loop.py) | async def の中の同期処理、再現手順 |
| | [`sync_vs_async/`](05_async_pitfalls/sync_vs_async/sync_vs_async.py) | def と async def の使い分け、スレッドプールの上限 |
| | [`background_task_loss/`](05_async_pitfalls/background_task_loss/background_task_loss.py) | BackgroundTasks の寿命、キューへ逃がす判断 |
| | [`pool_sizing/`](05_async_pitfalls/pool_sizing/pool_sizing.py) | ワーカー数 × タスク数 × プール上限の検算 |
| **06_runtime** | [`docker/`](06_runtime/docker/) | マルチステージ、非 root、ダイジェスト指定、exec 形式の CMD |
| | [`signal_handling/`](06_runtime/signal_handling/signal_handling.py) | PID 1 問題、SIGTERM がアプリに届くかの確認 |
| **07_integrated** | [`app/`](07_integrated/app/) | 01〜06 を統合した動くアプリ |

各章のフォルダに `README.md` があり、その章の合格基準が入っています。

---

## 🚀 セットアップ

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

各サンプルの起動:

```bash
cd 01_lifecycle/graceful_shutdown
uvicorn graceful_shutdown:app --reload
```

スクリプトとして実行するもの（サーバ不要）:

```bash
python 02_outbound/timeout_layers/timeout_layers.py     # 階層の逆転チェック
python 03_observability/json_logging/json_logging.py    # ログ出力の確認
python 03_observability/log_masking/log_masking.py      # マスキングの確認
python 04_failure/sli_error_budget/sli_error_budget.py  # エラーバジェット計算
python 05_async_pitfalls/pool_sizing/pool_sizing.py     # 接続数の検算
```

統合アプリ:

```bash
cd 07_integrated
uvicorn app.main:app --port 8000 --timeout-graceful-shutdown 60
```

---

## 📅 5日間の割り当て

| 日 | 章 | 主な作業 | 成果物 |
|---|---|---|---|
| 1日目 | 01 | lifespan と health を直し、シャットダウン4段階を実装 | 動くシャットダウン処理 |
| 2日目 | 02 | クライアントを使い回す形に直し、バックオフとサーキットブレーカを実装 | 修正版 HTTP クライアント |
| 3日目 | 03 | リクエストID伝搬とアクセスログを整備し、`/metrics` を追加 | RED メトリクスの公開 |
| 4日目 | 04 + 05 | 例外ハンドラと SLI 定義、ブロッキングの再現実験 | SLI 定義文、実験メモ |
| 5日目 | 06 + 07 | Dockerfile の書き換え、全体を1つのアプリに統合 | 統合版アプリ一式 |

---

## 🔗 ネットワーク・セキュリティロードマップとの対応

12月に学んだ概念が、コードでどう現れるかを確認する構成です。重複ではなく往復です。

| ここで直すこと | ロードマップの項目 |
|---|---|
| クライアントを使い回す | 第1部1章 エフェメラルポート枯渇 / SNATポート枯渇 / コネクションプール |
| タイムアウトの階層 | 第1部5章 タイムアウトの階層設計、3章 504 |
| バックオフとジッタ | 第1部5章 リトライとサーキットブレーカ、リトライストーム |
| 冪等キー | 第1部3章 冪等性とリトライ |
| シャットダウン順序 | 第1部3章 502、5章 コネクションドレイニング |
| ヘルスチェック設計 | 第1部5章 ヘルスチェック設計 |
| 構造化ログ・アクセスログ | 第1部8章 ALBアクセスログ、ネットワーク可観測性 |
| プールサイズの検算 | 第1部1章 コネクションプール、9章 キャパシティ |

---

## 🔧 技術メモ

- **Python 3.11+ を前提**（`X | None` 記法、`asyncio.to_thread` を使用）
- **`JSONResponse` の引数順**: 第1引数は `content`。`JSONResponse(503, {...})` と
  書くと `status_code` に dict が入り `TypeError` になります。必ずキーワード指定で
- **未捕捉例外と ContextVar**: 未捕捉例外を処理する `ServerErrorMiddleware` は
  自作ミドルウェアより外側にあり、そこへ到達する頃には ContextVar が reset 済みです。
  `request.state` にも request_id を持たせて拾えるようにしています
  （`07_integrated/app/observability.py` と `errors.py` を参照）
- **ミドルウェアの順序**: 後から `add` したものが外側になります。リクエストIDは
  最も外側で採番したいので、`observability.install` を最後に呼びます
- **`@app.on_event`** は非推奨です。新規は `lifespan` を使ってください
  （`health_endpoints.py` のみ単体動作のため使用）
