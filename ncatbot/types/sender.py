from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, model_validator

__all__ = [
    "BaseSender",
    "GroupSender",
]


class BaseSender(BaseModel):
    user_id: Optional[str] = None
    nickname: Optional[str] = "QQ用户"
    sex: Optional[str] = "unknown"
    age: Optional[int] = 0

    @model_validator(mode="before")
    @classmethod
    def _coerce_ids(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for key, value in data.items():
                if key.endswith("_id") and isinstance(value, (int, float)):
                    data[key] = str(int(value))
        return data


class GroupSender(BaseSender):
    card: Optional[str] = None
    area: Optional[str] = None
    level: Optional[str] = None
    role: Optional[str] = None
    title: Optional[str] = None
