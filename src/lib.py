# -*- coding: utf-8 -*-
"""
    ssp.lib
    ~~~~~~~~

    Lib function.

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

import click
import traceback
from tool import Logger, get_redis_connect, url_check, gen_rediskey, md5, get_current_timestamp, email_check, try_request, Universal_pat

logger = Logger("sys").getLogger
IndexKey = gen_rediskey("index")


def get_systems():
    """查询系统状态"""
    pipe = get_redis_connect.pipeline()
    for key in get_redis_connect.smembers(IndexKey):
        pipe.hgetall(key)
    try:
        data = pipe.execute()
    except Exception as e:
        logger.error(e, exc_info=True)
        return False
    else:
        return [sd for sd in data if sd]


def get_panels(systems=None):
    """查询状态不正常的系统"""
    s2, s3, s4 = [], [], []
    if not systems:
        systems = get_systems()
    if systems and isinstance(systems, list):
        for sd in systems:
            if sd["status"] not in ("0", "1", 0, 1):
                if sd["status"] in (4, "4"):
                    s4.append(sd.get("name", sd["url"]))
                elif sd["status"] in (3, "3"):
                    s3.append(sd.get("name", sd["url"]))
                elif sd["status"] in (2, "2"):
                    s2.append(sd.get("name", sd["url"]))
    if s2 or s3 or s4:
        return {"2": s2, "3": s3, "4": s4}
    else:
        return dict()


def run_add_system(url, name='', ok_status_code=200, is_json=False, verify_success_key="", verify_success_value="", verify_success_text="", email="", isCli=False):
    """添加一条监控状态的网址

    # 状态监控流程：
    # NO.1 请求url，返回状态码，与ok_status_code一致表示响应成功，继续NO.2，否则url异常
    # NO.2 A - 如果是json，获取verify-success-key值与verify-success-value比对，一致表示业务正常，否则业务异常
    # NO.2 B - 如果不是json，用verify-success-text与返回内容校验，存在表示业务正常，否则业务异常

    # 数据字段解释：
    # sid - url的name，未传递时则为urlMD5值，唯一
    # status - 0：等待检测  1：检测正常  2：状态异常  3：业务异常  4：性能下降
    # elapsed - 响应时间
    """
    res = dict(code=1, msg=None)
    if url_check(url):
        if email:
            if not email_check(email):
                res.update(msg="请输入有效的邮箱")
                if isCli is True:
                    click.echo(click.style(res["msg"], fg='red'))
                    return
                else:
                    return res
        if name:
            if not Universal_pat.match(name):
                res.update(msg="请输入字母、数字和下划线的有效组合")
                if isCli is True:
                    click.echo(click.style(res["msg"], fg='red'))
                    return
                else:
                    return res
        sid = name or md5(url)
        SysKey = gen_rediskey("system", sid)
        if get_redis_connect.sismember(IndexKey, SysKey):
            res.update(msg="URL已在监控状态")
        else:
            pipe = get_redis_connect.pipeline()
            pipe.sadd(IndexKey, SysKey)
            pipe.hmset(SysKey, dict(sid=sid, url=url, name=name, status=0, method="get", ctime=get_current_timestamp(), email=email, ok_status_code=ok_status_code, is_json=1 if is_json else 0, verify_success_key=verify_success_key, verify_success_value=verify_success_value, verify_success_text=verify_success_text))
            try:
                pipe.execute()
            except:
                if isCli is True:
                    traceback.print_exc()
                else:
                    res.update(msg="系统异常")
            else:
                res.update(code=0, sid=sid)
    else:
        res.update(msg="请输入有效的URL")

    if isCli is True:
        if res["code"] == 0:
            click.echo(click.style("成功添加状态监控", fg='green'))
        else:
            click.echo(click.style(res["msg"], fg='red'))
    else:
        return res


def run_check(sid_or_url=None):
    """运行一次检测"""
    if not sid_or_url:
        systems = get_systems()
    else:
        if url_check(sid_or_url):
            sid = md5(sid_or_url)
        else:
            sid = sid_or_url
        data = get_redis_connect.hgetall(gen_rediskey("system", sid))
        if not data:
            click.echo(click.style("未发现网址", fg='red'))
            return
        else:
            systems = []
    if systems:
        if isinstance(systems, list):
            for sd in systems:
                ud = dict(vtime=get_current_timestamp())
                try:
                    resp = try_request(sd["url"], method="get")
                except Exception as e:
                    logger.error(e, exc_info=True)
                    ud.update(check_msg=str(e), status=2)
                else:
                    if resp.status_code == int(sd["ok_status_code"]):
                        # 状态码检测通过
                        if sd["is_json"] in ("True", "true", True, "1", 1):
                            try:
                                resp_json = resp.json()
                            except ValueError:
                                ud.update(check_msg="Not a valid json string", status=3)
                            else:
                                if sd["verify_success_key"]:
                                    try:
                                        resp_json_kv = resp_json[sd["verify_success_key"]]
                                    except IndexError:
                                        ud.update(check_msg="No such field: " + sd["verify_success_key"], status=3)
                                    else:
                                        if isinstance(resp_json_kv, int):
                                            resp_json_kv = str(resp_json_kv)
                                        if resp_json_kv == sd["verify_success_value"]:
                                            ud.update(status=1)
                                        else:
                                            ud.update(check_msg="The field value of the response data does not match the preset", status=3)
                                else:
                                    ud.update(status=1)
                        else:
                            resp_text = resp.text
                            if sd["verify_success_text"]:
                                vt = sd["verify_success_text"]
                                if isinstance(vt, str):
                                    vt = vt.decode("utf8")
                                if vt in resp_text:
                                    ud.update(status=1)
                                else:
                                    ud.update(check_msg="No preset values ​​found in response data", status=4)
                            else:
                                ud.update(status=1)
                    else:
                        ud.update(status=2)
                    if ud.get("status") == 1:
                        # 当请求正常时，写入请求时间，在运行波动范围内（RANGE_TIME）计算性能是否下降
                        RANGE_TIME = 0.1
                        resp_time = resp.elapsed.total_seconds()
                        last_time = float(sd.get("total_seconds", 0))
                        if last_time != 0:
                            if resp_time > last_time + RANGE_TIME:
                                ud.update(status=4)
                        ud.update(total_seconds=resp_time, check_msg='')
                finally:
                    # 更新检测结果
                    SysKey = gen_rediskey("system", sd["sid"])
                    try:
                        get_redis_connect.hmset(SysKey, ud)
                    except Exception as e:
                        logger.error(e, exc_info=True)
                        click.echo(click.style("检测结果更新失败：" + sd["sid"], fg='red'))


def run_remove_system(sid_or_url):
    """删除一条监控状态的网址"""
    if sid_or_url:
        if url_check(sid_or_url):
            sid = md5(sid_or_url)
        else:
            sid = sid_or_url
        SysKey = gen_rediskey("system", sid)
        data = get_redis_connect.hgetall(SysKey)
        if not data:
            click.echo(click.style("未发现网址", fg='red'))
        else:
            pipe = get_redis_connect.pipeline()
            pipe.srem(IndexKey, SysKey)
            pipe.delete(SysKey)
            try:
                pipe.execute()
            except:
                click.echo(click.style("删除失败", fg='red'))
            else:
                click.echo(click.style("删除成功", fg='green'))
    else:
        click.echo(click.style("无效参数", fg='red'))
