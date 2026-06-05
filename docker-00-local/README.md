# 🐳 Docker イメージ作成 学習サンプル集

Dockerイメージ・コンテナ構築を体系的に学ぶためのサンプルコレクションです。  
OS基盤から本番運用に近いアプリケーション構成まで、段階的に学習できます。

---

## 📁 ディレクトリ構成

```
docker-samples/
├── os/
│   ├── debian/
│   ├── ubuntu/
│   ├── alpine/
│   └── amazonlinux2023/
├── database/
│   ├── mariadb-phpmyadmin/
│   ├── postgresql/
│   ├── postgresql-pgadmin4/
│   ├── mysql/
│   ├── mongodb/
│   └── redis-redisinsight/
├── webserver/
│   ├── nginx/
│   └── nginx-certbot/
├── language/
│   ├── ruby/
│   ├── python/
│   └── golang/
├── application/
│   ├── django/
│   ├── rails/
│   ├── php-apache-mariadb/
│   ├── springboot/
│   ├── flask/
│   ├── wordpress/
│   ├── fastapi/
│   ├── nodejs-express/
│   └── nextjs/
└── infra/
    ├── redis/
    ├── prometheus-grafana/
    └── nginx-fluentd/
```

---

## 🗂️ カテゴリ一覧

### 【OS基盤】

各Linuxディストリビューションの基礎的なDockerイメージを構築し、  
コンテナ内でのOS操作・パッケージ管理の違いを学習します。

| # | サンプル | 概要 | 難易度 |
|---|---------|------|--------|
| 1 | [Debianコンテナ](./os/debian/) | Debian最新版ベースの基本コンテナ | ⭐ |
| 2 | [Ubuntuコンテナ](./os/ubuntu/) | Ubuntu LTSベースの基本コンテナ | ⭐ |
| 3 | [Alpine Linuxコンテナ](./os/alpine/) | 軽量Alpine Linuxコンテナ（イメージサイズ最小化） | ⭐ |
| 4 | [Amazon Linux 2023コンテナ](./os/amazonlinux2023/) | AWS標準OS、ECS/Lambda互換環境 | ⭐ |

**学習ポイント:**
- `Dockerfile` の基本構文（`FROM`, `RUN`, `CMD`）
- パッケージマネージャの違い（`apt` / `apk` / `dnf`）
- イメージサイズの最適化手法

---

### 【データベース】

各種データベースエンジンのコンテナ化と、管理UIとの連携構成を学習します。

| # | サンプル | 概要 | 難易度 |
|---|---------|------|--------|
| 5 | [MariaDB + phpMyAdminコンテナ](./database/mariadb-phpmyadmin/) | MariaDB + Web管理画面のDocker Compose構成 | ⭐⭐ |
| 6 | [PostgreSQLコンテナ](./database/postgresql/) | PostgreSQL単体コンテナ＋初期化スクリプト | ⭐ |
| 7 | [PostgreSQL + pgAdmin4コンテナ](./database/postgresql-pgadmin4/) | PostgreSQL + GUI管理ツールの連携構成 | ⭐⭐ |
| 8 | [MySQLコンテナ](./database/mysql/) | MySQL単体コンテナ＋ボリューム永続化 | ⭐ |
| 9 | [MongoDBコンテナ](./database/mongodb/) | NoSQLドキュメントDBコンテナ | ⭐⭐ |
| 10 | [Redis + RedisInsightコンテナ](./database/redis-redisinsight/) | Redis KVS + GUI管理ツールの連携構成 | ⭐⭐ |

**学習ポイント:**
- `docker-compose.yml` による複数コンテナ連携
- 名前付きボリューム（Named Volume）によるデータ永続化
- 環境変数（`environment`）を使った設定注入
- ヘルスチェック（`healthcheck`）の設定

---

### 【Webサーバー】

Nginxを中心としたWebサーバーコンテナの構築と、SSL/TLS対応を学習します。

| # | サンプル | 概要 | 難易度 |
|---|---------|------|--------|
| 11 | [Nginxコンテナ](./webserver/nginx/) | 静的ファイル配信・リバースプロキシ設定 | ⭐⭐ |
| 12 | [Nginx + Certbot（SSL）コンテナ](./webserver/nginx-certbot/) | Let's Encrypt証明書自動取得・更新 | ⭐⭐⭐ |

**学習ポイント:**
- `nginx.conf` のカスタマイズと`COPY`命令
- リバースプロキシ設定（バックエンドコンテナへの転送）
- Let's Encrypt + Certbot による本番SSL対応
- コンテナ間通信（`depends_on`, `networks`）

---

### 【言語単体】

各プログラミング言語のランタイムコンテナを構築し、  
開発環境のDockerization基礎を学習します。

| # | サンプル | 概要 | 難易度 |
|---|---------|------|--------|
| 13 | [Rubyコンテナ](./language/ruby/) | Ruby実行環境・バージョン管理 | ⭐ |
| 14 | [Pythonコンテナ](./language/python/) | Python実行環境・pipパッケージ管理 | ⭐ |
| 15 | [Golangコンテナ](./language/golang/) | Goビルド環境・マルチステージビルド | ⭐⭐ |

**学習ポイント:**
- `官公式イメージ` のバージョン指定（`ruby:3.3-slim`等）
- `requirements.txt` / `go.mod` を使った依存関係管理
- マルチステージビルドによるイメージサイズ最適化（Go）
- `.dockerignore` の活用

---

### 【アプリケーション】

実際のWebフレームワーク・CMSをコンテナ化し、  
アプリケーション層のDocker構成パターンを学習します。

