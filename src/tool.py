# -*- coding: utf-8 -*-
"""
    ssp.tool
    ~~~~~~~~

    Common function.

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

import os
import re
import hashlib
import time
import requests
import logging
import logging.handlers
from uuid import uuid4
from redis import from_url
from version import __version__
from config import REDIS as REDIS_URL, LOGLEVEL

mail_pat = re.compile(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$')
comma_pat = re.compile(r"\s*,\s*")
Universal_pat = re.compile(r"^[a-zA-Z\_][0-9a-zA-Z\_]*$")
get_redis_connect = from_url(REDIS_URL)


def md5(pwd):
    return hashlib.md5(pwd).hexdigest()


def gen_rediskey(*args):
    return "ssp:" + ":".join(map(str, args))


def gen_requestId():
    return str(uuid4())


def get_current_timestamp():
    """ 获取本地当前时间戳(10位): Unix timestamp：是从1970年1月1日（UTC/GMT的午夜）开始所经过的秒数，不考虑闰秒 """
    return int(time.time())


def makedir(d):
    if not os.path.exists(d):
        os.makedirs(d)
    if os.path.exists(d):
        return True
    else:
        return False


def email_check(email):
    if email and isinstance(email, (str, unicode)):
        return mail_pat.match(email)


def url_check(addr):
    """检测UrlAddr是否为有效格式，例如
    http://ip:port
    https://abc.com
    """
    regex = re.compile(
        r'^(?:http)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if addr and isinstance(addr, (str, unicode)):
        if regex.match(addr):
            return True
    return False


def try_request(url, params=None, data=None, timeout=5, num_retries=1, method='post'):
    """
    @params dict: 请求查询参数
    @data dict: 提交表单数据
    @timeout int: 超时时间，单位秒
    @num_retries int: 超时重试次数
    """
    headers = {"User-Agent": "Mozilla/5.0 (X11; CentOS; Linux i686; rv:7.0.1406) Gecko/20100101 ssp/{}".format(__version__)}
    method_func = requests.get if method == 'get' else requests.post
    try:
        resp = method_func(url, params=params, headers=headers, timeout=timeout, data=data)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        if num_retries > 0:
            return try_request(url, params=params, data=data, timeout=timeout, num_retries=num_retries-1)
        else:
            raise
    except requests.exceptions.RequestException:
        raise
    except Exception as e:
        raise
    else:
        if resp:
            return resp
        else:
            raise


class Logger:

    def __init__(self, logName, backupCount=10):
        self.logName = logName
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        self.logFile = os.path.join(self.log_dir, '%s.log' % self.logName)
        self._levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self._logfmt = '%Y-%m-%d %H:%M:%S'
        self._logger = logging.getLogger(self.logName)
        makedir(self.log_dir)

        handler = logging.handlers.TimedRotatingFileHandler(filename=self.logFile,
                                                            backupCount=backupCount,
                                                            when="midnight")
        handler.suffix = "%Y%m%d"
        formatter = logging.Formatter('[ %(levelname)s ] %(asctime)s %(filename)s:%(lineno)d %(message)s', datefmt=self._logfmt)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(self._levels.get(LOGLEVEL, logging.INFO))

    @property
    def getLogger(self):
        return self._logger


def iconBind(status):
    status = int(status)
    if status == 0:
        return "unknown"
    elif status == 1:
        return "success"
    elif status == 4:
        return "warn"
    else:
        return "error"
