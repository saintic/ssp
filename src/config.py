# -*- coding: utf-8 -*-
"""
    ssp.config
    ~~~~~~~~~~~

    The program configuration file, the preferred configuration item, reads the system environment variable first.

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

from os import getenv

# Configuration Information:
# The getenv function first reads the configuration from the environment variable. When no variable is found, the default value is used.
# getenv("environment variable", "default value")
# Progranm Name
PROCNAME = "ssp"
# Program listening host
HOST = getenv("ssp_host", "127.0.0.1")
# Program listening port
PORT = int(getenv("ssp_port", 13148))
# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOGLEVEL = getenv("ssp_loglevel", "INFO")
# REDIS connection information in the format: redis://[:password]@host:port/db
REDIS = getenv("ssp_redis_url", "")

# Web Site Config
SITE = {
    "logo": "/static/images/logo.png",
    "title": "SaintIC Status",
    "subtitle": "Web Status of SaintIC",
    "favicon": "https://img.saintic.com/cdn/images/favicon-32.png",
    "footer": "Copyright &copy;2019 <a href='https://www.saintic.com' target='_blank'>SaintIC</a>. All rights reserved."
}
