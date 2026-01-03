"""
任务执行器

提供定时任务的执行逻辑。
"""

import asyncio
import traceback
from typing import Dict, Any, Callable, TYPE_CHECKING

from ncatbot.utils import run_coroutine, get_log

if TYPE_CHECKING:
    from .service import TimeTaskService

LOG = get_log("TimeTaskExecutor")


class TaskExecutor:
    """
    任务执行器

    负责执行定时任务，包括：
    - 条件检查
    - 参数处理
    - 执行任务函数
    - 事件发布
    """

    def __init__(self, service: "TimeTaskService"):
        self._service = service

    def execute(self, job_info: Dict[str, Any]) -> None:
        """
        执行任务

        Args:
            job_info: 任务信息字典
        """
        name = job_info["name"]

        # 执行次数检查
        if job_info["max_runs"] and job_info["run_count"] >= job_info["max_runs"]:
            self._service.remove_job(name)
            return

        # 条件检查
        if not self._check_conditions(job_info):
            return

        # 执行任务
        final_args, final_kwargs = self._prepare_arguments(job_info)

        try:
            self._run_task(job_info["func"], final_args, final_kwargs)
            job_info["run_count"] += 1
            self._publish_event(name)

        except Exception as e:
            LOG.error(f"定时任务执行失败 [{name}]: {e}")
            LOG.debug(f"任务执行异常堆栈:\n{traceback.format_exc()}")

    def _check_conditions(self, job_info: Dict[str, Any]) -> bool:
        """检查执行条件"""
        return all(cond() for cond in job_info["conditions"])

    def _prepare_arguments(self, job_info: Dict[str, Any]) -> tuple:
        """准备任务参数"""
        # 动态参数
        dyn_args = job_info["args_provider"]() if job_info["args_provider"] else ()
        dyn_kwargs = (
            job_info["kwargs_provider"]() if job_info["kwargs_provider"] else {}
        )

        # 合并参数（动态参数优先）
        final_args = dyn_args or job_info["static_args"] or ()
        final_kwargs = {**job_info["static_kwargs"], **dyn_kwargs}

        return final_args, final_kwargs

    def _run_task(self, func: Callable, args: tuple, kwargs: dict) -> None:
        """运行任务函数"""
        if asyncio.iscoroutinefunction(func):
            run_coroutine(func, *args, **kwargs)
        else:
            func(*args, **kwargs)

    def _publish_event(self, task_name: str) -> None:
        """发布任务执行事件（线程安全）"""
        service_manager = self._service.service_manager
        if service_manager is None:
            return

        bot_client = getattr(service_manager, "bot_client", None)
        if bot_client is None:
            return

        event_bus = getattr(bot_client, "event_bus", None)
        if event_bus is None:
            return

        from ncatbot.core.client.ncatbot_event import NcatBotEvent

        event = NcatBotEvent(
            type="ncatbot.time_task_executed",
            data={"task_name": task_name},
        )

        # 使用 EventBus 提供的线程安全接口
        event_bus.publish_threadsafe_wait(event, timeout=1.0)
