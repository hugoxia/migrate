from io import StringIO

from .sql import Mysql, SqlRunningError
from .log import logger

SQL_CMD_PREFIX = "-- +db "


def get_sql_statements(source: str, direction: bool):
    """

    :param source:
    :param direction:
    :return:
        （statements，is_transaction）
    """
    buf = StringIO()
    up_sections = 0
    down_sections = 0

    statement_ended = False
    ignore_semicolons = False
    direction_is_active = False

    is_transaction = True

    statements = []
    logger.info(f"Read file: {source}")
    with open(source, "r") as f:
        for line in f.readlines():
            line = line.strip()
            logger.debug(f"|{line}")
            if line.startswith(SQL_CMD_PREFIX):
                cmd = line[len(SQL_CMD_PREFIX):].strip()
                if cmd == "UP":
                    direction_is_active = bool(direction is True)
                    up_sections += 1
                elif cmd == "DOWN":
                    direction_is_active = bool(direction is False)
                    down_sections += 1
                elif cmd == "StatementBegin":
                    if direction_is_active:
                        ignore_semicolons = True
                elif cmd == "StatementEnd":
                    if direction_is_active:
                        statement_ended = bool(ignore_semicolons is True)
                        ignore_semicolons = False
                elif cmd == "NO TRANSACTION":
                    is_transaction = False
                else:
                    continue

                continue

            if not direction_is_active:
                continue

            buf.write(f"{line} ")  # 防止sql换行, 增加一个空格

            if (not ignore_semicolons and line.endswith(";")) or statement_ended:
                statement_ended = False
                statements.append(buf.getvalue().strip())
                buf.truncate(0)

    if ignore_semicolons:
        logger.warn("saw '-- +db StatementBegin' with no matching '-- +db StatementEnd'")

    buf_remaining = buf.getvalue().strip()
    if len(buf_remaining) > 0:
        logger.warn(f"Unexpected unfinished SQL query: {buf_remaining}. Missing a semicolon?")

    if up_sections == 0 and down_sections == 0:
        logger.error("no Up/Down annotations found, so no statements were executed.")

    buf.close()

    return statements, is_transaction


def run_sql_migration(source, direction):
    statements, is_transaction = get_sql_statements(source, direction)
    if is_transaction:
        try:
            with Mysql() as db:
                for query in statements:
                    db.do(query)
        except SqlRunningError as e:
            return e
        except Exception as e:
            return str(e)
        else:
            return ""
    else:
        db = Mysql()
        for query in statements:
            db.execute(query)
        return ""

