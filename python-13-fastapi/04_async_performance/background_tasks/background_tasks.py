"""
学習ポイント: BackgroundTasksによるバックグラウンド処理
- BackgroundTasks.add_task(): レスポンス返却後に非同期で処理を実行
- 用途: メール送信・ログ記録・通知・キャッシュ更新など
"""
import time
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def send_email(to: str, subject: str, body: str):
    """実際のメール送信処理（重い処理のシミュレーション）"""
    time.sleep(2)
    print(f"[BG] Email sent to {to}: {subject}")

def log_operation(user_id: int, action: str):
    print(f"[BG] Log: user={user_id} action={action}")

@app.post("/items")
async def create_item(name: str, user_id: int, background_tasks: BackgroundTasks):
    # レスポンスを即座に返しつつ、バックグラウンドでメール・ログを処理
    background_tasks.add_task(send_email, "user@example.com", "出品完了", f"{name}を出品しました")
    background_tasks.add_task(log_operation, user_id, f"create_item:{name}")
    return {"message": "アイテムを出品しました（メール送信中）", "name": name}
