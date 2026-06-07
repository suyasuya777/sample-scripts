from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

MemoId = Annotated[
    int, Field(
        description="メモを一意に識別するID番号。データベースで自動的に割り当てられます。",
        examples=[123]
    )
]

MemoTitle = Annotated[
    str, Field(
        min_length=1,
        description="メモのタイトルを入力してください。少なくとも1文字以上必要です。",
        examples=["明日のアジェンダ"]
    )
]

MemoDescription = Annotated[
    str | None, Field(
        default=None,
        description="メモの内容についての追加情報。任意で記入できます。",
        examples=["会議で話すトピック：プロジェクトの進捗状況"]
    )
]

MemoPriority = Annotated[
    str, Field(
        description="優先度",
        examples=["高"]
    )
]

MemoDueDate = Annotated[
    datetime | None, Field(
        default=None,
        description="メモの期限日、設定されていない場合はNone",
        examples=["2023-10-01T00:00:00"]
    )
]

MemoIsCompleted = Annotated[
    bool, Field(
        default=False,
        description="メモが完了したかどうかを示すフラグ",
        examples=[False]
    )
]

ResponseMessage = Annotated[
    str, Field(
        description="API操作の結果を説明するメッセージ。",
        examples=["メモの更新に成功しました。"],
    ),
]


class MemoBase(BaseModel):
    title: MemoTitle
    description: MemoDescription
    priority: MemoPriority
    due_date: MemoDueDate
    is_completed: MemoIsCompleted


class Memo(MemoBase):
    model_config = ConfigDict(from_attributes=True)
    id: MemoId
    created_at: datetime
    updated_at: datetime | None


class MemoResponse(BaseModel):
    message: ResponseMessage
