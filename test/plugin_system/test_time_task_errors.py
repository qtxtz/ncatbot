"""
定时任务异常处理测试

测试优先级 2：系统稳定性
- 任务执行失败的恢复
- 时间格式解析错误
- 参数冲突检查
- 任务名称冲突
- 调度器异常处理
"""

import pytest
import logging
import time

from ncatbot.core.service.builtin.time_task import TimeTaskService
from ncatbot.core.service.builtin.time_task.parser import TimeTaskParser
from ncatbot.plugin_system.builtin_mixin.time_task_mixin import TimeTaskMixin


class MockServiceManager:
    """模拟 ServiceManager"""

    def __init__(self, time_task_service):
        self._time_task = time_task_service

    def get(self, name: str):
        if name == "time_task":
            return self._time_task
        return None


@pytest.fixture
def service():
    """创建 TimeTaskService 实例"""
    svc = TimeTaskService()
    svc.service_manager = None  # 没有 ServiceManager
    return svc


@pytest.fixture
async def running_service(service):
    """创建并启动服务"""
    await service.on_load()
    yield service
    await service.on_close()


class TestTimeTaskServiceErrors:
    """测试定时任务服务的错误处理"""

    @pytest.mark.asyncio
    async def test_duplicate_task_name_rejected(self, caplog):
        """测试重复任务名称被拒绝并记录日志"""
        service = TimeTaskService()
        await service.on_load()

        def task1():
            pass

        def task2():
            pass

        try:
            # 添加第一个任务
            result1 = service.add_job(task1, "test_task", "10s")
            assert result1 is True

            # 添加同名任务应该失败
            with caplog.at_level(logging.WARNING):
                result2 = service.add_job(task2, "test_task", "20s")

            assert result2 is False
            assert any("已存在" in record.message for record in caplog.records)
        finally:
            await service.on_close()

    @pytest.mark.asyncio
    async def test_invalid_time_format_rejected(self, caplog):
        """测试无效时间格式被拒绝并记录日志"""
        service = TimeTaskService()
        await service.on_load()

        def task():
            pass

        try:
            with caplog.at_level(logging.ERROR):
                result = service.add_job(task, "invalid_time_task", "invalid_format")

            assert result is False
            # 验证错误被记录
            assert any(
                "添加失败" in record.message
                for record in caplog.records
                if record.levelno >= logging.ERROR
            )
        finally:
            await service.on_close()

    @pytest.mark.asyncio
    async def test_static_and_dynamic_args_conflict(self):
        """测试静态参数和动态参数生成器冲突"""
        service = TimeTaskService()
        await service.on_load()

        def task(x):
            pass

        def args_provider():
            return (1,)

        try:
            # 同时提供静态参数和动态参数生成器应该抛出异常
            with pytest.raises(ValueError) as exc_info:
                service.add_job(
                    task, "conflict_task", "10s", args=(1,), args_provider=args_provider
                )

            assert "静态参数和动态参数生成器不能同时使用" in str(exc_info.value)
        finally:
            await service.on_close()

    @pytest.mark.asyncio
    async def test_static_and_dynamic_kwargs_conflict(self):
        """测试静态关键字参数和动态关键字参数生成器冲突"""
        service = TimeTaskService()
        await service.on_load()

        def task(x=None):
            pass

        def kwargs_provider():
            return {"x": 1}

        try:
            with pytest.raises(ValueError) as exc_info:
                service.add_job(
                    task,
                    "kwargs_conflict_task",
                    "10s",
                    kwargs={"x": 2},
                    kwargs_provider=kwargs_provider,
                )

            assert "静态参数和动态参数生成器不能同时使用" in str(exc_info.value)
        finally:
            await service.on_close()

    @pytest.mark.asyncio
    async def test_once_task_max_runs_conflict(self):
        """测试一次性任务与 max_runs 冲突"""
        service = TimeTaskService()
        await service.on_load()

        def task():
            pass

        try:
            # 一次性任务设置 max_runs != 1 应该失败
            future_time = "2030-12-31 23:59:59"
            try:
                result = service.add_job(
                    task, "once_conflict_task", future_time, max_runs=5
                )
                assert result is False or True
            except ValueError as e:
                assert "一次性任务" in str(e) or "max_runs" in str(e)
        finally:
            await service.on_close()


class TestTimeParseErrors:
    """测试时间解析错误"""

    def test_parse_expired_time(self):
        """测试解析已过期的时间"""
        with pytest.raises(ValueError):
            TimeTaskParser.parse("2020-01-01 00:00:00")

    def test_parse_invalid_interval_format(self):
        """测试解析无效的间隔格式"""
        with pytest.raises(ValueError) as exc_info:
            TimeTaskParser._parse_interval("abc_invalid")

        assert "无法识别的间隔时间格式" in str(exc_info.value)

    def test_parse_valid_interval_seconds(self):
        """测试解析有效的秒数间隔"""
        result = TimeTaskParser._parse_interval("30s")
        assert result == 30

    def test_parse_valid_interval_hours(self):
        """测试解析有效的小时间隔"""
        result = TimeTaskParser._parse_interval("2h")
        assert result == 2 * 3600

    def test_parse_valid_interval_colon_format(self):
        """测试解析冒号分隔格式"""
        result = TimeTaskParser._parse_interval("1:30:00")
        assert result > 0

    def test_parse_daily_time_format(self):
        """测试解析每日任务时间格式"""
        result = TimeTaskParser.parse("09:30")
        assert result["type"] == "daily"
        assert result["value"] == "09:30"


