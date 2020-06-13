import subprocess
import paramiko
import os
import getpass
import stat
import difflib
from .log_util import setup_logger
from .log_util import ui_log_append as user_log
from .log_util import result_log_append as result_log

rk_logger = setup_logger("rocklock1")


class Connection1(object):
    def __init__(self, host, host_usr, host_pwd, result_log_path):
        self.host_usr = host_usr
        self.host_pwd = host_pwd
        self.host = host
        self.result_log_path = result_log_path
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            self.host, 22, username=self.host_usr, password=self.host_pwd
        )
        self.r_sftp = self.client.open_sftp()
        print("Script1 method:")
        print(host_usr)
        print(host_pwd)

    def S1(self, app_name, radio, src_app_path, log_path):
        print("Script1: method S1 started")
        dest_path = "/opt/splunk/etc/apps/"
        all_app_dirs = []

        copy = [
            "sshpass -p "
            + self.host_pwd
            + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
            + src_app_path
            + app_name
            + " root@"
            + self.host
            + ":"
            + dest_path
        ]
        print("Script1: copy command" + str(copy))

        try:
            rk_logger.info(self.host + ": " + app_name + ": File transfer started")
            user_log(self.host + ": " + app_name + ": File transfer started\n")
            result_log(
                self.result_log_path,
                self.host + ": " + app_name + ": File transfer started\n",
            )

            copy_status = subprocess.check_call(copy, shell=True)
            print("Script1: copy status" + str(copy_status))

            rk_logger.info(self.host + ": " + app_name + ": File transfer completed")
            user_log(self.host + ": " + app_name + ": File transfer completed\n")
            result_log(
                self.result_log_path,
                self.host + ": " + app_name + ": File transfer completed\n",
            )

            splunk_stop = "/opt/splunk/bin/splunk stop "
            untar_spl = (
                " tar xvzf /opt/splunk/etc/apps/"
                + app_name
                + " -C /opt/splunk/etc/apps/ "
            )
            remove_spl = " rm -rf /opt/splunk/etc/apps/" + app_name + " "
            splunk_start = " /opt/splunk/bin/splunk start"

            char_count = int(len(app_name) / 2)

            self.r_sftp.chdir(dest_path)
            for loop in self.r_sftp.listdir():
                if loop[:char_count] == app_name[:char_count]:
                    all_app_dirs.append(loop)
            matched_file = difflib.get_close_matches(app_name, all_app_dirs)
            print(matched_file)
            print(all_app_dirs)
            if (str(radio[0]) == "Install") or (matched_file == [app_name]):

                rk_logger.info(
                    self.host + ": " + app_name + ": App installation started"
                )
                user_log(self.host + ": " + app_name + ": App installation started\n")
                result_log(
                    self.result_log_path,
                    self.host + ": " + app_name + ": App installation started\n",
                )

                install_command = (
                    splunk_stop
                    + "&&"
                    + untar_spl
                    + "&&"
                    + remove_spl
                    + "&&"
                    + splunk_start
                )
                print("Script1: install command " + str(install_command))
                stdin, stdout, stderr = self.client.exec_command(install_command)
                for i, line in enumerate(stdout):
                    line = line.rstrip()
                    print("%s" % line)

                rk_logger.info(
                    self.host + ": " + app_name + ": App installation completed"
                )
                user_log(self.host + ": " + app_name + ": App installation completed\n")
                result_log(
                    self.result_log_path,
                    self.host + ": " + app_name + ": App installation completed\n",
                )
            else:

                matched_file.remove(app_name)
                delete_app = ""
                matched_file = delete_app.join(matched_file)

                remove_app = " rm -rf /opt/splunk/etc/apps/" + matched_file + " "
                reinstall_command = (
                    splunk_stop
                    + "&&"
                    + remove_app
                    + "&&"
                    + untar_spl
                    + "&&"
                    + remove_spl
                    + "&&"
                    + splunk_start
                )
                print("Script1: reinstall command " + str(reinstall_command))

                rk_logger.info(
                    self.host + ": " + app_name + ": App Reinstallation started"
                )
                user_log(self.host + ": " + app_name + ": App Reinstallation started\n")
                result_log(
                    self.result_log_path,
                    self.host + ": " + app_name + ": App Reinstallation started\n",
                )

                stdin, stdout, stderr = self.client.exec_command(reinstall_command)
                for i, line in enumerate(stdout):
                    line = line.rstrip()
                    print("%s" % line)

                rk_logger.info(
                    self.host + ": " + app_name + ": App Reinstallation completed"
                )
                user_log(
                    self.host + ": " + app_name + ": App Reinstallation completed\n"
                )
                result_log(
                    self.result_log_path,
                    self.host + ": " + app_name + ": App Reinstallation completed\n",
                )

            print("Script1 : try method completed " + str(self.host))

        except subprocess.CalledProcessError as e:
            print("Script1 : except method called " + str(self.host))
            rk_logger.info(
                self.host
                + ": "
                + app_name
                + ": either Directory /opt/splunk/etc/apps/ not available or subprocess call error, due to this App does not installed"
            )
            user_log(
                self.host
                + ": "
                + app_name
                + ": either Directory /opt/splunk/etc/apps/ not available or subprocess call error, due to this App does not installed\n"
            )
            result_log(
                self.result_log_path,
                self.host
                + ": "
                + app_name
                + ": either Directory /opt/splunk/etc/apps/ not available or subprocess call error, due to this App does not installed\n",
            )

        finally:
            print("Script1 : finally method called " + str(self.host))
            self.r_sftp.close()
            self.client.close()
