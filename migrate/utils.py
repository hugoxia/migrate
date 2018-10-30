import time

from functools import wraps
from urllib.parse import urlparse
from .log import logger

def fn_timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time() * 1000
        logger.info(f"[{func.__name__}] start running...")
        ret = func(*args, **kwargs)
        cost = time.time() * 1000 - start
        logger.info(f"[{func.__name__}] end, cost {cost} ms")
        return ret
    return wrapper


def parse_conn(conn_url):
    r = urlparse(conn_url)
    config = dict(
        host=r.hostname,
        user=r.username,
        password=r.password,
        database=r.path.split("/")[-1],
        charset="utf8"
    )
    return config 
