"""
学習ポイント: Alembicによるマイグレーション管理
- alembic init migrations       : マイグレーション環境の初期化
- migrations/env.py             : target_metadata = Base.metadata を設定
- alembic revision --autogenerate -m "コメント" : モデル差分からスクリプト自動生成
- alembic upgrade head          : 最新マイグレーションを適用
- alembic downgrade -1          : 1つ前のバージョンに戻す
- down_revision チェーン        : マイグレーション適用順序の管理

マイグレーション実行手順:
    1. alembic init migrations
    2. migrations/env.py を編集: target_metadata = Base.metadata
    3. alembic.ini の sqlalchemy.url を設定
    4. alembic revision --autogenerate -m "create items table"
    5. alembic upgrade head
"""
# このファイルは実行コードではなく学習リファレンスです。
# 以下は migrations/env.py の主要部分の解説です。

MIGRATIONS_ENV_EXAMPLE = '''
# migrations/env.py の主要設定箇所

from models import Base  # 全モデルが登録されたBaseをimport
target_metadata = Base.metadata  # autogenerateに必要

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # マイグレーション後に接続を即解放
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
'''

VERSIONS_CHAIN_EXAMPLE = '''
# マイグレーション適用順序（down_revisionチェーン）
# f3d5adf85e9a (down_revision=None) ← 起点: itemsテーブル作成
#   ↓
# b8ca17099c7d (down_revision='f3d5adf85e9a') ← usersテーブル作成
#   ↓
# ff676fae4f35 (down_revision='b8ca17099c7d') ← saltカラム追加
#   ↓
# 5f1777586dbe (down_revision='ff676fae4f35') ← 外部キー追加（最新）
'''

if __name__ == "__main__":
    print("Alembicコマンド一覧:")
    commands = [
        "alembic init migrations              # 初期化",
        "alembic revision --autogenerate -m 'message'  # スクリプト生成",
        "alembic upgrade head                 # 最新に適用",
        "alembic downgrade -1                 # 1つ前に戻す",
        "alembic downgrade base               # 全て戻す",
        "alembic history                      # 履歴表示",
        "alembic current                      # 現在バージョン確認",
    ]
    for cmd in commands:
        print(f"  {cmd}")