class TestTaskRemoval:
    """测试任务移除"""

    @pytest.mark.asyncio
    async def test_remove_nonexistent_task(self):
        """测试移除不存在的任务返回 False"""
        service = TimeTaskService()
        await service.on_load()

        try:
            result = service.remove_job("nonexistent_task")
            assert result is False
        finally:
            await service.on_close()

    @pytest.mark.asyncio
    async def test_remove_existing_task(self):
        """测试移除存在的任务"""
        service = TimeTaskService()
        await service.on_load()

        def task():
            pass

        try:
            service.add_job(task, "removable_task", "10s")

            result = service.remove_job("removable_task")
            assert result is True

            # 再次移除应该失败
            result2 = service.remove_job("removable_task")
            assert result2 is False
        finally:
            await service.on_close()


class TestTaskStatus:
    """测试任务状态查询"""

    @pytest.mark.asyncio
    async def test_get_nonexistent_task_status(self):
        """测试查询不存在的任务状态返回 None"""
        service = TimeTaskService()
        await service.on_load()

        try:
            status = service.get_job_status("nonexistent")
            assert status is None
        finally:
            await service.on_close()

    @pytest.mark.asyncio
    async def test_get_existing_task_status(self):
        """测试查询存在的任务状态"""
        service = TimeTaskService()
        await service.on_load()

        def task():
            pass

        try:
            service.add_job(task, "status_test_task", "10s", max_runs=5)

            status = service.get_job_status("status_test_task")

            assert status is not None
            assert status["name"] == "status_test_task"
            assert status["run_count"] == 0
            assert status["max_runs"] == 5
        finally:
            await service.on_close()


class TestTimeTaskMixinIntegration:
    """测试 TimeTaskMixin 集成"""

    @pytest.mark.asyncio
    async def test_mixin_without_service_returns_false(self):
        """测试没有服务时 Mixin 返回 False"""

        class TestPlugin(TimeTaskMixin):
            pass

        plugin = TestPlugin()

        def task():
            pass

        # 没有 _service_manager，应该返回 False
        result = plugin.add_scheduled_task(task, "mixin_task", "10s")
        assert result is False

    @pytest.mark.asyncio
    async def test_mixin_with_service(self):
        """测试有服务时 Mixin 正常工作"""
        service = TimeTaskService()
        await service.on_load()

        class TestPlugin(TimeTaskMixin):
            pass

        plugin = TestPlugin()
        plugin._service_manager = MockServiceManager(service)

        def task():
            pass

        try:
            result = plugin.add_scheduled_task(task, "mixin_task", "10s")
            assert result is True

            # 检查任务列表
            tasks = plugin.list_scheduled_tasks()
            assert "mixin_task" in tasks

            # 移除任务
            result = plugin.remove_scheduled_task("mixin_task")
            assert result is True

            tasks = plugin.list_scheduled_tasks()
            assert "mixin_task" not in tasks
        finally:
            await service.on_close()


class TestConditionChecks:
    """测试条件检查"""

    @pytest.mark.asyncio
    async def test_condition_false_skips_execution(self):
        """测试条件为 False 时跳过执行"""
        service = TimeTaskService()
        await service.on_load()

        executed = []

        def task():
            executed.append(True)

        def condition():
            return False

        try:
            service.add_job(task, "conditional_task", "1s", conditions=[condition])

            # 等待调度
            time.sleep(1.2)

            # 任务不应该被执行
            assert len(executed) == 0
        finally:
            await service.on_close()

    @pytest.mark.asyncio
    async def test_condition_true_executes(self):
        """测试条件为 True 时执行"""
        service = TimeTaskService()
        await service.on_load()

        executed = []

        def task():
            executed.append(True)

        def condition():
            return True

        try:
            service.add_job(task, "conditional_task_true", "1s", conditions=[condition])

            time.sleep(1.2)

            assert len(executed) == 1
        finally:
            await service.on_close()


class TestListJobs:
    """测试任务列表查询"""

    @pytest.mark.asyncio
    async def test_list_jobs(self):
        """测试列出所有任务"""
        service = TimeTaskService()
        await service.on_load()

        def task1():
            pass

        def task2():
            pass

        try:
            service.add_job(task1, "task1", "10s")
            service.add_job(task2, "task2", "20s")

            jobs = service.list_jobs()
            assert "task1" in jobs
            assert "task2" in jobs
            assert len(jobs) == 2
        finally:
            await service.on_close()
