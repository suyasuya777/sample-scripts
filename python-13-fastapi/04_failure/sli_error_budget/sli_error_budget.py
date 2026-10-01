"""
学習ポイント: SLI を定義し、エラーバジェットを数字にする
- SLI : 測る指標。「成功リクエスト数 ÷ 全リクエスト数」
- SLO : 目標値。「30日間で 99.9% 以上」
- エラーバジェット : 100% - SLO。許容される失敗の総量

SRE 的な論点:
  SLO は「守るための目標」であると同時に「使うための予算」。
  バジェットが余っているならリリース速度を上げてよいし、
  尽きているなら新機能を止めて信頼性の改善に回す、という判断材料になる。
  これがないと「落ちたから怒られる」という属人的な運用のままになる。

  注意: SLI は利用者から見た指標にする。サーバ側の 5xx 率だけでは、
  LB より手前で落ちた分（ターゲット全滅、TLS失敗）が見えない。
  ALB のメトリクスや合成監視を併用する。
"""
from dataclasses import dataclass


@dataclass
class SLO:
    name: str
    target: float          # 例: 0.999
    window_days: int = 30

    def budget_ratio(self) -> float:
        return 1.0 - self.target

    def allowed_downtime_minutes(self) -> float:
        return self.window_days * 24 * 60 * self.budget_ratio()

    def allowed_failures(self, total_requests: int) -> float:
        return total_requests * self.budget_ratio()

    def consumed_ratio(self, total: int, failures: int) -> float:
        """バジェットの何%を使ったか"""
        allowed = self.allowed_failures(total)
        return (failures / allowed * 100) if allowed else float("inf")


if __name__ == "__main__":
    for target in (0.99, 0.995, 0.999, 0.9995, 0.9999):
        slo = SLO(name="availability", target=target)
        print(f"SLO {target*100:7.3f}% → 30日で {slo.allowed_downtime_minutes():8.1f} 分")

    print()
    slo = SLO(name="availability", target=0.999)
    total, failures = 10_000_000, 6_500
    print(f"総リクエスト {total:,} / 5xx {failures:,}")
    print(f"  許容失敗数 : {slo.allowed_failures(total):,.0f}")
    print(f"  消費率     : {slo.consumed_ratio(total, failures):.1f}%")


# ── SLI 定義文のテンプレート ──────────────────────────
#
# 指標名 : API 可用性
# 対象   : ALB のターゲットグループ xxx に届いた全リクエスト
#          （ヘルスチェックパスを除く）
# 成功   : elb_status_code が 5xx 以外
# 計測   : ALB の RequestCount と HTTPCode_Target_5XX_Count
# 窓     : 直近30日のローリング
# 目標   : 99.9%
#
# 自分の担当システムについて、この6項目を埋めてみること。
# 埋まらない項目があれば、そこが計測できていない箇所。
