"""Global state management for NcatBot."""

from threading import Lock
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ncatbot_legacy.core.service.builtin.rbac import RBACService


class Status:
    """Global state management class."""

    def __init__(self):
        self.exit = False  # 全局退出标志
        self._lock = Lock()
        self.current_github_proxy = None
        self.global_access_manager: Optional["RBACService"] = None

    def set(self, key: str, value: Any) -> None:
        """Set a state value."""
        with self._lock:
            setattr(self, key, value)


# Global status instance
status = Status()
