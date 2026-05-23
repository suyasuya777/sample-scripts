"""
rest_api_client.py - クライアント側のREST API処理

テスト用API: https://jsonplaceholder.typicode.com
"""

import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "https://jsonplaceholder.typicode.com"
TIMEOUT  = 5  # 秒


# ============================================================
# レスポンスの処理（共通）
# ============================================================
def print_response(res: requests.Response) -> None:
    """レスポンスの status_code / json / text を表示する。"""
    print(f"  status : {res.status_code}")
    try:
        print(f"  json   : {res.json()}")
    except ValueError:
        print(f"  text   : {res.text[:100]}")


# ============================================================
# 1. GETリクエスト
# ============================================================
def get_request() -> None:
    res = requests.get(f"{BASE_URL}/posts/1", timeout=TIMEOUT)
    print_response(res)


# ============================================================
# 2. GETリクエスト（クエリパラメータ）
# ============================================================
def get_with_params() -> None:
    params = {"userId": 1, "_limit": 3}
    res = requests.get(f"{BASE_URL}/posts", params=params, timeout=TIMEOUT)
    print(f"  url    : {res.url}")
    print_response(res)


# ============================================================
# 3. POSTリクエスト（jsonボディ）
# ============================================================
def post_request() -> None:
    payload = {"title": "新しい投稿", "body": "本文テキスト", "userId": 1}
    res = requests.post(f"{BASE_URL}/posts", json=payload, timeout=TIMEOUT)
    print_response(res)


# ============================================================
# 4. POSTリクエスト（フォームデータ）
# ============================================================
def post_form_request() -> None:
    form_data = {"username": "alice", "password": "secret"}
    res = requests.post(f"{BASE_URL}/posts", data=form_data, timeout=TIMEOUT)
    print_response(res)


# ============================================================
# 5. PUTリクエスト（全フィールド更新）
# ============================================================
def put_request() -> None:
    payload = {"id": 1, "title": "更新タイトル", "body": "更新本文", "userId": 1}
    res = requests.put(f"{BASE_URL}/posts/1", json=payload, timeout=TIMEOUT)
    print_response(res)


# ============================================================
# 6. DELETEリクエスト
# ============================================================
def delete_request() -> None:
    res = requests.delete(f"{BASE_URL}/posts/1", timeout=TIMEOUT)
    print(f"  status : {res.status_code}")  # 200


# ============================================================
# 7. リクエストヘッダーの設定
# ============================================================
def request_with_headers() -> None:
    headers = {
        "Content-Type" : "application/json",
        "Accept"       : "application/json",
        "X-Request-ID" : "abc-123",
    }
    res = requests.get(f"{BASE_URL}/posts/1", headers=headers, timeout=TIMEOUT)
    print_response(res)


# ============================================================
# 8. 認証 - Basic認証
# ============================================================
def basic_auth_request() -> None:
    res = requests.get(
        f"{BASE_URL}/posts/1",
        auth=HTTPBasicAuth("user", "password"),
        timeout=TIMEOUT,
    )
    print(f"  status : {res.status_code}")


# ============================================================
# 9. 認証 - Bearer Token
# ============================================================
def bearer_token_request() -> None:
    token = "your-access-token"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/posts/1", headers=headers, timeout=TIMEOUT)
    print(f"  status : {res.status_code}")


# ============================================================
# 10. タイムアウト・エラーハンドリング
# ============================================================
def request_with_error_handling(url: str) -> dict | None:
    """
    エラーハンドリング付きGETリクエスト。
    成功時はレスポンスのdictを返す。失敗時はNoneを返す。
    """
    try:
        res = requests.get(url, timeout=TIMEOUT)
        res.raise_for_status()          # 4xx / 5xx で例外を送出
        return res.json()

    except requests.exceptions.Timeout:
        print("  [Error] タイムアウト")
    except requests.exceptions.ConnectionError:
        print("  [Error] 接続エラー")
    except requests.exceptions.HTTPError as e:
        print(f"  [Error] HTTPエラー: {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  [Error] リクエストエラー: {e}")

    return None


# ============================================================
# 11. セッションの再利用（ヘッダー・認証を使い回す）
# ============================================================
def session_request() -> None:
    with requests.Session() as session:
        session.headers.update({
            "Authorization": "Bearer your-token",
            "Accept"       : "application/json",
        })
        # 同じセッションで複数リクエスト（接続を再利用）
        res1 = session.get(f"{BASE_URL}/posts/1",    timeout=TIMEOUT)
        res2 = session.get(f"{BASE_URL}/posts/2",    timeout=TIMEOUT)
        res3 = session.get(f"{BASE_URL}/comments/1", timeout=TIMEOUT)

    for label, res in [("post1", res1), ("post2", res2), ("comment", res3)]:
        try:
            print(f"  {label:<8}: {res.json()}")
        except ValueError:
            print(f"  {label:<8}: status={res.status_code}")

