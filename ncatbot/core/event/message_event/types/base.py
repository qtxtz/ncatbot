from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict


class MessageSegment(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    type: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageSegment":
        """从 {"type": "...", "data": {...}} 结构或扁平结构解析"""
        seg_type = data.get("type")
        payload = data.get("data", data)
        # 注意：实际使用时通常配合 TypeAdapter 或根据 type 映射子类
        return cls.model_validate({**payload, "type": seg_type})

    def to_dict(self) -> Dict[str, Any]:
        """序列化为 {"type": "...", "data": {...}} 结构"""
        dump = self.model_dump(exclude={"type"}, exclude_none=True)
        return {"type": self.type, "data": dump}


class MessageArrayDTO(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
    message: List[MessageSegment]

    @classmethod
    def from_list(cls, data: List[Dict]):
        return cls(message=[MessageSegment.from_dict(seg) for seg in data])

    def to_list(self):
        return self.model_dump()
