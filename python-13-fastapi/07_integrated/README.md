# 07_integrated — 統合サンプル

01〜06 で個別に学んだものを、1つのアプリにまとめたものです。
**5日目はここを完成させることが目標**になります。

## なぜ統合するか

各章のサンプルは単体では動きますが、実際には互いに絡みます。

- lifespan の中で httpx クライアントを作る（01 × 02）
- リクエストIDを採番し、下流呼び出しのヘッダに載せる（03 × 02）
- シャットダウン時に readiness を落とし、処理中リクエストを数える（01 × 03）
- エラーレスポンスに request_id を含める（03 × 04）

バラバラのファイルのままだと、この噛み合いが見えません。

## 構成

```
app/
  main.py           エントリポイント。ミドルウェアの順序もここで決まる
  lifecycle.py      起動・ヘルスチェック・graceful shutdown      (01)
  http_client.py    共有クライアント・タイムアウト・リトライ         (02)
  observability.py  リクエストID・アクセスログ・RED メトリクス      (03)
  logging_setup.py  構造化ログ・マスキング                     (03)
  errors.py         統一エラー形式・未捕捉例外                  (04)
  context.py        ContextVar
```

## 起動と確認

```bash
pip install fastapi "uvicorn[standard]" httpx prometheus-client
uvicorn app.main:app --port 8000 --timeout-graceful-shutdown 60
```

| 確認したいこと | 手順 | 期待する結果 |
|---|---|---|
| リクエストIDの採番 | `curl -i localhost:8000/` | `x-request-id` が返る |
| IDの引き継ぎ | `curl -i -H 'x-request-id: mytest' localhost:8000/` | `mytest` が返る |
| 構造化ログ | 上記実行時の標準出力 | JSON 1行、`request_id` 入り |
| 未捕捉例外 | `curl -i localhost:8000/boom` | 500。本文に内部詳細が出ない。ログにはトレースが残る |
| メトリクス | `curl localhost:8000/metrics` | `http_requests_total` と `http_request_duration_seconds` |
| graceful shutdown | `/slow?seconds=15` を実行中に `kill -TERM <pid>` | `/slow` が完走し、shutdown 1/4〜4/4 が順に出る |

## ミドルウェアの順序

FastAPI では**後から追加したミドルウェアが外側**になります。
リクエストIDは最も外側で採番したいので、`observability.install` を最後に呼びます。
順序を逆にすると、アクセスログに `request_id` が入りません。

## 5日目の課題

1. 上の表の6項目をすべて自分で確認する
2. `06_runtime/docker/` の Dockerfile でこのアプリをコンテナ化する
3. コンテナ内で PID 1 が uvicorn であることを確認する
4. `docker compose stop` で graceful shutdown のログが最後まで出ることを確認する
5. `DRAIN_WAIT_SECONDS` と compose の `stop_grace_period` の関係を検算する
