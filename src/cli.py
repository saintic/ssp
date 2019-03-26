#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    ssp.cli
    ~~~~~~~~~~~~~~

    Cli Entrance

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

import click
from lib import run_add_system, run_check, run_remove_system


@click.group()
def cli():
    pass


@cli.command()
@click.option("--ok-status-code", "-ok", default=200, type=int, help=u"响应成功状态码", show_default=True)
@click.option("--json/--no-json", default=False, help=u"是否返回JSON数据", show_default=True)
@click.option("--verify-success-key", '-vsk', help=u"仅--json时有效，表示检验业务正常响应的字段名")
@click.option("--verify-success-value", '-vsv', help=u"仅--json时有效，表示检验业务正常响应的字段值")
@click.option("--verify-success-text", '-vst', help=u"仅--no-json时有效，表示检验业务正常响应的文本")
@click.option("--email", help=u"异常时接收报警的邮箱")
@click.option("--name", help=u"可以作为唯一标识名，建议设置！")
@click.argument("url")
def add_system(ok_status_code, json, verify_success_key, verify_success_value, verify_success_text, email, name, url):
    """添加一条监控状态的网址"""
    run_add_system(url, name or '', ok_status_code, json, verify_success_key or '', verify_success_value or '', verify_success_text or '', email or '', True)


@cli.command()
@click.option("--name_or_url", '-sid', help=u"根据name或url删除一条监控项")
def remove_system(name_or_url):
    """删除一条监控状态的网址"""
    run_remove_system(name_or_url)


@cli.command()
@click.option("--name_or_url", '-sid', help=u"根据name或url单独检测")
def check(name_or_url):
    """运行一次状态检测"""
    run_check(name_or_url)


if __name__ == "__main__":
    cli()
