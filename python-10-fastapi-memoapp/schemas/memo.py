from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# ── 型エイリアス ──────────────────────────────────────────
MemoId = Annotated[
    int,
    Field(
        description="メモを一意に識別するID番号。データベースで自動的に割り当てられます。",
        examples=[123],
    ),
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
    str | None,
    Field(
        default=None,
        description="メモの内容についての追加情報。任意で記入できます。",
        examples=["会議で話すトピック：プロジェクトの進捗状況"],
    ),
]

Priority = Annotated[str, Field(description="優先度", examples=["高"])]

DueDate = Annotated[
    datetime | None,
    Field(
        default=None,
        description="メモの期限日、設定されていない場合はNone",
        examples=["2023-10-01T00:00:00"],
    ),
]

IsCompleted = Annotated[
    bool,
    Field(default=False, description="メモが完了したかどうかを示すフラグ", examples=[False]),
]

ResponseMsg = Annotated[
    str,
    Field(
        description="API操作の結果を説明するメッセージ。",
        examples=["メモの更新に成功しました。"],
    ),
]


# ── モデル ────────────────────────────────────────────────
class CreateAndUpdateMemoSchema(BaseModel):
    title: MemoTitle
    description: MemoDesc
    priority: Priority
    due_date: DueDate
    is_completed: IsCompleted


class MemoSchema(CreateAndUpdateMemoSchema):
    model_config = ConfigDict(from_attributes=True)
    memo_id: MemoId
    created_at: datetime
    updated_at: datetime | None


class ResponseSchema(BaseModel):
    message: ResponseMsg
