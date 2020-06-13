import subprocess
import paramiko
import os, glob
import getpass
import re
import stat
import difflib
from .log_util import setup_logger
from .log_util import ui_log_append as user_log
from .log_util import result_log_append as result_log


rk_logger = setup_logger("rocklock3")
client = paramiko.SSHClient()


class Connection3(object):
    def __init__(self, result_log_path, radio_button):
        self.result_log_path = result_log_path
        self.radio_button = radio_button

    def S3(self, host, host_user, host_pwd, idx):
        user = host_user
        user_pwd = host_pwd
        login_user = "admin"
        login_pwd = "admin123"

        Splunk_home = "/opt/splunk/bin/splunk "
        add_server = (
            Splunk_home
            + "add search-server https://"
            + idx
            + ":8089 -auth "
            + login_user
            + ":"
            + login_pwd
            + " -remoteUsername "
            + login_user
            + " -remotePassword "
            + login_pwd
        )
        print(add_server)
        remove_server = (
            Splunk_home
            + "remove search-server -auth "
            + login_user
            + ":"
            + login_pwd
            + " "
            + idx
            + ":8089"
        )
        print(remove_server)
        try:
            rk_logger.info("Distributed Setup/Remove started ")
            user_log("Distributed Setup/Remove started\n")
            result_log(self.result_log_path, "Distributed Setup/Remove started\n")
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, 22, username=user, password=user_pwd)
            print("==========Connected to Linux IP :" + str(host))
            if self.radio_button[0] == "Setup":
                rk_logger.info(
                    "Going to add " + str(idx) + " with Search head " + str(host)
                )
                user_log(
                    "Going to add " + str(idx) + " with Search head " + str(host) + "\n"
                )
                result_log(
                    self.result_log_path,
                    "Going to add "
                    + str(idx)
                    + " with Search head "
                    + str(host)
                    + "\n",
                )
                self.execute(add_server)
            else:
                rk_logger.info(
                    "Going to remove " + str(idx) + " from Search head " + str(host)
                )
                user_log(
                    "Going to remove "
                    + str(idx)
                    + " from Search head "
                    + str(host)
                    + "\n"
                )
                result_log(
                    self.result_log_path,
                    "Going to remove "
                    + str(idx)
                    + " from Search head "
                    + str(host)
                    + "\n",
                )
                self.execute(remove_server)

            rk_logger.info("Distributed Setup/Remove completed ")
            user_log("Distributed Setup/Remove completed\n")
            result_log(self.result_log_path, "Distributed Setup/Remove completed\n")

        except paramiko.SSHException:
            rk_logger.info(str(host) + " Connection error")
            user_log(str(host) + " Connection error\n")
            result_log(self.result_log_path, str(host) + " Connection error\n")

        finally:
            client.close()

    def execute(self, command):

        stdin, stdout, stderr = client.exec_command(command)

        for j, line in enumerate(stdout):
            line = line.rstrip()
            print("%s" % line)
            rk_logger.info("%s" % line)
            user_log("%s" % line + "\n")
            result_log(self.result_log_path, "%s" % line + "\n")
        for j, line in enumerate(stderr):
            line = line.rstrip()
            print("%s" % line)
            rk_logger.info("%s" % line)
            user_log("%s" % line + "\n")
            result_log(self.result_log_path, "%s" % line + "\n")
