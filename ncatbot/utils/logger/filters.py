"""日志过滤器。"""

import re
import logging


class MessageFoldFilter(logging.Filter):
    """折叠超长消息和 base64 内容。

    - 替换连续 1000+ 字符的 base64 片段为 [BASE64_CONTENT]
    - 总长超过 2000 字符时截断
    """

    _BASE64_RE = re.compile(r"[A-Za-z0-9+/\\]{1000,}={0,2}")
    MAX_LENGTH = 2000

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        if len(msg) > 1000:
            msg = self._BASE64_RE.sub("[BASE64_CONTENT]", msg)
        if len(msg) > self.MAX_LENGTH:
            msg = msg[: self.MAX_LENGTH] + "...[TRUNCATED]"
        record.msg = msg
        record.args = None
        return True
