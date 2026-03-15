"""NcatBot CLI 主入口 — click group 定义。"""

import importlib.metadata

import click

from .commands.run import run, dev
from .commands.config import config
from .commands.plugin import plugin
from .commands.napcat import napcat
from .commands.init import init


def _get_version() -> str:
    try:
        return importlib.metadata.version("ncatbot5")
    except importlib.metadata.PackageNotFoundError:
        return "dev"


@click.group(invoke_without_command=True)
@click.version_option(version=_get_version(), prog_name="NcatBot")
@click.pass_context
def cli(ctx: click.Context):
    """NcatBot — QQ 机器人框架 CLI"""
    if ctx.invoked_subcommand is None:
        from .utils.repl import start_repl

        start_repl(ctx)


cli.add_command(run)
cli.add_command(dev)
cli.add_command(config)
cli.add_command(plugin)
cli.add_command(napcat)
cli.add_command(init)
