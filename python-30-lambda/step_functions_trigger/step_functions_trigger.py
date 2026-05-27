import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sfn_client = boto3.client("stepfunctions")


# ── 同期タスク（通常の Lambda タスク）────────────────────────
def process_task(params: dict) -> dict:
    """Step Functions から渡された入力パラメータを処理して結果を返す"""
    item_id = params.get("item_id")
    action = params.get("action", "process")

    logger.info("タスク処理: item_id=%s action=%s", item_id, action)

    # ここにビジネスロジックを実装
    result = {
        "item_id": item_id,
        "status": "completed",
        "action": action,
    }
    return result


# ── 非同期コールバックタスク（waitForTaskToken パターン）──────
def handle_callback(task_token: str, params: dict) -> None:
    """
    waitForTaskToken パターン: Step Functions は taskToken を渡して待機する。
    処理完了後に send_task_success / send_task_failure を呼んで再開させる。
    """
    logger.info("コールバックタスク開始: token=%s...", task_token[:20])

    try:
        # 非同期処理（外部 API 呼び出し・人手承認など）の完了を待つ想定
        output = process_task(params)

        sfn_client.send_task_success(
            taskToken=task_token,
            output=json.dumps(output),
        )
        logger.info("send_task_success 完了")
    except Exception as e:
        sfn_client.send_task_failure(
            taskToken=task_token,
            error="TaskFailed",
            cause=str(e),
        )
        logger.error("send_task_failure: %s", e)


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    """
    Step Functions からの呼び出しを判定して処理を振り分ける。

    通常タスク: event に直接パラメータが含まれる
    waitForTaskToken: event に "taskToken" が含まれる
    """
    logger.info("event: %s", json.dumps(event))

    task_token = event.get("taskToken")

    if task_token:
        # 非同期コールバックパターン
        handle_callback(task_token, event.get("params", {}))
        return {"status": "callback_sent"}
    else:
        # 通常の同期タスク: 戻り値が次のステートへの入力になる
        return process_task(event)
