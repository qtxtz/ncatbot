"""
08_scheduled_tasks — 定时任务

演示功能:
  - TimeTaskMixin: add_scheduled_task / remove_scheduled_task
  - 多种时间格式: "30s"（秒）、"HH:MM"（每日）、一次性
  - conditions 条件执行
  - @registrar.on_group_command() 命令匹配 + int 参数绑定

使用方式:
  "启动心跳"       → 每 30 秒打印一次心跳日志
  "停止心跳"       → 停止心跳任务
  "任务列表"       → 查看当前活跃的定时任务
  "添加提醒 10"    → 10 秒后发送一次性提醒
  "开关任务"       → 切换定时任务的启用状态
"""

from ncatbot.core import registrar
from ncatbot.event import GroupMessageEvent
from ncatbot.plugin import NcatBotPlugin
from ncatbot.utils import get_log

LOG = get_log("ScheduledTasks")


class ScheduledTasksPlugin(NcatBotPlugin):
    name = "scheduled_tasks"
    version = "1.0.0"
    author = "NcatBot"
    description = "定时任务演示"

    async def on_load(self):
        self._enabled = True
        self._notify_group = None  # 接收通知的群号

        # 启动一个带条件的定时任务：每 60 秒执行，仅在 enabled 时
        self.add_scheduled_task(
            "conditional_tick",
            "60s",
            conditions=[lambda: self._enabled],
        )

        LOG.info("ScheduledTasks 插件已加载")

    # ---- 心跳任务管理 ----

    @registrar.on_group_command("启动心跳")
    async def on_start_heartbeat(self, event: GroupMessageEvent):
        """启动心跳定时任务（每 30 秒）"""
        self._notify_group = str(event.group_id)
        success = self.add_scheduled_task("heartbeat", "30s")
        if success:
            await event.reply("💓 心跳任务已启动（每 30 秒）")
        else:
            await event.reply("心跳任务已存在或启动失败")

    @registrar.on_group_command("停止心跳")
    async def on_stop_heartbeat(self, event: GroupMessageEvent):
        """停止心跳定时任务"""
        self.remove_scheduled_task("heartbeat")
        await event.reply("💔 心跳任务已停止")

    # ---- 一次性任务 (CommandHook 自动绑定 int 参数) ----

    @registrar.on_group_command("添加提醒")
    async def on_add_reminder(self, event: GroupMessageEvent, seconds: int = 0):
        """添加一次性提醒: 添加提醒 10 → 10 秒后提醒"""
        if seconds <= 0:
            await event.reply("请输入秒数，例如: 添加提醒 10")
            return

        self._notify_group = str(event.group_id)
        task_name = f"reminder_{seconds}s"
        success = self.add_scheduled_task(task_name, seconds, max_runs=1)
        if success:
            await event.reply(f"⏰ 将在 {seconds} 秒后提醒你")
        else:
            await event.reply("添加提醒失败")

    # ---- 条件任务开关 ----

    @registrar.on_group_command("开关任务")
    async def on_toggle(self, event: GroupMessageEvent):
        """切换定时任务启用状态"""
        self._enabled = not self._enabled
        state = "启用" if self._enabled else "禁用"
        await event.reply(f"定时任务已{state} {'✅' if self._enabled else '❌'}")

    # ---- 任务查询 ----

    @registrar.on_group_command("任务列表")
    async def on_list_tasks(self, event: GroupMessageEvent):
        """查看当前定时任务列表"""
        tasks = self.list_scheduled_tasks()
        if not tasks:
            await event.reply("当前没有活跃的定时任务")
            return

        lines = ["📋 定时任务列表:"]
        for name in tasks:
            status = self.get_task_status(name)
            if status:
                lines.append(f"  {name}: 运行 {status.get('run_count', 0)} 次")
            else:
                lines.append(f"  {name}")

        await event.reply("\n".join(lines))

    # ---- 任务回调（框架自动调用同名方法） ----

    async def heartbeat(self):
        """心跳回调"""
        LOG.info("💓 心跳")
        if self._notify_group:
            await self.api.post_group_msg(
                self._notify_group, text="💓 心跳 - 我还活着！"
            )

    async def conditional_tick(self):
        """条件任务回调"""
        LOG.info("⏱️ 条件定时任务执行了（enabled=%s）", self._enabled)
