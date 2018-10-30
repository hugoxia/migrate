import os
import sys
import logging


def start_log(path, filename):
    log_path = os.path.abspath(path)
    os.makedirs(os.path.realpath(log_path), exist_ok=True)
    log_file = os.path.join(log_path, filename)
    logger = logging.getLogger("migrate")
    # create handler
    ch = logging.StreamHandler(sys.stdout)
    fh = logging.FileHandler(log_file)
    ch.setLevel("DEBUG")
    fh.setLevel("DEBUG")
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                '%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)
    # log into a file if it is a script
    logger.addHandler(fh)
    return logger

logger = start_log("/var/log", "db_migrate.log")
