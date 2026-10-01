# 03_observability — 観測可能性

**この章の問い**: 障害の最中に「どのリクエストが、どこで、どれだけ遅かったか」を特定できるか。

| ファイル | 学ぶこと |
|---|---|
| `request_id/` | X-Amzn-Trace-Id の受け取り、ContextVar、下流への伝搬 |
| `json_logging/` | 必須フィールド、request_id の自動差し込み、出力先の判断 |
| `access_log_middleware/` | try/finally、ヘルスチェック除外、XFF からのクライアントIP |
| `log_masking/` | ログに載せてはいけないもの、マスク関数 |
| `red_metrics/` | Rate / Errors / Duration、ヒストグラム、カーディナリティ |
| `tracing_otel/` | トレース・スパン・伝搬、ログ/メトリクスとの役割分担 |

この章が6章のうち最も重く、かつ既存サンプルに最も欠けている部分です。
`red_metrics` と `tracing_otel` は FastAPI というより SRE の中核領域で、
ここが薄いと SLI が作れず、SLO 運用に進めません。

## 実行に必要な追加パッケージ

```bash
pip install prometheus-client            # red_metrics
pip install opentelemetry-instrumentation-fastapi   # tracing（任意）
```

## 合格基準

- [ ] 構造化ログの必須フィールドを列挙できる
- [ ] ALB のアクセスログとアプリログを同じIDで突き合わせた経験がある
- [ ] 例外で終わったリクエストがログに残らない実装の危険性を説明できる
- [ ] アプリから CloudWatch へ直接送る方式が増やす failure mode を3つ挙げられる
- [ ] 平均レイテンシが正常でも p99 が悪化している状況を、数値例で説明できる
- [ ] `/metrics` を実装し、RED の3つを公開した
- [ ] ログ・メトリクス・トレースがそれぞれ何に強いかを言える
