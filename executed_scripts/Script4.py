import subprocess
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

rk_logger = setup_logger("rocklock4")

filepath = os.path.abspath(__file__)

status_path = str(filepath.rsplit("/", 2)[0]) + "/Splunk_Status/"
access_rights = 0o755
if not os.path.isdir(status_path):
    os.mkdir(status_path, access_rights)


class Connection4(object):
    def __init__(self, host, host_user, host_pwd, CM, splunk_version, result_log_path):
        self.host_usr = host_user
        self.host_pwd = host_pwd
        self.host = host
        self.result_log_path = result_log_path
        self.all_status = []
        self.all_app_dirs = []
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            self.host, 22, username=self.host_usr, password=self.host_pwd
        )
        self.r_sftp = self.client.open_sftp()
        self.CM = CM
        self.license_file = "Rakesh_Yadav_16_Aug_2020.License"
        self.Splunk_Home = " /opt/splunk/bin/splunk "
        self.Splunk_new_version = (
            self.Splunk_Home
            + "start --accept-license --answer-yes --no-prompt --seed-passwd admin123 "
        )
        self.Splunk_old_version = self.Splunk_Home + "start --accept-license "
        self.Splunk_old_pass_update = (
            self.Splunk_Home
            + "edit user admin -password admin123 -auth admin:changeme "
        )
        self.Splunk_Restart = self.Splunk_Home + "restart "
        self.login_pwd = "admin:admin123 "
        self.Splunk_version = splunk_version
        self.get_version = self.Splunk_version[7:10]
        print(self.get_version)
        self.Splunk_license_master = (
            self.Splunk_Home
            + "add license /opt/"
            + self.license_file
            + " -auth "
            + self.login_pwd
            + "&&"
            + self.Splunk_Restart
        )
        self.Splunk_license_slave = (
            self.Splunk_Home
            + "edit licenser-localslave -master_uri https://"
            + self.CM
            + ":8089 -auth "
            + self.login_pwd
            + "&&"
            + self.Splunk_Restart
        )
        self.src_auth_file = "/opt/splunk/etc/auth/splunk.secret"
        self.dest_auth_path = "/opt/splunk/etc/auth/"

    def S4_untar(self, DPL, radio, Splunk_path, log_path):
        dest_path = "/opt/"
        main_dir = "opt"

        Splunk_dir_name = dest_path + "splunk/bin"

        copy = [
            "sshpass -p "
            + self.host_pwd
            + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
            + Splunk_path
            + "/"
            + self.Splunk_version
            + " root@"
            + self.host
            + ":"
            + dest_path
        ]
        print(copy)

        copy_license = [
            "sshpass -p "
            + self.host_pwd
            + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
            + Splunk_path
            + "/"
            + self.license_file
            + " root@"
            + self.host
            + ":"
            + dest_path
        ]
        print(copy_license)

        Splunk_Home = " /opt/splunk/bin/splunk "
        Splunk_Stop = Splunk_Home + "stop "
        Splunk_Removed = " rm -rf /opt/splunk "
        Splunk_untar = " tar xvzf /opt/" + self.Splunk_version + " -C /opt/ "

        command_Old_install = Splunk_untar
        command_Old_install_stop = Splunk_Stop + "&&" + Splunk_untar
        command_Old_reinstall_stop = (
            Splunk_Stop + "&&" + Splunk_Removed + "&&" + Splunk_untar
        )

        command_New_install = Splunk_untar
        command_New_install_stop = Splunk_Stop + "&&" + Splunk_untar
        command_New_reinstall_stop = (
            Splunk_Stop + "&&" + Splunk_Removed + "&&" + Splunk_untar
        )

        print(command_Old_install)
        print(command_Old_install_stop)
        print(command_Old_reinstall_stop)
        print(command_New_install)
        print(command_New_install_stop)
        print(command_New_reinstall_stop)
        try:
            self.execute("cd ..; pwd")
            self.r_sftp.chdir("/")

            for folder in self.r_sftp.listdir():
                self.all_app_dirs.append(folder)
            print(self.all_app_dirs)

            matched_file = difflib.get_close_matches(main_dir, self.all_app_dirs)

            print(matched_file)
            if matched_file:

                rk_logger.info(
                    self.host + ": " + self.Splunk_version + ": File transfer started"
                )
                user_log(
                    self.host + ": " + self.Splunk_version + ": File transfer started\n"
                )
                result_log(
                    self.result_log_path,
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": File transfer started\n",
                )

                copy = [
                    "sshpass -p "
                    + self.host_pwd
                    + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
                    + Splunk_path
                    + "/"
                    + self.Splunk_version
                    + " root@"
                    + self.host
                    + ":"
                    + dest_path
                ]
                copy_status = subprocess.check_call(copy, shell=True)

                rk_logger.info(
                    self.host + ": " + self.Splunk_version + ": File transfer completed"
                )
                user_log(
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": File transfer completed\n"
                )
                result_log(
                    self.result_log_path,
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": File transfer completed\n",
                )

                rk_logger.info(
                    self.host + ": " + self.license_file + ": File transfer started"
                )
                user_log(
                    self.host + ": " + self.license_file + ": File transfer started\n"
                )
                result_log(
                    self.result_log_path,
                    self.host + ": " + self.license_file + ": File transfer started\n",
                )

                copy_license = [
                    "sshpass -p "
                    + self.host_pwd
                    + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
                    + Splunk_path
                    + "/"
                    + self.license_file
                    + " root@"
                    + self.host
                    + ":"
                    + dest_path
                ]
                copy_status1 = subprocess.check_call(copy_license, shell=True)

                rk_logger.info(
                    self.host + ": " + self.license_file + ": File transfer completed"
                )
                user_log(
                    self.host + ": " + self.license_file + ": File transfer completed\n"
                )
                result_log(
                    self.result_log_path,
                    self.host
                    + ": "
                    + self.license_file
                    + ": File transfer completed\n",
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
                        + self.Splunk_version
                        + ": Splunk fresh installation started as splunk was not installed"
                    )
                    user_log(
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk fresh installation started as splunk was not installed\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk fresh installation started as splunk was not installed\n",
                    )

                    self.final_execute(
                        self.get_version, command_New_install, command_Old_install
                    )

                    rk_logger.info(
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk fresh installation completed"
                    )
                    user_log(
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk fresh installation completed\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk fresh installation completed\n",
                    )
                    self.cluster_license()

                elif str(radio[0]) == "Install":
                    print("Install loop")

                    rk_logger.info(
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Installation started"
                    )
                    user_log(
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Installation started\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Installation started\n",
                    )

                    self.final_execute(
                        self.get_version,
                        command_New_install_stop,
                        command_Old_install_stop,
                    )

                    rk_logger.info(
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Installation completed"
                    )
                    user_log(
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Installation completed\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Installation completed\n",
                    )
                    self.cluster_license()

                else:
                    print("reinstall loop")

                    rk_logger.info(
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Reinstallation started"
                    )
                    user_log(
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Reinstallation started\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Reinstallation started\n",
                    )

                    self.final_execute(
                        self.get_version,
                        command_New_reinstall_stop,
                        command_Old_reinstall_stop,
                    )

                    rk_logger.info(
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Reinstallation completed"
                    )
                    user_log(
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Reinstallation completed\n"
                    )
                    result_log(
                        self.result_log_path,
                        self.host
                        + ": "
                        + self.Splunk_version
                        + ": Splunk Reinstallation completed\n",
                    )
                    self.cluster_license()

            else:
                self.execute("cd ..;pwd; mkdir " + main_dir)

                rk_logger.info(
                    self.host + ": " + self.Splunk_version + ": File transfer started"
                )
                user_log(
                    self.host + ": " + self.Splunk_version + ": File transfer started\n"
                )
                result_log(
                    self.result_log_path,
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": File transfer started\n",
                )

                copy = [
                    "sshpass -p "
                    + self.host_pwd
                    + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
                    + Splunk_path
                    + "/"
                    + self.Splunk_version
                    + " root@"
                    + self.host
                    + ":"
                    + dest_path
                ]
                copy_status = subprocess.check_call(copy, shell=True)

                rk_logger.info(
                    self.host + ": " + self.Splunk_version + ": File transfer completed"
                )
                user_log(
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": File transfer completed\n"
                )
                result_log(
                    self.result_log_path,
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": File transfer completed\n",
                )

                rk_logger.info(
                    self.host + ": " + self.license_file + ": File transfer started"
                )
                user_log(
                    self.host + ": " + self.license_file + ": File transfer started\n"
                )
                result_log(
                    self.result_log_path,
                    self.host + ": " + self.license_file + ": File transfer started\n",
                )

                copy_license = [
                    "sshpass -p "
                    + self.host_pwd
                    + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
                    + Splunk_path
                    + "/"
                    + self.license_file
                    + " root@"
                    + self.host
                    + ":"
                    + dest_path
                ]
                copy_status1 = subprocess.check_call(copy_license, shell=True)

                rk_logger.info(
                    self.host + ": " + self.license_file + ": File transfer completed"
                )
                user_log(
                    self.host + ": " + self.license_file + ": File transfer completed\n"
                )
                result_log(
                    self.result_log_path,
                    self.host
                    + ": "
                    + self.license_file
                    + ": File transfer completed\n",
                )

                rk_logger.info(
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": Splunk fresh installation started after creating the /opt directory"
                )
                user_log(
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": Splunk fresh installation started after creating the /opt directory\n"
                )
                result_log(
                    self.result_log_path,
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": Splunk fresh installation started after creating the /opt directory\n",
                )

                self.final_execute(
                    self.get_version, command_New_install, command_Old_install
                )

                rk_logger.info(
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": Splunk fresh installation completed after creating the /opt directory"
                )
                user_log(
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": Splunk fresh installation completed after creating the /opt directory\n"
                )
                result_log(
                    self.result_log_path,
                    self.host
                    + ": "
                    + self.Splunk_version
                    + ": Splunk fresh installation completed after creating the /opt directory\n",
                )
                self.cluster_license()

            if self.host == DPL:
                print("start deployer method")
                command_New_install = self.Splunk_new_version
                command_Old_install = (
                    self.Splunk_old_version + "&&" + self.Splunk_old_pass_update
                )
                self.final_execute(
                    self.get_version, command_New_install, command_Old_install
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
            print("finally called---------" + str(self.host))
            self.r_sftp.close()
            self.client.close()

    def S4_secret_copy(self, SH1, SH2, SH3):
        print("S4_secret_copy method")
        print(SH1)
        print(SH2)
        print(SH3)
        try:
            print("Deployer is")
            print(self.host)

            with open(status_path + "linux_distro.txt", "w") as rk:
                rk.write("")
            stdin, stdout, stderr = self.client.exec_command("hostnamectl")

            for i, line in enumerate(stdout):
                line = line.rstrip()
                with open(status_path + "linux_distro.txt", "a") as rk:
                    rk.write(line)
                print("%s" % line)
            for i, line in enumerate(stderr):
                line = line.rstrip()
                with open(status_path + "linux_distro.txt", "a") as rk:
                    rk.write(line)
                print("%s" % line)

            with open(status_path + "linux_distro.txt", "r") as rk:
                verify_os = rk.read()
            os = re.findall(r"(?:\bCentOS\b|\bUbuntu\b|\bopenSUSE\b)", str(verify_os))

            print("OS is " + str(os))
            if os == ["CentOS"]:
                print("if CentOS")
                self.ssh_copy("yum install -y sshpass")

            elif os == ["Ubuntu"]:
                print("Ubuntu")
                self.ssh_copy("apt-get install -y sshpass")

            elif os == ["openSUSE"]:
                print("openSUSE")
                self.ssh_copy("zypper install -y sshpass")

            else:
                print("OS not found")
                rk_logger.info(
                    self.host
                    + ": It seems virtual machine OS is not CentOS/Ubuntu/openSUSE \n"
                )
                user_log(
                    self.host
                    + ": It seems virtual machine OS is not CentOS/Ubuntu/openSUSE \n"
                )
                result_log(
                    self.result_log_path,
                    self.host
                    + ": It seems virtual machine OS is not CentOS/Ubuntu/openSUSE \n",
                )

            self.copy_secret_file(SH1)
            self.copy_secret_file(SH2)
            self.copy_secret_file(SH3)

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
            print("finally called---------" + str(self.host))
            self.r_sftp.close()
            self.client.close()

    def S4_restart_idx_sh(self):
        print("S4_restart_idx_sh method")
        command_New_install = self.Splunk_new_version
        command_Old_install = (
            self.Splunk_old_version + "&&" + self.Splunk_old_pass_update
        )

        try:
            self.final_execute(
                self.get_version, command_New_install, command_Old_install
            )
            self.license_add(self.Splunk_license_master, self.Splunk_license_slave)

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
            print("finally called---------" + str(self.host))
            self.r_sftp.close()
            self.client.close()

    def cluster_license(self):
        if self.host == self.CM:
            print("start cluster master after adding the license")
            command_New_install = self.Splunk_new_version
            command_Old_install = (
                self.Splunk_old_version + "&&" + self.Splunk_old_pass_update
            )
            self.final_execute(
                self.get_version, command_New_install, command_Old_install
            )
            self.license_add(self.Splunk_license_master, self.Splunk_license_slave)

    def ssh_copy(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        for j, line in enumerate(stdout):
            line = line.rstrip()
            print("%s" % line)
        for j, line in enumerate(stderr):
            line = line.rstrip()
            print("%s" % line)

    def copy_secret_file(self, sh):
        command = (
            "sshpass -p "
            + self.host_pwd
            + " scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
            + self.src_auth_file
            + " root@"
            + sh
            + ":"
            + self.dest_auth_path
        )
        print(command)

        rk_logger.info(
            self.host
            + ": splunk.secret file copy started to Search Head IP : "
            + sh
            + "\n"
        )
        user_log(
            self.host
            + ": splunk.secret file copy started to Search Head IP : "
            + sh
            + "\n"
        )
        result_log(
            self.result_log_path,
            self.host
            + ": splunk.secret file copy started to Search Head IP : "
            + sh
            + "\n",
        )

        stdin, stdout, stderr = self.client.exec_command(command)

        rk_logger.info(
            self.host
            + ": splunk.secret file copy done to Search Head IP : "
            + sh
            + "\n"
        )
        user_log(
            self.host
            + ": splunk.secret file copy done to Search Head IP : "
            + sh
            + "\n"
        )
        result_log(
            self.result_log_path,
            self.host
            + ": splunk.secret file copy done to Search Head IP : "
            + sh
            + "\n",
        )

        for j, line in enumerate(stdout):
            line = line.rstrip()
            print("%s" % line)
        for j, line in enumerate(stderr):
            line = line.rstrip()
            print("%s" % line)

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

    def license_add(self, master, slave):
        print("==========Connected to Linux IP for license add :" + self.host)
        if self.host == self.CM:
            stdin, stdout, stderr = self.client.exec_command(master)
            rk_logger.info(
                self.host
                + ": "
                + self.license_file
                + ": License added to Cluster Master"
            )
            user_log(
                self.host
                + ": "
                + self.license_file
                + ": License added to Cluster Master\n"
            )
            result_log(
                self.result_log_path,
                self.host
                + ": "
                + self.license_file
                + ": License added to Cluster Master\n",
            )
        else:
            stdin, stdout, stderr = self.client.exec_command(slave)
            rk_logger.info(
                self.host + ": " + self.license_file + ": License added as a slave"
            )
            user_log(
                self.host + ": " + self.license_file + ": License added as a slave\n"
            )
            result_log(
                self.result_log_path,
                self.host + ": " + self.license_file + ": License added as a slave\n",
            )

        for j, line in enumerate(stdout):
            line = line.rstrip()
            print("%s" % line)
        for j, line in enumerate(stderr):
            line = line.rstrip()
            print("%s" % line)
