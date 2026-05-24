"""
学習ポイント: Pydanticモデルの定義
- BaseModel  : 全スキーマの基底クラス
- Field      : バリデーションルール・デフォルト値・Swagger例示値の定義
- Optional   : 省略可能フィールド（None許容）
- Enum       : 列挙型フィールド
- ConfigDict : モデル設定（from_attributes=Trueでorm_modeに相当）
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ItemStatus(Enum):
    ON_SALE = "ON_SALE"
    SOLD_OUT = "SOLD_OUT"


class ItemCreate(BaseModel):
    name: str = Field(min_length=2, max_length=20, examples=["ノートPC"])
    price: int = Field(gt=0, examples=[50000])
    description: Optional[str] = Field(None, examples=["美品です"])


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=20)
    price: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    status: Optional[ItemStatus] = None


class ItemResponse(BaseModel):
    id: int
    name: str
    price: int
    description: Optional[str]
    status: ItemStatus
    created_at: datetime
    updated_at: datetime
    user_id: int
    model_config = ConfigDict(from_attributes=True)  # ORMオブジェクトを直接変換


# 動作確認
if __name__ == "__main__":
    item = ItemCreate(name="ノートPC", price=50000)
    print(item.model_dump())
    try:
        ItemCreate(name="A", price=-100)  # バリデーションエラー
    except Exception as e:
        print(f"ValidationError: {e}")
