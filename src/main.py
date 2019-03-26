# -*- coding: utf-8 -*-
"""
    ssp
    ~~~~

    Simple Status Page

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

from redis import from_url
from flask import Flask, render_template
from config import HOST, PORT, REDIS, SITE
from version import __version__
from lib import get_systems, get_panels
from tool import iconBind

__author__ = 'staugur'
__email__ = 'staugur@saintic.com'
__date__ = '2019-03-25'

app = Flask(__name__)
redis = from_url(REDIS)


@app.context_processor
def GlobalTemplateVariables():
    data = {"Version": __version__, "Author": __author__, "Email": __email__, "SITE": SITE, "iconBind": iconBind}
    return data


@app.route("/")
def index():
    # systems - 所有注册的web
    # panels - systems中有问题的
    # incidents - 人工维护的故障事件
    systems = get_systems()
    panels = get_panels(systems)
    return render_template("index.html", systems=systems, panels=panels, incidents={})


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
