"""
32. Lambda 関数の設定・環境変数更新
設定変更・強制再デプロイに使用する。コードを変更せずに設定だけ更新できる。
"""
import boto3
import time

lmb = boto3.client('lambda', region_name='ap-northeast-1')
FUNCTION_NAME = 'my-function'

# 現在の設定を取得
current = lmb.get_function_configuration(FunctionName=FUNCTION_NAME)
current_env = current.get('Environment', {}).get('Variables', {})
print(f"現在の環境変数: {current_env}")

# 環境変数を更新
new_env = {**current_env, 'LOG_LEVEL': 'DEBUG', 'FORCE_REDEPLOY': str(int(time.time()))}
lmb.update_function_configuration(
    FunctionName=FUNCTION_NAME,
    Environment={'Variables': new_env},
    Timeout=30,
    MemorySize=256,
)
print(f"設定を更新しました: {FUNCTION_NAME}")

# メモリ・タイムアウト変更を待機
waiter = lmb.get_waiter('function_updated')
waiter.wait(FunctionName=FUNCTION_NAME)
print("更新完了")
