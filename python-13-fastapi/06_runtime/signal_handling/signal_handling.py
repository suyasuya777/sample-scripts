"""
学習ポイント: SIGTERM がアプリまで届くか
- PID 1 問題 : シェル形式の CMD だと sh が PID 1 になり、シグナルを転送しない
- exec 形式  : CMD ["uvicorn", ...] と書けば uvicorn が PID 1 になる
- 確認方法   : コンテナ内で ps を見て、PID 1 が何かを確かめる

SRE 的な論点:
  SIGTERM が届かないと、graceful shutdown のコードは一切動かない。
  stopTimeout の秒数だけ待たされたあと SIGKILL で強制終了され、
  処理中のリクエストが切れる。デプロイのたびに一定数の 5xx が出る形になる。

  01_lifecycle で書いたシャットダウン処理が「動いていない」場合、
  まずここを疑う。
"""
import os
import signal
import sys

received = []


def handler(signum, frame):
    name = signal.Signals(signum).name
    received.append(name)
    print(f"[signal] received {name} (pid={os.getpid()})", flush=True)
    sys.exit(0)


signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

if __name__ == "__main__":
    print(f"[start] pid={os.getpid()} — send SIGTERM to test", flush=True)
    signal.pause()


# ── コンテナでの確認手順 ──────────────────────────────
# docker run -d --name sig sre-sample
# docker exec sig ps -eo pid,comm        # PID 1 が sh なら NG、uvicorn なら OK
# docker stop sig                        # ログに [signal] received SIGTERM が出るか
#
# ── ❌ NG な書き方 ────────────────────────────────────
# CMD uvicorn main:app --host 0.0.0.0     # シェル形式。sh が PID 1
# CMD ["sh", "-c", "uvicorn main:app"]    # 同上
#
# ── ✅ OK な書き方 ────────────────────────────────────
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#
# どうしてもシェルが必要なら tini や dumb-init を挟む:
# ENTRYPOINT ["/usr/bin/tini", "--"]
