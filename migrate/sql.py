import pymysql

from .log import logger
from .utils import fn_timer, parse_conn


class SqlRunningError(Exception):
    pass


class Mysql(object):
    def __init__(self, conn_url):
        self.conn = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **parse_conn(conn_url))
        self.cursor = self.conn.cursor()

    @fn_timer
    def execute(self, sql, *args, **kwargs):
        logger.info(f"[execute]{sql}")
        self.cursor.execute(sql)
        self.conn.commit()
        self.close()
        logger.info(f"[execute]success")

    def do(self, sql, *args, **kwargs):
        """execute in transaction"""
        logger.info(f"[do]{sql}")
        self.cursor.execute(sql)

    def fetchone(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        self.close()
        return result

    def fetchall(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.close()
        return result

    def close(self):
        self.cursor.close()
        self.conn.close()

    def __enter__(self):
        self.conn.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"SqlRunningError: {exc_tb}")
            self.conn.rollback()
            self.close()
            raise SqlRunningError(str(exc_val))
        else:
            self.conn.commit()
            self.close()


if __name__ == "__main__":
    # check transaction
    with Mysql() as db:
        db.do("insert into user_table (`username`, `group_id`) values ('xia', '1');")
        db.do("update wahaha set a = 1 where id = 1;")