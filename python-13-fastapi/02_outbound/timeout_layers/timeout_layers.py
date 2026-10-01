"""
学習ポイント: タイムアウトは4分類と階層で考える
- 4分類 : connect / read / write / pool
- 階層   : クライアント > ALB > uvicorn > アプリ > 外部呼び出し・DB
- 鉄則   : 外側ほど長く、内側ほど短く。逆転させない

SRE 的な論点:
  逆転していると、下流がまだ処理を続けているのに上流が諦める。
  上流から見れば 504、下流から見れば正常終了。両方のログを突き合わせても
  「どちらも正しく見える」ため原因にたどり着きにくい。
  さらに、諦めた側の接続は解放されても下流の処理は走り続けるので、
  リソースだけが無駄に消費される。
"""
import httpx

# ── 4分類の意味 ───────────────────────────────────────
#   connect : TCP 接続確立まで。相手が落ちている/SG で落ちている場合に効く
#   read    : レスポンスの次の1バイトが来るまで。相手が遅い場合に効く
#   write   : リクエスト送信時。大きなボディを送るときに効く
#   pool    : プールから接続を借りられるまで。自分が詰まっている場合に効く
TIMEOUT = httpx.Timeout(connect=3.0, read=5.0, write=5.0, pool=3.0)

# ❌ よくある誤り: read だけ設定して connect を無設定にする
#    → 相手が無応答のとき、接続確立で無限に待つ
BAD_TIMEOUT = httpx.Timeout(5.0)  # 全部 5 秒（まだマシ）。None は無限待ち


# ── 階層設計の記入表 ──────────────────────────────────
# 担当システムの実値を埋めて、外側 > 内側 になっているか確認する
LAYERS = [
    # (層, 設定項目, 値[秒])
    ("クライアント", "HTTP client timeout", 60),
    ("ALB", "idle_timeout.timeout_seconds", 50),
    ("uvicorn", "--timeout-keep-alive", 45),
    ("アプリ", "エンドポイント内の処理上限", 30),
    ("外部API", "httpx read timeout", 5),
    ("DB", "statement_timeout", 10),
]


def check_layers(layers=LAYERS) -> list[str]:
    """外側 > 内側 が崩れている箇所を返す"""
    problems = []
    for i in range(len(layers) - 1):
        outer_name, _, outer = layers[i]
        inner_name, _, inner = layers[i + 1]
        if outer <= inner:
            problems.append(
                f"逆転: {outer_name}({outer}s) <= {inner_name}({inner}s)"
            )
    return problems


if __name__ == "__main__":
    for line in check_layers() or ["逆転なし"]:
        print(line)
