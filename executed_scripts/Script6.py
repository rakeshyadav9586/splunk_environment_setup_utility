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

rk_logger = setup_logger("rocklock6")


class Connection6(object):
    def __init__(self, result_log_path):
        self.result_log_path = result_log_path

    def S6(self, host, host_user, host_pwd, app_names, app_path):

        keys = ["master", "Deployer"]
        IP_Dict = {"master": host[0], "Deployer": host[1]}

        SH3 = host[7]
        print(IP_Dict)
        print(SH3)
        app_names = list(map(lambda s: s.strip(), app_names))
        print(app_names)
        print(app_names[0])
        print(app_names[1])
        print(app_path)

        ssh_pwd = host_pwd
        app_names[0]
        app_names[1]
        src_path_ta = app_path + app_names[0]
        print(src_path_ta)
        src_path_app = app_path + app_names[1]
        print(src_path_app)

        dest_path_master = "/opt/splunk/etc/master-apps"
        des_path_shcluster = "/opt/splunk/etc/shcluster/apps"

        rk_logger.info("Started to push app on Cluster")
        user_log("Started to push app on Cluster\n")
        result_log(self.result_log_path, "Started to push app on Cluster\n")

        for i in keys:
            if (app_names[0]) and (IP_Dict.get(i) == IP_Dict.get("master")):
                copy = [
                    "sshpass -p "
                    + ssh_pwd
                    + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
                    + src_path_ta
                    + " root@"
                    + IP_Dict.get(i)
                    + ":"
                    + dest_path_master
                ]
                print(copy)

            elif (app_names[1]) and (IP_Dict.get(i) == IP_Dict.get("Deployer")):
                copy = [
                    "sshpass -p "
                    + ssh_pwd
                    + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
                    + src_path_app
                    + " root@"
                    + IP_Dict.get(i)
                    + ":"
                    + des_path_shcluster
                ]
                print(copy)

            try:
                copy_status = subprocess.check_call(copy, shell=True)
                print("Copy Success ")
            except Exception:
                rk_logger.info("Error while copy the app")
                user_log("Error while copy the app\n")
                result_log(self.result_log_path, "Error while copy the app\n")
                print("Error while Copy...")

            user = host_user
            user_pwd = host_pwd
            login_pwd = "admin:admin123"
            master_path = " /opt/splunk/etc/master-apps/"
            deployer_path = " /opt/splunk/etc/shcluster/apps/"
            splunk_home = "/opt/splunk/bin/splunk "

            deployer_push = (
                "tar -xvzf"
                + deployer_path
                + app_names[1]
                + " -C"
                + deployer_path
                + " && "
                + "rm -rf"
                + deployer_path
                + app_names[1]
                + " && "
                + splunk_home
                + "apply shcluster-bundle --answer-yes -target https://"
                + SH3
                + ":8089 -auth "
                + login_pwd
                + " && "
                + splunk_home
                + "show shcluster-status"
            )
            print("deployer" + deployer_push)

            master_push = (
                "tar -xvzf"
                + master_path
                + app_names[0]
                + " -C"
                + master_path
                + " && "
                + "rm -rf"
                + master_path
                + app_names[0]
                + " && "
                + splunk_home
                + "apply cluster-bundle --answer-yes -auth "
                + login_pwd
                + " && "
                + splunk_home
                + "show cluster-bundle-status -auth "
                + login_pwd
            )
            print("master command" + master_push)
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(IP_Dict.get(i), 22, username=user, password=user_pwd)
                print("==========Connected to Linux IP : " + IP_Dict.get(i))

                if (app_names[0]) and (IP_Dict.get(i) == IP_Dict.get("master")):
                    print("Master IP is " + IP_Dict.get(i))
                    stdin, stdout, stderr = client.exec_command(master_push)

                    rk_logger.info(
                        "Started to push app from Cluster Master "
                        + str(IP_Dict.get(i))
                        + " to indexer"
                    )
                    user_log(
                        "Started to push app from Cluster Master "
                        + str(IP_Dict.get(i))
                        + " to indexer\n"
                    )
                    result_log(
                        self.result_log_path,
                        "Started to push app from Cluster Master "
                        + str(IP_Dict.get(i))
                        + " to indexer\n",
                    )

                elif (app_names[1]) and (IP_Dict.get(i) == IP_Dict.get("Deployer")):
                    print("Deployer IP is " + IP_Dict.get(i))
                    stdin, stdout, stderr = client.exec_command(deployer_push)

                    rk_logger.info(
                        "Started to push app from Deployer "
                        + str(IP_Dict.get(i))
                        + " to search head"
                    )
                    user_log(
                        "Started to push app from Deployer "
                        + str(IP_Dict.get(i))
                        + " to search head\n"
                    )
                    result_log(
                        self.result_log_path,
                        "Started to push app from Deployer "
                        + str(IP_Dict.get(i))
                        + " to search head\n",
                    )

                for j, line in enumerate(stdout):
                    line = line.rstrip()
                    print("%s" % (line))
                for j, line in enumerate(stderr):
                    line = line.rstrip()
                    print("%s" % (line))
                print("==========App Push Successfully ")

            except Exception:
                print("Unable to Connect and Execute Command")

            finally:
                client.close()

        rk_logger.info("App push completed on Cluster")
        user_log("App push completed on Cluster\n")
        result_log(self.result_log_path, "App push completed on Cluster\n")
