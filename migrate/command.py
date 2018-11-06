import os
import fire

from .migration import set_version, get_versions, get_current_version, \
    set_history_version, version_dir, Migration

__db_version__ = "1.0.0.0"


def init():
    """初始化当前包里对应的数据库版本"""
    max_version = __db_version__.replace(".", "")
    Migration(max_version).init()


def up():
    """升级至当前包里对应的数据库版本"""
    max_version = __db_version__.replace(".", "")
    return up_to(max_version)


def up_to(version):
    """升级至指定的数据库版本"""
    curr, last = get_versions()
    set_history_version(curr)
    all_versions = sorted([x.split(".")[0][-4:] for x in os.listdir(version_dir)])
    versions = [x for x in all_versions if x <= version]
    while 1:
        current_version = get_current_version()
        next = Migration(current_version, versions).next
        if next:
            _, err_msg = next.up()
            if err_msg:
                return err_msg
            else:
                set_version(next.curr)
        else:
            return


def down():
    """基于当前版本，降级至上一个版本"""
    _, history = get_versions()
    err_msg = down_to(history)
    return err_msg


def down_to(version):
    """降级至指定的数据库版本

    策略: 从当前版本中的patch文件依次往下降版本，降级的sql中应该包含设置降级后的版本的sql
    """
    all_versions = sorted([x.split(".")[0][-4:] for x in os.listdir(version_dir)], reverse=True)
    while 1:
        current_version = get_current_version()
        if current_version <= version:
            return
        _, err_msg = Migration(current_version, all_versions).down()
        if err_msg:
            return err_msg

def main():
    fire.Fire()


if __name__ == '__main__':
    fire.Fire()
