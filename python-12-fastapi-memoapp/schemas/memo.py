from typing import Annotated
from pydantic import BaseModel, Field
from datetime import datetime

# ── 型エイリアス ──────────────────────────────────────────
Priority = Annotated[str, Field(description="優先度", examples=["高"])]
DueDate = Annotated[
    datetime | None,
    Field(
        None,
        description="メモの期限日、設定されていない場合はNone",
        examples=["2023-10-01T00:00:00"],
    ),
]
IsCompleted = Annotated[
    bool,
    Field(False, description="メモが完了したかどうかを示すフラグ", examples=[False]),
]

MemoTitle = Annotated[
    str,
    Field(
        min_length=1,
        description="メモのタイトルを入力してください。少なくとも1文字以上必要です。",
        examples=["明日のアジェンダ"],
    ),
]
MemoDesc = Annotated[
    str,
    Field(
        default="",
        description="メモの内容についての追加情報。任意で記入できます。",
        examples=["会議で話すトピック：プロジェクトの進捗状況"],
    ),
]
MemoId = Annotated[
    int,
    Field(
        description="メモを一意に識別するID番号。データベースで自動的に割り当てられます。",
        examples=[123],
    ),
]
ResponseMsg = Annotated[
    str,
    Field(
        description="API操作の結果を説明するメッセージ。",
        examples=["メモの更新に成功しました。"],
    ),
]


# ── モデル ────────────────────────────────────────────────
class MemoStatusSchema(BaseModel):
    priority: Priority
    due_date: DueDate = None
    is_completed: IsCompleted = False


class InsertAndUpdateMemoSchema(BaseModel):
    title: MemoTitle
    description: MemoDesc = ""
    status: Annotated[MemoStatusSchema, Field(description="メモの状態を表す情報")]


class MemoSchema(InsertAndUpdateMemoSchema):
    memo_id: MemoId


class ResponseSchema(BaseModel):
    message: ResponseMsg
