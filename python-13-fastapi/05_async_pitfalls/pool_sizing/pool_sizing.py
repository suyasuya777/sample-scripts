"""
学習ポイント: 接続数はスケールアウトの天井になる
- 式 : ワーカー数 × タスク数 × プール上限 ≦ 下流の受け入れ上限
- DB なら max_connections、外部APIなら相手のレート上限

SRE 的な論点:
  「負荷が高いのでタスク数を増やす」は、DB 接続数の上限に当たると逆効果になる。
  接続が取れないタスクが増え、全体のエラー率が上がる。
  スケールアウトの前に、この式が成り立つかを確認する。

  RDS の max_connections はインスタンスクラスのメモリから自動算出される
  （パラメータグループの既定式）。実値は SHOW max_connections で確認する。
  RDS Proxy を挟むと、アプリ側の接続数と DB 側の接続数を分離できる。
"""
from dataclasses import dataclass


@dataclass
class Plan:
    workers_per_task: int    # uvicorn のワーカー数（1推奨）
    tasks: int               # ECS のタスク数
    pool_per_worker: int     # 1ワーカーあたりのDBプール上限
    db_max_connections: int  # DB 側の上限
    reserved: int = 10       # 管理用に空けておく分

    def used(self) -> int:
        return self.workers_per_task * self.tasks * self.pool_per_worker

    def available(self) -> int:
        return self.db_max_connections - self.reserved

    def max_tasks(self) -> int:
        """この設定で立てられるタスク数の上限"""
        per_task = self.workers_per_task * self.pool_per_worker
        return self.available() // per_task if per_task else 0

    def report(self) -> str:
        ok = "OK" if self.used() <= self.available() else "超過"
        return (
            f"使用見込み {self.used():4d} / 利用可能 {self.available():4d}  [{ok}]\n"
            f"  このプール設定で立てられるタスク数の上限: {self.max_tasks()}"
        )


if __name__ == "__main__":
    print("── 現状 ──")
    print(Plan(workers_per_task=1, tasks=10, pool_per_worker=10,
               db_max_connections=200).report())
    print("\n── タスクを3倍にスケールアウトした場合 ──")
    print(Plan(workers_per_task=1, tasks=30, pool_per_worker=10,
               db_max_connections=200).report())
    print("\n── プールを絞ってスケールアウトした場合 ──")
    print(Plan(workers_per_task=1, tasks=30, pool_per_worker=5,
               db_max_connections=200).report())
