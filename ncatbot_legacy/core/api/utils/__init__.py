"""
API 工具类和基础组件

提供 API 调用的核心工具、错误处理、状态管理和依赖注入支持。
"""

# 同步运行器
from .sync_runner import AsyncRunner as AsyncRunner
from .sync_runner import run_sync as run_sync
from .sync_runner import generate_sync_methods as generate_sync_methods

# 错误类型
from .errors import NapCatAPIError as NapCatAPIError
from .errors import APIValidationError as APIValidationError

# 参数验证
from .validation import require_at_least_one as require_at_least_one
from .validation import require_exactly_one as require_exactly_one
from .validation import check_exclusive_argument as check_exclusive_argument

# 响应状态
from .status import APIReturnStatus as APIReturnStatus
from .status import MessageAPIReturnStatus as MessageAPIReturnStatus

# 组件基类
from .component import APIComponent as APIComponent
