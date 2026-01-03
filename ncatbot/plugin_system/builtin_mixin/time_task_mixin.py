"""
定时任务混入类

提供定时任务的注册接口，实际调度由 TimeTaskService 服务完成。
"""

from typing import (
    Callable,
    Optional,
    List,
    Tuple,
    Dict,
    Any,
    Union,
    final,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from ncatbot.core.service.builtin.time_task import TimeTaskService


class TimeTaskMixin:
    """
    定时任务调度混入类，提供定时任务的管理功能。

    描述:
        该混入类提供了定时任务的添加、移除等管理功能。
        实际的任务调度由 TimeTaskService 服务完成。

    属性:
        _time_task_jobs (list): 当前插件注册的任务名称列表

    特性:
        - 支持固定时间间隔的任务调度
        - 支持条件触发机制
        - 支持最大执行次数限制
        - 支持动态参数生成
    """

    @property
    def _time_task_service(self) -> Optional["TimeTaskService"]:
        """获取定时任务服务实例"""
        # 通过 service_manager 获取服务
        if hasattr(self, "_service_manager") and self._service_manager:
            return self._service_manager.get("time_task")
        return None

    @final
    def add_scheduled_task(
        self,
        job_func: Callable,
        name: str,
        interval: Union[str, int, float],
        conditions: Optional[List[Callable[[], bool]]] = None,
        max_runs: Optional[int] = None,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict] = None,
        args_provider: Optional[Callable[[], Tuple]] = None,
        kwargs_provider: Optional[Callable[[], Dict[str, Any]]] = None,
    ) -> bool:
        """
        添加一个定时任务。

        Args:
            job_func: 要执行的任务函数
            name: 任务名称
            interval: 任务执行的时间间隔，支持多种格式:
                - 一次性任务: 'YYYY-MM-DD HH:MM:SS'
                - 每日任务: 'HH:MM'
                - 间隔任务: '120s', '2h30m', '0.5d' 等
            conditions: 任务执行的条件列表，所有条件返回 True 时才执行
            max_runs: 任务的最大执行次数
            args: 任务函数的位置参数
            kwargs: 任务函数的关键字参数
            args_provider: 提供任务函数位置参数的函数
            kwargs_provider: 提供任务函数关键字参数的函数

        Returns:
            如果任务添加成功返回 True，否则返回 False
        """
        service = self._time_task_service
        if service is None:
            from ncatbot.utils import get_log

            LOG = get_log("TimeTaskMixin")
            LOG.warning("定时任务服务不可用，无法添加任务")
            return False

        # 记录插件注册的任务
        if not hasattr(self, "_time_task_jobs"):
            self._time_task_jobs: List[str] = []
        self._time_task_jobs.append(name)

        return service.add_job(
            job_func=job_func,
            name=name,
            interval=interval,
            conditions=conditions,
            max_runs=max_runs,
            args=args,
            kwargs=kwargs,
            args_provider=args_provider,
            kwargs_provider=kwargs_provider,
        )

    @final
    def remove_scheduled_task(self, task_name: str) -> bool:
        """
        移除一个定时任务。

        Args:
            task_name: 要移除的任务名称

        Returns:
            如果任务移除成功返回 True，否则返回 False
        """
        service = self._time_task_service
        if service is None:
            return False

        # 从插件记录中移除
        if hasattr(self, "_time_task_jobs") and task_name in self._time_task_jobs:
            self._time_task_jobs.remove(task_name)

        return service.remove_job(name=task_name)

    @final
    def get_scheduled_task_status(self, task_name: str) -> Optional[Dict[str, Any]]:
        """
        获取定时任务状态。

        Args:
            task_name: 任务名称

        Returns:
            任务状态信息字典，包含:
                - name: 任务名称
                - next_run: 下次运行时间
                - run_count: 已执行次数
                - max_runs: 最大允许次数
        """
        service = self._time_task_service
        if service is None:
            return None
        return service.get_job_status(task_name)

    @final
    def list_scheduled_tasks(self) -> List[str]:
        """
        列出当前插件注册的所有定时任务名称。

        Returns:
            任务名称列表
        """
        if hasattr(self, "_time_task_jobs"):
            return list(self._time_task_jobs)
        return []

    @final
    def cleanup_scheduled_tasks(self) -> None:
        """
        清理当前插件注册的所有定时任务。

        通常在插件卸载时调用。
        """
        if hasattr(self, "_time_task_jobs"):
            for task_name in list(self._time_task_jobs):
                self.remove_scheduled_task(task_name)
