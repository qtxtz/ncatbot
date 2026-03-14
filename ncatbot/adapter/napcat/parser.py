"""
NapCat 事件解析

将 OB11 原始 JSON 转换为 BaseEventData 数据模型。
只产出纯数据模型，不创建实体。
"""

from typing import Optional

from ncatbot.event.parser import EventParser
from ncatbot.types import BaseEventData
from ncatbot.utils import get_log

LOG = get_log("NapCatEventParser")


class NapCatEventParser:
    """将 OB11 原始 JSON 转换为 BaseEventData"""

    def parse(self, raw_data: dict) -> Optional[BaseEventData]:
        if "post_type" not in raw_data:
            return None
        try:
            return EventParser.parse(raw_data)
        except ValueError as e:
            LOG.debug(f"事件解析跳过: {e}")
            return None
        except Exception as e:
            LOG.warning(f"事件解析失败: {e}")
            return None
