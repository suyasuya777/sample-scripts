"""
学習ポイント: pytestフィクスチャとconftest.pyの設計
- @pytest.fixture()        : テスト用の共通セットアップ/ティアダウンを定義
- scope                    : "function"(デフォルト) / "module" / "session" でライフサイクル制御
- conftest.py              : フィクスチャを複数テストファイルで共有する特別なファイル
- yield フィクスチャ        : yieldの前がsetup、後がteardown
- フィクスチャの依存関係    : フィクスチャが他のフィクスチャを引数に取れる

conftest.py に配置すべきフィクスチャ:
  - session_fixture  : テスト用DBセッション
  - user_fixture     : 認証済みユーザーモック
  - client_fixture   : TestClientインスタンス

実行: pytest pytest_fixtures_and_conftest.py -v
"""
import pytest

# ── スコープの違い ─────────────────────────────────────
@pytest.fixture(scope="function")  # デフォルト: テスト関数ごとに再生成
def function_scoped_resource():
    print("\n[setup] function scoped")
    yield {"data": "function_resource"}
    print("\n[teardown] function scoped")

@pytest.fixture(scope="module")    # モジュール内で1度だけ生成
def module_scoped_resource():
    print("\n[setup] module scoped")
    yield {"data": "module_resource"}
    print("\n[teardown] module scoped")

@pytest.fixture(scope="session")   # テストセッション全体で1度だけ生成
def session_scoped_resource():
    print("\n[setup] session scoped")
    yield {"data": "session_resource"}
    print("\n[teardown] session scoped")

# ── フィクスチャの依存関係 ────────────────────────────
@pytest.fixture()
def base_user():
    return {"user_id": 1, "username": "base_user"}

@pytest.fixture()
def admin_user(base_user):
    """base_user フィクスチャを拡張してadminユーザーを作成"""
    return {**base_user, "role": "admin"}

# ── テスト ────────────────────────────────────────────
def test_function_scope(function_scoped_resource):
    assert function_scoped_resource["data"] == "function_resource"

def test_module_scope(module_scoped_resource):
    assert module_scoped_resource["data"] == "module_resource"

def test_admin_user(admin_user):
    assert admin_user["role"] == "admin"
    assert admin_user["user_id"] == 1
