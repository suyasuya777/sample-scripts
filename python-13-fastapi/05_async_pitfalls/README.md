# 05_async_pitfalls — 非同期処理の落とし穴

**この章の問い**: 「速くするため」に書いた非同期処理が、なぜ障害の原因になるのか。

| ファイル | 学ぶこと |
|---|---|
| `blocking_event_loop/` | async def の中の同期処理、再現手順 |
| `sync_vs_async/` | def と async def の使い分け、スレッドプールの上限 |
| `background_task_loss/` | BackgroundTasks の寿命、キューへ逃がす判断 |
| `pool_sizing/` | ワーカー数 × タスク数 × プール上限の検算 |

この章の3つはいずれも「エラーが出ない障害」です。ログにもメトリクスにも
異常が出ず、レイテンシだけが伸びます。知らなければ原因にたどり着けません。

## 実行

```bash
python pool_sizing/pool_sizing.py      # 接続数の検算
```

## 合格基準

- [ ] `blocking_event_loop.py` を起動し、ブロッキングが他リクエストに波及することを実際に観測した
- [ ] async def と def の使い分け基準を言える
- [ ] スレッドプールが枯渇したときの症状を説明できる
- [ ] BackgroundTasks に載せてよい処理と、いけない処理を区別できる
- [ ] 担当システムの実値で「ワーカー数 × タスク数 × プール上限 ≦ max_connections」を検算した
