"""
log_file_config_write.py - ログファイルの設定・書き込み
"""

import logging
import logging.config
import logging.handlers
import json
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


# ============================================================
# 1. loggingモジュールの基本 / ログレベルの設定
# ============================================================
def basic_logging():
    """basicConfig による最小構成"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logger = logging.getLogger(__name__)

    logger.debug("デバッグ情報")
    logger.info("正常処理")
    logger.warning("警告")
    logger.error("エラー発生")
    logger.critical("致命的エラー")


# ============================================================
# 2. ファイル + コンソール出力 / Formatter / getLogger
# ============================================================
def file_and_console_logging():
    """FileHandler + StreamHandler を組み合わせる"""
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)

    # 既存ハンドラをクリア（関数を複数回呼んでも重複しない）
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ファイルハンドラ（INFO以上）
    fh = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    # コンソールハンドラ（DEBUG以上）
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)

    logger.debug("デバッグ: コンソールのみ出力")
    logger.info("INFO: ファイルとコンソール両方に出力")
    logger.warning("WARNING: 想定外の値を検出")
    logger.error("ERROR: DB接続失敗")


# ============================================================
# 3. RotatingFileHandler（サイズローテーション）
# ============================================================
def rotating_file_logging():
    """ファイルサイズが上限に達したらローテーション"""
    logger = logging.getLogger("app.rotating")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    handler = logging.handlers.RotatingFileHandler(
        filename=LOG_DIR / "app_rotating.log",
        maxBytes=1 * 1024 * 1024,    # 1MB でローテーション
        backupCount=5,               # 最大5世代保持
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    ))
    logger.addHandler(handler)

    for i in range(5):
        logger.info(f"RotatingFileHandler テスト {i + 1}")


# ============================================================
# 4. TimedRotatingFileHandler（時刻ローテーション）
# ============================================================
def timed_rotating_file_logging():
    """毎日深夜0時にローテーション"""
    logger = logging.getLogger("app.timed")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_DIR / "app_timed.log",
        when="midnight",             # 毎日深夜にローテーション
        interval=1,                  # 1日ごと
        backupCount=30,              # 30日分保持
        encoding="utf-8",
    )
    # ローテーション後のファイル名サフィックス
    handler.suffix = "%Y%m%d"

    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    ))
    logger.addHandler(handler)

    logger.info("TimedRotatingFileHandler テスト")


# ============================================================
# 5. logging.config による設定ファイルからの読み込み
# ============================================================

# logging設定をdictで定義（実務ではJSONやYAMLから読み込むことが多い）
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)-8s] %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "[%(levelname)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": str(LOG_DIR / "app_config.log"),
            "maxBytes": 1048576,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "app.service": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console"],
    },
}


def config_dict_logging():
    """dictConfig による設定読み込み"""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("app.service")

    logger.debug("DEBUG: 詳細トレース")
    logger.info("INFO: サービス起動")
    logger.warning("WARNING: レスポンス遅延")
    logger.error("ERROR: 外部API呼び出し失敗")


def config_file_logging():
    """JSONファイルから設定を読み込む"""
    config_path = LOG_DIR / "logging_config.json"

    # 設定ファイルを生成
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(LOGGING_CONFIG, f, indent=2, ensure_ascii=False)

    # JSONから読み込んで適用
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    logging.config.dictConfig(config)
    logger = logging.getLogger("app.service")
    logger.info("JSONファイルから設定を読み込みました")

