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

rk_logger = setup_logger("rocklock5")


class Connection5(object):
    def __init__(self, result_log_path):
        self.result_log_path = result_log_path

    def S5(self, host, host_user, host_pwd):
        keys = ["master", "Deployer", "IDX1", "IDX2", "IDX3", "SH1", "SH2", "SH3"]
        IP_Dict = {
            "master": host[0],
            "Deployer": host[1],
            "IDX1": host[2],
            "IDX2": host[3],
            "IDX3": host[4],
            "SH1": host[5],
            "SH2": host[6],
            "SH3": host[7],
        }

        user = host_user
        user_pwd = host_pwd
        login_pwd = "admin:admin123 "

        Splunk_home = "/opt/splunk/bin/splunk "
        Splunk_Restart = " /opt/splunk/bin/splunk restart "

        rk_logger.info("Cluster Setup started")
        user_log("Cluster Setup started\n")
        result_log(self.result_log_path, "Cluster Setup started\n")

        for i in keys:
            make_cluster_master = (
                Splunk_home
                + "edit cluster-config -mode master -replication_factor 3 -search_factor 2 -auth "
                + login_pwd
                + "&&"
                + Splunk_Restart
            )

            connect_idx_master = (
                Splunk_home
                + "edit cluster-config -mode slave -master_uri https://"
                + IP_Dict.get("master")
                + ":8089 -replication_port 8080 -auth "
                + login_pwd
                + "&&"
                + Splunk_Restart
            )

            connect_sh_master_deployer = (
                Splunk_home
                + "edit cluster-config -mode searchhead -master_uri https://"
                + IP_Dict.get("master")
                + ":8089 -auth "
                + login_pwd
                + "&&"
                + Splunk_Restart
                + "&& "
                + Splunk_home
                + "init shcluster-config -replication_port 8087 -mgmt_uri https://"
                + IP_Dict.get(i)
                + ":8089 -conf_deploy_fetch_url https://"
                + IP_Dict.get("Deployer")
                + ":8089 -auth "
                + login_pwd
                + "&&"
                + Splunk_Restart
            )

            sh_captain = (
                Splunk_home
                + "bootstrap shcluster-captain -servers_list 'https://"
                + IP_Dict.get("SH1")
                + ":8089,https://"
                + IP_Dict.get("SH2")
                + ":8089,https://"
                + IP_Dict.get("SH3")
                + ":8089' -auth "
                + login_pwd
            )

            connect_sh_master_deployer_captain = (
                Splunk_home
                + "edit cluster-config -mode searchhead -master_uri https://"
                + IP_Dict.get("master")
                + ":8089 -auth "
                + login_pwd
                + "&&"
                + Splunk_Restart
                + "&& "
                + Splunk_home
                + "init shcluster-config -replication_port 8087 -mgmt_uri https://"
                + IP_Dict.get(i)
                + ":8089 -conf_deploy_fetch_url https://"
                + IP_Dict.get("Deployer")
                + ":8089 -auth "
                + login_pwd
                + "&&"
                + Splunk_Restart
                + "&& "
                + sh_captain
            )

            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(IP_Dict.get(i), 22, username=user, password=user_pwd)
                print("==========Connected to Linux IP :" + IP_Dict.get(i))

                if IP_Dict.get(i) == IP_Dict.get("master"):
                    print("master IP is " + IP_Dict.get(i))
                    print(make_cluster_master)
                    stdin, stdout, stderr = client.exec_command(make_cluster_master)

                    rk_logger.info(str(IP_Dict.get(i)) + " is set as Cluster Master")
                    user_log(str(IP_Dict.get(i)) + " is set as Cluster Master\n")
                    result_log(
                        self.result_log_path,
                        str(IP_Dict.get(i)) + " is set as Cluster Master\n",
                    )

                elif IP_Dict.get(i) == IP_Dict.get("IDX1"):
                    print("IDX1 IP is " + IP_Dict.get(i))
                    print(connect_idx_master)
                    stdin, stdout, stderr = client.exec_command(connect_idx_master)

                    rk_logger.info(str(IP_Dict.get(i)) + " is set as Indexer1")
                    user_log(str(IP_Dict.get(i)) + " is set as Indexer1\n")
                    result_log(
                        self.result_log_path,
                        str(IP_Dict.get(i)) + " is set as Indexer1\n",
                    )

                elif IP_Dict.get(i) == IP_Dict.get("IDX2"):
                    print("IDX2 IP is " + IP_Dict.get(i))
                    print(connect_idx_master)
                    stdin, stdout, stderr = client.exec_command(connect_idx_master)

                    rk_logger.info(str(IP_Dict.get(i)) + " is set as Indexer2")
                    user_log(str(IP_Dict.get(i)) + " is set as Indexer2\n")
                    result_log(
                        self.result_log_path,
                        str(IP_Dict.get(i)) + " is set as Indexer2\n",
                    )

                elif IP_Dict.get(i) == IP_Dict.get("IDX3"):
                    print("IDX3 IP is " + IP_Dict.get(i))
                    print(connect_idx_master)
                    stdin, stdout, stderr = client.exec_command(connect_idx_master)

                    rk_logger.info(str(IP_Dict.get(i)) + " is set as Indexer3")
                    user_log(str(IP_Dict.get(i)) + " is set as Indexer3\n")
                    result_log(
                        self.result_log_path,
                        str(IP_Dict.get(i)) + " is set as Indexer3\n",
                    )

                elif IP_Dict.get(i) == IP_Dict.get("SH1"):
                    print("SH1 IP is " + IP_Dict.get(i))
                    print(connect_sh_master_deployer)
                    stdin, stdout, stderr = client.exec_command(
                        connect_sh_master_deployer
                    )

                    rk_logger.info(str(IP_Dict.get(i)) + " is set as Search Head1")
                    user_log(str(IP_Dict.get(i)) + " is set as Search Head1\n")
                    result_log(
                        self.result_log_path,
                        str(IP_Dict.get(i)) + " is set as Search Head1\n",
                    )

                elif IP_Dict.get(i) == IP_Dict.get("SH2"):
                    print("SH2 IP is " + IP_Dict.get(i))
                    print(connect_sh_master_deployer)
                    stdin, stdout, stderr = client.exec_command(
                        connect_sh_master_deployer
                    )

                    rk_logger.info(str(IP_Dict.get(i)) + " is set as Search Head2")
                    user_log(str(IP_Dict.get(i)) + " is set as Search Head2\n")
                    result_log(
                        self.result_log_path,
                        str(IP_Dict.get(i)) + " is set as Search Head2\n",
                    )

                elif IP_Dict.get(i) == IP_Dict.get("SH3"):
                    print("SH3 IP is " + IP_Dict.get(i))
                    print(connect_sh_master_deployer_captain)
                    stdin, stdout, stderr = client.exec_command(
                        connect_sh_master_deployer_captain
                    )

                    rk_logger.info(
                        str(IP_Dict.get(i)) + " is set as Search Head3 and captain"
                    )
                    user_log(
                        str(IP_Dict.get(i)) + " is set as Search Head3 and captain\n"
                    )
                    result_log(
                        self.result_log_path,
                        str(IP_Dict.get(i)) + " is set as Search Head3 and captain\n",
                    )

                for j, line in enumerate(stdout):
                    line = line.rstrip()
                    print("%s" % line)
                for j, line in enumerate(stderr):
                    line = line.rstrip()
                    print("%s" % line)

                print("==========Set Up done on Linux IP :" + IP_Dict.get(i))

            except paramiko.SSHException:
                print("Error")
                rk_logger.info(str(IP_Dict.get(i)) + " Connection error")
                user_log(str(IP_Dict.get(i)) + " Connection error\n")
                result_log(
                    self.result_log_path, str(IP_Dict.get(i)) + " Connection error\n"
                )

            finally:
                client.close()

        rk_logger.info("Cluster Setup task completed")
        user_log("Cluster Setup task completed\n")
        result_log(self.result_log_path, "Cluster Setup task completed\n")

