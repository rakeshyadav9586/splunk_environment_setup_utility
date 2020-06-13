import logging
import os

access_rights = 0o755
filepath = os.path.abspath(__file__)

logger_path = filepath.rsplit("/", 2)[0] + "/log"

if not os.path.isdir(logger_path):
    os.mkdir(logger_path, access_rights)

BASEPATH, current_filename = os.path.split(filepath)

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")


def setup_logger(name, level=logging.INFO):
    handler = logging.FileHandler(logger_path + "/All_in_One.log")
    handler.setFormatter(formatter)

    rk_logger = logging.getLogger(name)
    rk_logger.setLevel(level)
    rk_logger.addHandler(handler)

    return rk_logger


def ui_log_write():
    with open(BASEPATH + "/ui_log.log", "w") as rk:
        rk.write(
            "Hey, If any task is in progress then your task is in queue so, keep calm and observe log :-)\n"
        )
    for i in range(10):
        for i in range(98):
            with open(BASEPATH + "/ui_log.log", "a") as rk:
                rk.write("*")
        with open(BASEPATH + "/ui_log.log", "a") as rk:
            rk.write("\n")


def ui_log_append(message):
    with open(BASEPATH + "/ui_log.log", "a") as rk:
        rk.write(message)


def result_log_write(result_log_path):
    with open(result_log_path, "w") as rk:
        rk.write("\n")
    for i in range(10):
        for i in range(98):
            with open(result_log_path, "a") as rk:
                rk.write("*")
        with open(result_log_path, "a") as rk:
            rk.write("\n")


def result_log_append(result_log_path, message):
    print(result_log_path)
    with open(result_log_path, "a") as rk:
        rk.write(message)
