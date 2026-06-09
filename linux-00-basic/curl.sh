#!/bin/bash
# ============================================================
# curl サンプル集 - SRE向け
# ============================================================

BASE_URL="http://httpbin.org"

# ============================================================
# 1. 基本的なGETリクエスト
# ============================================================
echo "=== 1. 基本 GET リクエスト ==="
curl -s https://httpbin.org/get | head -10

# ============================================================
# 2. HTTPステータスコードのみ確認
# ============================================================
echo ""
echo "=== 2. ステータスコードのみ表示 ==="
curl -s -o /dev/null -w "%{http_code}" https://httpbin.org/get
echo ""

# ============================================================
# 3. ヘルスチェック（成功/失敗を判定）
# ============================================================
echo ""
echo "=== 3. ヘルスチェック ==="
URL="https://httpbin.org/get"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
if [ "$STATUS" -eq 200 ]; then
    echo "✅ ヘルシー: $URL ($STATUS)"
else
    echo "⚠️  異常検知: $URL ($STATUS)"
fi

# ============================================================
# 4. レスポンスタイムの計測
# ============================================================
echo ""
echo "=== 4. レスポンスタイムの詳細計測 ==="
curl -s -o /dev/null -w "\
DNS解決時間:     %{time_namelookup}s\n\
TCP接続時間:     %{time_connect}s\n\
TLSハンドシェイク: %{time_appconnect}s\n\
最初のバイトまで:  %{time_starttransfer}s\n\
合計時間:        %{time_total}s\n\
ステータスコード:  %{http_code}\n\
" https://httpbin.org/get

# ============================================================
# 5. POSTリクエスト（JSONボディ）
# ============================================================
echo ""
echo "=== 5. POST リクエスト（JSON） ==="
curl -s -X POST https://httpbin.org/post \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "value": 123}' | python3 -m json.tool | head -15

# ============================================================
# 6. カスタムヘッダーの付与
# ============================================================
echo ""
echo "=== 6. カスタムヘッダーを付与 ==="
curl -s https://httpbin.org/headers \
  -H "X-Request-ID: abc-123" \
  -H "Authorization: Bearer mytoken" | python3 -m json.tool

# ============================================================
# 7. リダイレクトを追跡（-L）
# ============================================================
echo ""
echo "=== 7. リダイレクトを追跡 ==="
curl -s -L -o /dev/null -w "最終ステータス: %{http_code}\nリダイレクト回数: %{num_redirects}\n最終URL: %{url_effective}\n" \
  https://httpbin.org/redirect/2

# ============================================================
# 8. タイムアウトの設定（--connect-timeout / -m）
# ============================================================
echo ""
echo "=== 8. タイムアウト設定 ==="
curl -s \
  --connect-timeout 3 \
  --max-time 5 \
  -o /dev/null \
  -w "ステータス: %{http_code} / 合計時間: %{time_total}s\n" \
  https://httpbin.org/delay/1

# ============================================================
# 9. ファイルのダウンロード（-o / -O）
# ============================================================
echo ""
echo "=== 9. ファイルをダウンロード ==="
curl -s -o /tmp/downloaded.json https://httpbin.org/get
echo "ダウンロード完了: $(wc -c < /tmp/downloaded.json) bytes"

# ============================================================
# 10. レスポンスヘッダーを表示（-I / -v）
# ============================================================
echo ""
echo "=== 10. レスポンスヘッダーのみ表示 ==="
curl -s -I https://httpbin.org/get | head -15

# ============================================================
# 11. 基本認証
# ============================================================
echo ""
echo "=== 11. 基本認証（Basic Auth） ==="
curl -s -u user:passwd https://httpbin.org/basic-auth/user/passwd \
  | python3 -m json.tool

# ============================================================
# 12. プロキシ経由でのリクエスト
# ============================================================
echo ""
echo "=== 12. プロキシ設定（コマンド例） ==="
cat << 'HELP'
# HTTPプロキシ経由
curl -x http://proxy.example.com:8080 https://example.com

# 環境変数でプロキシ設定
export http_proxy=http://proxy.example.com:8080
export https_proxy=http://proxy.example.com:8080
curl https://example.com

# プロキシを除外するホストを指定
export no_proxy=localhost,127.0.0.1,internal.example.com
HELP

# ============================================================
# 13. 証明書検証をスキップ（-k）※開発・検証環境のみ
# ============================================================
echo ""
echo "=== 13. SSL証明書検証をスキップ（開発環境用） ==="
curl -s -k -o /dev/null -w "ステータス: %{http_code}\n" https://httpbin.org/get

# ============================================================
# 14. 実用例：複数エンドポイントの死活監視
# ============================================================
echo ""
echo "=== 14. 複数エンドポイントの死活監視 ==="
ENDPOINTS=(
    "https://httpbin.org/get"
    "https://httpbin.org/status/200"
    "https://httpbin.org/status/500"
)

for url in "${ENDPOINTS[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url")
    TIME=$(curl -s -o /dev/null -w "%{time_total}" --max-time 5 "$url")
    if [ "$STATUS" -ge 200 ] && [ "$STATUS" -lt 400 ]; then
        printf "✅ %-45s %s %.3fs\n" "$url" "$STATUS" "$TIME"
    else
        printf "⚠️  %-45s %s %.3fs\n" "$url" "$STATUS" "$TIME"
    fi
done

# ============================================================
# 15. 実用例：APIレスポンスをjqでパース
# ============================================================
echo ""
echo "=== 15. APIレスポンスを jq でパース ==="
curl -s https://httpbin.org/get \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('origin:', d.get('origin',''))"
