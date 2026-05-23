# docker

FastAPI + PostgreSQL + pgAdmin の Docker 構成サンプルです。

## 起動手順

```bash
# 環境変数ファイルを作成
echo 'SECRET_KEY=your-secret-key-here' > .env

# コンテナを起動
docker compose up -d

# マイグレーション実行
docker compose exec app alembic upgrade head

# ログ確認
docker compose logs -f app
```

## アクセス先

- API: http://localhost:8000/docs
- pgAdmin: http://localhost:81
