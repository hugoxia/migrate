import os

from .sql import mysql_config, Mysql
from .log import logger
from .migration_sql import run_sql_migration

version_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "versions")
patch_dir = os.path.join(version_dir, "sql_patch")


def set_version(version):
    """设置当前版本信息(升级时设置当前版本信息)"""
    version = version.replace("V", "")
    version = ".".join(version)
    with Mysql() as db:
        db.do(f'update irain_park.alembic_version set version_num="{version}";')


def set_history_version(version):
    """设置历史版本信息(升级时设置初始版本信息)"""
    version = version.replace("V", "")
    version = ".".join(version)
    with Mysql() as db:
        db.do(f'update irain_park.alembic_version set last_version_num="{version}";')


def get_current_version():
    """获取当前数据库版本

    返回: 当前版本
    """
    query = Mysql().fetchone("select * from alembic_version;")
    if query:
        return query["version_num"].replace(".", "")
    else:
        err_msg = "record is not exist, check alembic_version."
        logger.error(err_msg)
        raise Exception(err_msg)


def get_versions():
    """获取数据库版本信息

    返回: 当前版本, 历史版本
    """
    query = Mysql().fetchone("select * from alembic_version;")
    if query:
        return query["version_num"].replace(".", ""), query["last_version_num"].replace(".", "")
    else:
        err_msg = "record is not exist, check alembic_version."
        logger.error(err_msg)
        raise Exception(err_msg)


class Migration(object):
    def __init__(self, curr: str, versions=None):
        self.curr = curr
        self.versions = versions
        self.source = os.path.join(patch_dir, f"patch_V{self.curr}.sql")

    @property
    def prev(self):
        for v in self.versions:  # desc
            if v < self.curr:
                return Migration(v, versions=self.versions)
        else:
            return None

    @property
    def next(self):
        for v in self.versions:  # asc
            if v > self.curr:
                return Migration(v, versions=self.versions)
        else:
            return None

    def init(self):
        path = os.path.join(version_dir, f"V{self.curr}.sql")
        with Mysql() as db:
            db.do("flush tables")
            cmd = f"mysql -h{mysql_config['host']} -uroot -p{mysql_config['password']} " \
                  f"{mysql_config['database']} < {path}"
            status_code = os.system(cmd)
            if status_code != 0:
                logger.error("init error")
                raise Exception("init error")
            else:
                logger.info("init success")

    def up(self):
        err_msg = self.run(True)
        return 1, err_msg

    def down(self):
        err_msg = self.run(False)
        return 1, err_msg

    def run(self, direction: bool):
        return run_sql_migration(self.source, direction)

    def __repr__(self):
        return ""

    __str__ = __repr__