| # | サンプル | 構成 | 難易度 |
|---|---------|------|--------|
| 16 | [Djangoコンテナ](./application/django/) | Django + PostgreSQL + Nginx | ⭐⭐⭐ |
| 17 | [Ruby on Railsコンテナ](./application/rails/) | Rails + PostgreSQL + Redis | ⭐⭐⭐ |
| 18 | [PHP + Apache + MariaDBコンテナ](./application/php-apache-mariadb/) | LAMPスタック構成 | ⭐⭐ |
| 19 | [Spring Bootコンテナ](./application/springboot/) | Spring Boot + MySQL + マルチステージビルド | ⭐⭐⭐ |
| 20 | [Flaskコンテナ](./application/flask/) | Flask + PostgreSQL + Gunicorn | ⭐⭐ |
| 21 | [WordPressコンテナ](./application/wordpress/) | WordPress + MySQL + Nginx | ⭐⭐ |
| 22 | [FastAPIコンテナ](./application/fastapi/) | FastAPI + PostgreSQL + Uvicorn | ⭐⭐ |
| 23 | [Node.js（Express）コンテナ](./application/nodejs-express/) | Express + MongoDB | ⭐⭐ |
| 24 | [Next.js（React静的）コンテナ](./application/nextjs/) | Next.js静的エクスポート + Nginx配信 | ⭐⭐⭐ |

**学習ポイント:**
- アプリケーション層 + DB層の分離構成
- `entrypoint.sh` によるコンテナ起動処理の制御
- `db:migrate` 等の初期化処理の自動化
- 本番向け設定（`DEBUG=False`, Gunicorn/Uvicorn等）
- マルチステージビルド（Javaバイナリ, Reactビルド成果物）

---

### 【インフラ・運用】

モニタリング・ログ収集など、本番運用に必要なインフラ基盤をコンテナで構築します。

| # | サンプル | 概要 | 難易度 |
|---|---------|------|--------|
| 25 | [Redis（単体）コンテナ](./infra/redis/) | Redisキャッシュ・セッション管理用単体構成 | ⭐ |
| 26 | [Prometheus + Grafanaコンテナ](./infra/prometheus-grafana/) | メトリクス収集・可視化ダッシュボード | ⭐⭐⭐ |
| 27 | [Nginx + Fluentd（ログ収集）コンテナ](./infra/nginx-fluentd/) | アクセスログの収集・集約パイプライン | ⭐⭐⭐ |

**学習ポイント:**
- `prometheus.yml` によるスクレイプ設定
- Grafana DataSource・Dashboardの自動プロビジョニング
- Fluentdによるログルーティング・フォーマット変換
- コンテナ間のログ受け渡し（`logging` ドライバー）

---

## 🛠️ 前提環境

| ツール | 推奨バージョン |
|--------|--------------|
| Docker Engine | 24.x 以上 |
| Docker Compose | v2.x 以上（`docker compose` コマンド） |
| OS | Linux / macOS / Windows（WSL2推奨） |

### インストール確認

```bash
docker --version
# Docker version 24.x.x

docker compose version
# Docker Compose version v2.x.x
```

---

## 🚀 クイックスタート

各サンプルディレクトリで以下のコマンドを実行します。

```bash
# 例: FastAPIコンテナの起動
cd application/fastapi

# コンテナビルド＆起動（バックグラウンド）
docker compose up -d --build

# ログ確認
docker compose logs -f

# コンテナ停止・削除
docker compose down

# ボリュームも含めて削除
docker compose down -v
```

---

## 📚 学習推奨順序

段階的にスキルを積み上げるための推奨学習パスです。

```
Step 1【OS基盤】
  Debian → Ubuntu → Alpine → Amazon Linux 2023
      ↓
Step 2【言語単体】
  Python → Ruby → Golang
      ↓
Step 3【データベース】
  MySQL → PostgreSQL → MongoDB → Redis
      ↓
Step 4【Webサーバー】
  Nginx → Nginx + Certbot
      ↓
Step 5【アプリケーション（シンプル）】
  Flask → FastAPI → Node.js(Express)
      ↓
Step 6【アプリケーション（フルスタック）】
  Django → Rails → Next.js → WordPress
      ↓
Step 7【インフラ・運用】
  Redis単体 → Prometheus+Grafana → Nginx+Fluentd
```

---

## 📝 各サンプルの構成

各ディレクトリは以下の構成を基本とします。

```
<sample>/
├── Dockerfile          # イメージ定義
├── docker-compose.yml  # 複数コンテナ構成（該当する場合）
├── .env.example        # 環境変数サンプル
├── config/             # 設定ファイル群
│   └── *.conf
└── README.md           # サンプル個別説明
```

---

## ⚡ よく使うDockerコマンド

```bash
# イメージ一覧
docker images

# 起動中コンテナ確認
docker ps

# コンテナへのシェル接続
docker exec -it <container_name> bash

# イメージ・コンテナ・ボリュームの一括クリーンアップ
docker system prune -a --volumes

# ビルドキャッシュなしで再ビルド
docker compose build --no-cache
```

---

## 🔗 参考リソース

- [Docker 公式ドキュメント](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Docker Compose リファレンス](https://docs.docker.com/compose/compose-file/)
- [Dockerfile ベストプラクティス](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

---

## 📌 注意事項

- 本サンプルは学習目的のため、**本番環境への直接適用は非推奨**です
- パスワード・シークレットは `.env.example` を参考に `.env` を作成して管理してください
- `.env` ファイルは `.gitignore` に追加し、リポジトリへのコミットを避けてください

---

<div align="center">

**Happy Dockerizing! 🐋**

</div>
