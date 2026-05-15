"""CLI 文本输入增强。"""

from __future__ import annotations

import importlib
import sys

import click

_CLICK_PROMPTS_PATCHED = False


def _patch_click_visible_prompts() -> None:
    """修补 Click 在 POSIX + readline 下的可见输入错位。"""
    global _CLICK_PROMPTS_PATCHED
    if _CLICK_PROMPTS_PATCHED:
        return

    termui = click.termui

    def prompt(
        text: str,
        default: object | None = None,
        hide_input: bool = False,
        confirmation_prompt: bool | str = False,
        type: object | None = None,
        value_proc: object | None = None,
        prompt_suffix: str = ": ",
        show_default: bool = True,
        err: bool = False,
        show_choices: bool = True,
    ) -> object:
        def prompt_func(prompt_text: str) -> str:
            reader = (
                termui.hidden_prompt_func if hide_input else termui.visible_prompt_func
            )
            try:
                return reader(prompt_text)
            except (KeyboardInterrupt, EOFError):
                if hide_input:
                    termui.echo(None, err=err)
                raise click.Abort() from None

        if value_proc is None:
            value_proc = termui.convert_type(type, default)

        built_prompt = termui._build_prompt(
            text, prompt_suffix, show_default, default, show_choices, type
        )

        if confirmation_prompt:
            if confirmation_prompt is True:
                confirmation_prompt = termui._("Repeat for confirmation")
            confirmation_prompt = termui._build_prompt(
                confirmation_prompt,
                prompt_suffix,
            )

        while True:
            while True:
                value = prompt_func(built_prompt)
                if value:
                    break
                if default is not None:
                    value = default
                    break
            try:
                result = value_proc(value)
            except click.UsageError as e:
                if hide_input:
                    termui.echo(
                        termui._("Error: The value you entered was invalid."),
                        err=err,
                    )
                else:
                    termui.echo(termui._("Error: {e.message}").format(e=e), err=err)
                continue
            if not confirmation_prompt:
                return result
            while True:
                value2 = prompt_func(confirmation_prompt)
                is_empty = not value and not value2
                if value2 or is_empty:
                    break
            if value == value2:
                return result
            termui.echo(
                termui._("Error: The two entered values do not match."), err=err
            )

    def confirm(
        text: str,
        default: bool | None = False,
        abort: bool = False,
        prompt_suffix: str = ": ",
        show_default: bool = True,
        err: bool = False,
    ) -> bool:
        built_prompt = termui._build_prompt(
            text,
            prompt_suffix,
            show_default,
            "y/n" if default is None else ("Y/n" if default else "y/N"),
        )

        while True:
            try:
                value = termui.visible_prompt_func(built_prompt).lower().strip()
            except (KeyboardInterrupt, EOFError):
                raise click.Abort() from None
            if value in ("y", "yes"):
                rv = True
            elif value in ("n", "no"):
                rv = False
            elif default is not None and value == "":
                rv = default
            else:
                termui.echo(termui._("Error: invalid input"), err=err)
                continue
            break
        if abort and not rv:
            raise click.Abort()
        return rv

    click.prompt = prompt
    click.confirm = confirm
    termui.prompt = prompt
    termui.confirm = confirm
    click.core.prompt = prompt
    click.core.confirm = confirm
    _CLICK_PROMPTS_PATCHED = True


def enable_terminal_line_editing() -> None:
    """为 Click 的文本 prompt 启用 POSIX 行编辑。

    Click 可见输入默认走 ``input()``。在类 Unix 终端中，除了加载
    ``readline``，还需要把 Click 的 prompt 修补为“整行传给 input”，
    否则左右键编辑时会发生提示词覆盖和输入错位。

    Windows 保持 no-op，避免引入额外依赖。
    """
    if sys.platform == "win32":
        return

    try:
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            return
    except Exception:
        return

    try:
        importlib.import_module("readline")
    except Exception:
        return

    _patch_click_visible_prompts()


__all__ = ["enable_terminal_line_editing"]
