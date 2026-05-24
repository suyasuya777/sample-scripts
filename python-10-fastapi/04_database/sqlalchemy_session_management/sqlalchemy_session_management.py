"""
学習ポイント: SQLAlchemyのDB接続・セッション管理
- create_engine    : DB接続エンジンの生成
- sessionmaker     : セッションファクトリ（autocommit=False / autoflush=False）
- declarative_base : 全ORMモデルが継承するベースクラス
- get_db()         : yieldジェネレーターによるセッション管理（try/finally）
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./sample.db"  # 本番ではPostgreSQL URLに変更
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    FastAPIのDependsで使用するジェネレーター。
    - autocommit=False: 明示的なcommit()が必要
    - autoflush=False : flush()を自動実行しない
    - try/finally     : 例外発生時もセッションを確実にクローズ
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── 接続確認 ─────────────────────────────────────────
if __name__ == "__main__":
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("DB接続成功:", result.fetchone())
