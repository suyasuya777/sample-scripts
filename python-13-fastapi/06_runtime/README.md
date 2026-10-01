# 06_runtime — コンテナ化と実行環境

**この章の問い**: イメージと起動構成が、ロールバックの速さと障害時の挙動を決める。

| ファイル | 学ぶこと |
|---|---|
| `docker/Dockerfile` | マルチステージ、非 root、ダイジェスト指定、exec 形式の CMD |
| `docker/docker-compose.yml` | stop_grace_period、ヘルスチェック定義 |
| `signal_handling/` | PID 1 問題、SIGTERM がアプリに届くかの確認 |

## この章が 01_lifecycle と繋がる理由

01 で書いたシャットダウン処理は、SIGTERM が届いて初めて動きます。
`CMD` をシェル形式で書いていると sh が PID 1 になり、シグナルが転送されず、
シャットダウン処理は一切実行されません。**01 のコードが動かない原因の
大半がここ**です。

## ワーカー構成の方針

| 方式 | 利点 | 欠点 |
|---|---|---|
| 1コンテナ1プロセス（推奨） | タスク数で水平に伸ばせる。落ちた単位が明確 | コンテナ数が増える |
| gunicorn + 複数ワーカー | プロセス起動コストを分散できる | 1コンテナの障害範囲が広い。接続数が掛け算 |

ECS/Fargate では前者が素直です。CPU 割当を超えるワーカーを立てると
スロットリングでかえって遅くなります。

## 確認手順

```bash
cd docker
docker compose build
docker compose up -d
docker compose exec app ps -eo pid,comm    # PID 1 が uvicorn であること
docker compose stop                        # graceful shutdown のログが出ること
```

## 合格基準

- [ ] イメージサイズが起動時間とロールバック速度に効く理由を説明できる
- [ ] タグ指定とダイジェスト指定の違いを説明できる
- [ ] シェル形式の CMD で SIGTERM が届かない理由を説明できる
- [ ] コンテナ内で PID 1 を確認し、uvicorn であることを確かめた
- [ ] CPU 制限を超えるワーカー数を立てたときに何が起きるか説明できる
- [ ] 非 root で動かす Dockerfile を書き、起動を確認した
