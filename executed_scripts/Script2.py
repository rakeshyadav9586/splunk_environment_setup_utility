import subprocess
import threading
from queue import Queue
import paramiko
import os, glob
import getpass
import re
import stat
import difflib
from .log_util import setup_logger
from .log_util import ui_log_append as user_log
from .log_util import result_log_append as result_log

rk_logger = setup_logger("rocklock2")
filepath = os.path.abspath(__file__)
status_path = str(filepath.rsplit("/", 2)[0]) + "/Splunk_Status/"
access_rights = 0o755
if not os.path.isdir(status_path):
    os.mkdir(status_path, access_rights)


class Connection2(object):
    def __init__(self, host, host_usr, host_pwd, result_log_path):
        self.host_usr = host_usr
        self.host_pwd = host_pwd
        self.host = host
        self.result_log_path = result_log_path
        self.all_status = []
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            self.host, 22, username=self.host_usr, password=self.host_pwd
        )
        self.r_sftp = self.client.open_sftp()

    def S2(self, Splunk_version, radio, Splunk_path, log_path, raw_ip_list):
        print("from script2 method")
        dest_path = "/opt/"
        main_dir = "opt"
        all_app_dirs = []
        Splunk_dir_name = dest_path + "splunk/bin"

        copy = [
            "sshpass -p "
            + self.host_pwd
            + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
            + Splunk_path
            + "/"
            + Splunk_version
            + " root@"
            + self.host
            + ":"
            + dest_path
        ]
        print(copy)

        get_version = Splunk_version[7:10]

        Splunk_Home = " /opt/splunk/bin/splunk "
        Splunk_Stop = Splunk_Home + "stop "
        Splunk_Removed = " rm -rf /opt/splunk "
        Splunk_untar = " tar xvzf /opt/" + Splunk_version + " -C /opt/ "
        Splunk_new_version = (
            Splunk_Home
            + "start --accept-license --answer-yes --no-prompt --seed-passwd admin123 "
        )
        Splunk_old_version = Splunk_Home + "start --accept-license "
        Splunk_old_pass_update = (
            Splunk_Home + "edit user admin -password admin123 -auth admin:changeme "
        )
        Splunk_Restart = Splunk_Home + "restart "

        command_Old_install = (
            Splunk_untar + "&&" + Splunk_old_version + "&&" + Splunk_old_pass_update
        )
        command_Old_install_stop = (
            Splunk_Stop
            + "&&"
            + Splunk_untar
            + "&&"
            + Splunk_old_version
            + "&&"
            + Splunk_old_pass_update
        )
        command_Old_reinstall_stop = (
            Splunk_Stop
            + "&&"
            + Splunk_Removed
            + "&&"
            + Splunk_untar
            + "&&"
            + Splunk_old_version
            + "&&"
            + Splunk_old_pass_update
        )

        command_New_install = Splunk_untar + "&&" + Splunk_new_version
        command_New_install_stop = (
            Splunk_Stop + "&&" + Splunk_untar + "&&" + Splunk_new_version
        )
        command_New_reinstall_stop = (
            Splunk_Stop
            + "&&"
            + Splunk_Removed
            + "&&"
            + Splunk_untar
            + "&&"
            + Splunk_new_version
        )

        try:
            self.execute("cd ..; pwd")
            self.r_sftp.chdir("/")

            for folder in self.r_sftp.listdir():
                all_app_dirs.append(folder)
            print(all_app_dirs)

            matched_file = difflib.get_close_matches(main_dir, all_app_dirs)

            print(matched_file)
            if matched_file:
                rk_logger.info(
                    self.host + ": " + Splunk_version + ": File transfer started"
                )
                user_log(
                    self.host + ": " + Splunk_version + ": File transfer started\n"
                )
                result_log(
                    self.result_log_path,
                    self.host + ": " + Splunk_version + ": File transfer started\n",
                )

                copy = [
                    "sshpass -p "
                    + self.host_pwd
                    + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
                    + Splunk_path
                    + "/"
                    + Splunk_version
                    + " root@"
                    + self.host
                    + ":"
                    + dest_path
                ]
                copy_status = subprocess.check_call(copy, shell=True)

                rk_logger.info(
                    self.host + ": " + Splunk_version + ": File transfer completed"
                )
                user_log(
                    self.host + ": " + Splunk_version + ": File transfer completed\n"
                )
                result_log(
                    self.result_log_path,
                    self.host + ": " + Splunk_version + ": File transfer completed\n",
                )

                self.status_check(Splunk_Stop)
                with open(status_path + self.host + "splunk_status.txt", "r") as rk:
                    verify_status = rk.read()
                    print(verify_status)
                self.all_status = re.findall(
                    r"(?:\bNo such file or directory\b|\bShutting down\b|\bis not running\b)",
                    str(verify_status),
                )
                print("found " + str(self.all_status))

                if str(self.all_status[0]) == "No such file or directory":
                    print("No such file or directory")

                    rk_logger.info(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk fresh installation started as splunk not installed"
                    )
                    user_log(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk fresh installation started as splunk not installed\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk fresh installation started as splunk not installed\n",
                    )

                    self.final_execute(
                        get_version, command_New_install, command_Old_install
                    )

                    rk_logger.info(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk fresh installation completed"
                    )
                    user_log(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk fresh installation completed\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk fresh installation completed\n",
                    )

                elif str(radio[0]) == "Install":
                    print("Install loop")

                    rk_logger.info(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Installation started"
                    )
                    user_log(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Installation started\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Installation started\n",
                    )

                    self.final_execute(
                        get_version, command_New_install_stop, command_Old_install_stop
                    )

                    rk_logger.info(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Installation completed"
                    )
                    user_log(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Installation completed\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Installation completed\n",
                    )

                else:
                    print("reinstall loop")

                    rk_logger.info(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Reinstallation started"
                    )
                    user_log(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Reinstallation started\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Reinstallation started\n",
                    )

                    self.final_execute(
                        get_version,
                        command_New_reinstall_stop,
                        command_Old_reinstall_stop,
                    )

                    rk_logger.info(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Reinstallation completed"
                    )
                    user_log(
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Reinstallation completed\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + Splunk_version
                        + ": Splunk Reinstallation completed\n",
                    )

            else:
                rk_logger.info(
                    self.host + " : /opt directory not there so going to create\n"
                )
                user_log(self.host + " : /opt directory not there so going to create\n")
                result_log(
                    self.result_log_path,
                    self.host + " : /opt directory not there so going to create\n",
                )

                self.execute("cd ..;pwd; mkdir " + main_dir)

                rk_logger.info(
                    self.host + ": " + Splunk_version + ": File transfer started"
                )
                user_log(
                    self.host + ": " + Splunk_version + ": File transfer started\n"
                )
                result_log(
                    self.result_log_path,
                    self.host + ": " + Splunk_version + ": File transfer started\n",
                )

                copy = [
                    "sshpass -p "
                    + self.host_pwd
                    + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
                    + Splunk_path
                    + "/"
                    + Splunk_version
                    + " root@"
                    + self.host
                    + ":"
                    + dest_path
                ]
                copy_status = subprocess.check_call(copy, shell=True)

                rk_logger.info(
                    self.host + ": " + Splunk_version + ": File transfer completed"
                )
                user_log(
                    self.host + ": " + Splunk_version + ": File transfer completed\n"
                )
                result_log(
                    self.result_log_path,
                    self.host + ": " + Splunk_version + ": File transfer completed\n",
                )

                rk_logger.info(
                    self.host
                    + ": "
                    + Splunk_version
                    + ": Splunk fresh installation started after creating the /opt directory"
                )
                user_log(
                    self.host
                    + ": "
                    + Splunk_version
                    + ": Splunk fresh installation started after creating the /opt directory\n"
                )
                result_log(
                    self.result_log_path,
                    self.host
                    + ": "
                    + Splunk_version
                    + ": Splunk fresh installation started after creating the /opt directory\n",
                )

                self.final_execute(
                    get_version, command_New_install, command_Old_install
                )

                rk_logger.info(
                    self.host
                    + ": "
                    + Splunk_version
                    + ": Splunk fresh installation completed after creating the /opt directory"
                )
                user_log(
                    self.host
                    + ": "
                    + Splunk_version
                    + ": Splunk fresh installation completed after creating the /opt directory\n"
                )
                result_log(
                    self.result_log_path,
                    self.host
                    + ": "
                    + Splunk_version
                    + ": Splunk fresh installation completed after creating the /opt directory\n",
                )

        except OSError as e:
            print("ERROR :", e)
            rk_logger.info(self.host + ": ERROR :", e)
            user_log(self.host + ": OS ERROR \n")
            result_log(self.result_log_path, self.host + ": OS ERROR \n")

        except subprocess.CalledProcessError as f:
            print("ERROR: ", f)
            rk_logger.info(self.host + ": ERROR :", f)
            user_log(self.host + ": Subprocess ERROR \n")
            result_log(self.result_log_path, self.host + ": Subprocess ERROR \n")

        finally:
            print("finally called " + str(self.host))
            self.r_sftp.close()
            self.client.close()

    def final_execute(self, get_version, command1, command2):
        if (float(get_version)) > 7.0:
            self.execute(command1)
        else:
            print("below 7.0")
            self.execute(command2)

    def execute(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        for i, line in enumerate(stdout):
            line = line.rstrip()
            print("%s" % line)
        for i, line in enumerate(stderr):
            line = line.rstrip()
            print("%s" % line)

    def status_check(self, command):
        with open(status_path + self.host + "splunk_status.txt", "w") as rk:
            rk.write("")
        stdin, stdout, stderr = self.client.exec_command(command)
        for i, line in enumerate(stdout):
            line = line.rstrip()
            with open(status_path + self.host + "splunk_status.txt", "a") as rk:
                rk.write(line)
            print("%s" % line)
        for i, line in enumerate(stderr):
            line = line.rstrip()
            with open(status_path + self.host + "splunk_status.txt", "a") as rk:
                rk.write(line)
            print("%s" % line)
