from datetime import datetime, timezone
from bson.objectid import ObjectId
from typing import Optional
formafrom pydantic import BaseModel, Field, validator


class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')  # mongo return Bson
    asset_object_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)
    asset_pushed_at: datetime = Field(
        default=datetime.now(timezone.utc).replace(tzinfo=None))
    asset_config: dict = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("asset_object_id", 1)
                ],
                "name": "asset_object_id_index_1",
                "unique": False
            },
            {
                "key": [
                    ("asset_object_id", 1),
                    ("asset_name", 1)
                ],
                "name": "asset_object_id_name_index_1",
                "unique": True
            }
        ]
