# ── ビルドステージ ────────────────────────────────────
# ✅ ダイジェスト指定でベースイメージを固定する（タグは付け替えられる）
#    実運用では sha256 を書く。ここでは可読性のためタグ表記に留める。
#    例: FROM python:3.12-slim@sha256:xxxxxxxx AS builder
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
# wheel を作って実行ステージへ運ぶ。ビルドツールを最終イメージに残さない
RUN pip install --no-cache-dir --upgrade pip \
 && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ── 実行ステージ ──────────────────────────────────────
FROM python:3.12-slim

# ✅ 非 root ユーザを先に作る
RUN useradd --create-home --uid 10001 appuser

WORKDIR /app
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
 && rm -rf /wheels

COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000

# ✅ exec 形式。SIGTERM が uvicorn（PID 1）に直接届く
#    --timeout-graceful-shutdown は 01_lifecycle の待ち時間より長くする
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--timeout-graceful-shutdown", "60"]

# ── コンテナ側ヘルスチェックについて ──────────────────
# ECS では task definition の healthCheck で定義する。
# Dockerfile の HEALTHCHECK は ECS では使われないため、ここには書かない。
