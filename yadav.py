#!/usr/bin/env python3
from flask import render_template, request, flash
from paramiko import BadHostKeyException
from paramiko import AuthenticationException
from werkzeug.utils import secure_filename
from executed_scripts import log_util as user_log
from executed_scripts import Script1
from executed_scripts import Script2
from executed_scripts import Script3
from executed_scripts import Script4
from executed_scripts import Script5
from executed_scripts import Script6
from threading import Thread, Lock
from html.parser import HTMLParser
from paramiko import SSHException
from itertools import islice
from pexpect import pxssh
from flask import Flask
from flask import Response
from queue import Queue
import subprocess
import threading
import traceback
import logging
import log
import paramiko
import string
import shutil
import queue
import glob
import time
import re
import os


app = Flask(__name__)
app.secret_key = b"_rakesh_the_bug_hunter/"

# Allowing only .spl and .tgz file extension
ALLOWED_EXTENSIONS = {"spl", "tgz"}
access_rights = 0o755
app_file_name = ""
app_file_nameS1 = ""
radio_buttion = ""
setup_name = ""
directory = ""
lock = Lock()
ABSPATH = os.path.abspath(__file__)
BASEPATH, current_filename = os.path.split(ABSPATH)

# Splunk_Setup is the directory which contains the setup and license file
# For example: splunk-8.0.4-767223ac207f-Linux-x86_64.tgz
splunk_path = os.path.join(BASEPATH, "Splunk_Setup")
if not os.path.isdir(splunk_path):
    os.mkdir(splunk_path, access_rights)

# All in one log file
log_path = os.path.join(BASEPATH, "log")

# Specific installation log file
ui_log_path = os.path.join(BASEPATH, "executed_scripts/")

#'users' is the directory where directory will be created based on the request
# coming from the user as here we don't have a registration page or kind of any
# session management
user_path = os.path.join(BASEPATH, "users/")
if not os.path.isdir(user_path):
    os.mkdir(user_path, access_rights)

count_file_path = ui_log_path + "script_count.txt"
host_user = "root"
host_pwd = ""


@app.route("/")
def hello():
    lock.acquire()
    global user_path, directory, count_file_path
    print(
        "hello : Remote IP Address is :-------------------------------------- "
        + request.remote_addr
    )

    directory_name = request.remote_addr
    directory = user_path + directory_name

    splunk_list = []
    user_count = len(os.listdir(user_path))
    print("hello: User count is " + str(user_count))
    text1 = "Total users have visited: "

    count_file = os.path.isfile(count_file_path)
    if not count_file:
        with open(count_file_path, "w") as rk:
            rk.write("0")
    with open(count_file_path, "r") as rk:
        script_run_count = rk.read()
    text2 = "Total number of times script executed: "

    list_of_splunk = glob.glob(splunk_path + "/*.tgz")
    total_splunk = len(list_of_splunk)
    for i in range(0, total_splunk):
        head, splunk_name = os.path.split(list_of_splunk[i])
        splunk_list.append(splunk_name)
    splunk_list.sort(reverse=False)

    S1_app_path = directory + "/S1_app/"
    S6_app_path = directory + "/S6_app/"

    S1_app_filelist = glob.glob(os.path.join(S1_app_path, "*.spl")) + glob.glob(
        os.path.join(S1_app_path, "*.tgz")
    )
    for f in S1_app_filelist:
        os.remove(f)

    S6_app_filelist = glob.glob(os.path.join(S6_app_path, "*.spl")) + glob.glob(
        os.path.join(S6_app_path, "*.tgz")
    )
    for f in S6_app_filelist:
        os.remove(f)

    lock.release()

    return render_template(
        "index.html",
        total_user=text1 + (str(user_count)),
        script_count=text2 + (str(script_run_count)),
        splunks=splunk_list,
    )
    # return render_template('index.html', splunks = splunk_list)


@app.route("/confirm", methods=["POST"])
def confirm():

    try:
        lock.acquire()
        global setup_name, directory, radio_buttion, user_path, app_file_name, app_file_nameS1, access_rights, host_user, host_pwd
        print("confirm : Remote IP Address is : " + request.remote_addr)
        user_log.ui_log_write()
        user_log.ui_log_append(
            "Recently visited user's IP address is: " + request.remote_addr + " \n"
        )

        directory_name = request.remote_addr
        directory = user_path + directory_name
        print("confirm: Full directory Name " + directory)

        try:
            if not os.path.isdir(directory):
                os.mkdir(directory, access_rights)
            setup_name = request.form["setup"]
            print("confirm: setup name is " + setup_name)
            print(
                "confirm: setup file path with name "
                + directory
                + "/"
                + setup_name
                + ".txt"
            )
            with open(directory + "/" + setup_name + ".txt", "w") as rk:
                rk.write("")
            print("confirm: setup file creation ")

            if setup_name == "S1":
                host_pwd = request.form["pwd"]
                print("confirm: check host_pwd")
                print(host_pwd)
                UPLOAD_FOLDER = directory + "/S1_app" + "/"
                print("confirm: going to call file browse method")
                upload_stop, app_file_nameS1 = file_browse(
                    "file", directory + "/S1_app"
                )
                print("confirm: file browse method return values")
                print(upload_stop)
                print(app_file_nameS1)
                print("confirm: file browse method return value done")

                if upload_stop:
                    return ("", 204)

                form_data("A", setup_name)

                radio_buttion = request.form["app"]
                print("confirm: radio button value " + radio_buttion)

                print(
                    "confirm: check user entered values " + request.form["A1"],
                    request.form["A2"],
                    request.form["A3"],
                    request.form["A4"],
                    request.form["A5"],
                    request.form["A6"],
                    request.form["A7"],
                    request.form["A8"],
                )
                with open(UPLOAD_FOLDER + "pwd.txt", "w") as rk:
                    rk.write(host_pwd)

                with open(UPLOAD_FOLDER + "radio.txt", "w") as rk:
                    rk.write(radio_buttion)
                content = read_ip(directory, setup_name)
                print("confirm: read contents " + content)

                if content:
                    print("confirm: Remote IP Address is : " + request.remote_addr)
                    print("---------------Confirm method done from if loop")
                    return render_template(
                        "/confirm.html", readIP=content, app_file=app_file_nameS1
                    )
                else:
                    print("--------------Confirm method done from else loop")
                    return ("", 204)

            if setup_name == "S2":
                host_pwd = request.form["pwd"]
                print("confirm: check host_pwd")
                print(host_pwd)
                form_data("B", setup_name)
                radio_buttion = request.form["splunk"]
                print("confirm: Radio button is " + radio_buttion)
                if not os.path.isdir(directory + "/S2_radio_option"):
                    os.mkdir(directory + "/S2_radio_option", access_rights)
                UPLOAD_FOLDER = directory + "/S2_radio_option" + "/"

                with open(UPLOAD_FOLDER + "pwd.txt", "w") as rk:
                    rk.write(host_pwd)

                with open(UPLOAD_FOLDER + "radio.txt", "w") as rk:
                    rk.write(radio_buttion)
                print(
                    "confirm: check user entered values " + request.form["B1"],
                    request.form["B2"],
                    request.form["B3"],
                    request.form["B4"],
                    request.form["B5"],
                    request.form["B6"],
                    request.form["B7"],
                    request.form["B8"],
                )

                content = read_ip(directory, setup_name)
                print("confirm: read contents " + content)

                if content:
                    print("confirm: Remote IP Address is : " + request.remote_addr)
                    print("-------------------Confirm method done from if loop")
                    return render_template("/confirm.html", readIP=content)
                else:
                    print("--------------Confirm method done from else loop")
                    return ("", 204)

            if setup_name == "S3":
                host_pwd = request.form["pwd"]
                print("confirm: check host_pwd")
                print(host_pwd)
                form_data("C", setup_name)

                radio_buttion = request.form["dist"]
                print("confirm: Radio button is " + radio_buttion)
                if not os.path.isdir(directory + "/S3_radio_option"):
                    os.mkdir(directory + "/S3_radio_option", access_rights)
                UPLOAD_FOLDER = directory + "/S3_radio_option" + "/"

                with open(UPLOAD_FOLDER + "pwd.txt", "w") as rk:
                    rk.write(host_pwd)
                with open(UPLOAD_FOLDER + "radio.txt", "w") as rk:
                    rk.write(radio_buttion)

                print(
                    "confirm: check user entered values " + request.form["C1"],
                    request.form["C2"],
                    request.form["C3"],
                    request.form["C4"],
                    request.form["C5"],
                    request.form["C6"],
                    request.form["C7"],
                    request.form["C8"],
                )
                stop = field_check("C1", 2)
                if stop:
                    return ("", 204)
                content = read_ip(directory, setup_name)
                print("confirm: read contents " + content)

                if content:
                    print("confirm: Remote IP Address is : " + request.remote_addr)
                    print("-----------------Confirm method done from if loop")
                    return render_template("/confirm.html", readIP=content)
                else:
                    print("---------------Confirm method done from else loop")
                    return ("", 204)

            if setup_name == "S4":
                host_pwd = request.form["pwd"]
                print("confirm: check host_pwd")
                print(host_pwd)
                form_data("D", setup_name)
                radio_buttion = request.form["splunk"]
                print("confirm: Radio button is " + radio_buttion)
                if not os.path.isdir(directory + "/S4_radio_option"):
                    os.mkdir(directory + "/S4_radio_option", access_rights)
                UPLOAD_FOLDER = directory + "/S4_radio_option" + "/"
                with open(UPLOAD_FOLDER + "pwd.txt", "w") as rk:
                    rk.write(host_pwd)
                with open(UPLOAD_FOLDER + "radio.txt", "w") as rk:
                    rk.write(radio_buttion)
                print(
                    "confirm: check user entered values " + request.form["D1"],
                    request.form["D2"],
                    request.form["D3"],
                    request.form["D4"],
                    request.form["D5"],
                    request.form["D6"],
                    request.form["D7"],
                    request.form["D8"],
                )
                stop = field_check("D1", 8)
                if stop:
                    return ("", 204)
                content = read_ip(directory, setup_name)
                print("confirm: read contents " + content)

                if content:
                    print("confirm: Remote IP Address is : " + request.remote_addr)
                    print("-----------------Confirm method done from if loop")
                    return render_template("/confirm.html", readIP=content)
                else:
                    print("---------------Confirm method done from else loop")
                    return ("", 204)

            if setup_name == "S5":
                host_pwd = request.form["pwd"]
                print("confirm: check host_pwd")
                print(host_pwd)
                if not os.path.isdir(directory + "/S5_pwd"):
                    os.mkdir(directory + "/S5_pwd", access_rights)
                UPLOAD_FOLDER = directory + "/S5_pwd" + "/"
                with open(UPLOAD_FOLDER + "pwd.txt", "w") as rk:
                    rk.write(host_pwd)
                form_data("E", setup_name)
                print(
                    "confirm: check user entered values " + request.form["E1"],
                    request.form["E2"],
                    request.form["E3"],
                    request.form["E4"],
                    request.form["E5"],
                    request.form["E6"],
                    request.form["E7"],
                    request.form["E8"],
                )
                stop = field_check("E1", 8)
                if stop:
                    return ("", 204)
                content = read_ip(directory, setup_name)
                print("confirm: read contents " + content)

                if content:
                    print("confirm: Remote IP Address is : " + request.remote_addr)
                    print("-----------------Confirm method done from if loop")
                    return render_template("/confirm.html", readIP=content)
                else:
                    print("----------------Confirm method done from else loop")
                    return ("", 204)

            if setup_name == "S6":
                host_pwd = request.form["pwd"]
                print("confirm: check host_pwd")
                print(host_pwd)

                form_data("F", setup_name)
                print(
                    "confirm: check user entered values " + request.form["F1"],
                    request.form["F2"],
                    request.form["F3"],
                    request.form["F4"],
                    request.form["F5"],
                    request.form["F6"],
                    request.form["F7"],
                    request.form["F8"],
                )
                stop = field_check("F1", 8)
                if stop:
                    return ("", 204)

                print("confirm: going to call file browse method")
                upload_stop1, app_file_name1 = file_browse(
                    "file1", directory + "/S6_app"
                )
                print(upload_stop1)
                print(app_file_name1)
                with open(directory + "/S6_app/app_list.txt", "w") as rk:
                    rk.write(app_file_name1 + "\n")

                upload_stop2, app_file_name2 = file_browse(
                    "file2", directory + "/S6_app"
                )
                print(upload_stop2)
                print(app_file_name2)
                if upload_stop2:
                    return ("", 204)
                else:
                    with open(directory + "/S6_app/app_list.txt", "a") as rk:
                        rk.write(app_file_name2)
                print("confirm: file browse method return values")
                print(upload_stop1, upload_stop2)
                print(app_file_name1, app_file_name2)
                print("confirm: file browse method return values done")
                UPLOAD_FOLDER = directory + "/S6_app" + "/"
                with open(UPLOAD_FOLDER + "pwd.txt", "w") as rk:
                    rk.write(host_pwd)
                with open(directory + "/S6_app/app_list.txt", "r") as rk:
                    app_file_name = rk.read()

            content = read_ip(directory, setup_name)
            print("confirm: read contents " + content)

            if content:
                print("confirm: Remote IP Address is : " + request.remote_addr)
                print("---------------------Confirm method done from if loop")
                return render_template(
                    "/confirm.html", readIP=content, app_file=app_file_name
                )
            else:
                print("-------------------Confirm method done from else loop")
                return ("", 204)
        except OSError:
            print("error : {}".format(traceback.format_exc()))
    finally:
        lock.release()
        print("Confirm: finally block called")


@app.route("/logframe", methods=["GET"])
def stream():
    def generate():
        global ui_log_path
        with open(ui_log_path + "ui_log.log") as f:
            while True:
                yield f.read()
                time.sleep(1)

    return app.response_class(generate(), mimetype="text/plain")


@app.route("/result", methods=["POST"])
def run_script():

    try:
        lock.acquire()
        start_time = time.time()
        global setup_name, directory, radio_buttion, file_name_with_path, app_file_name, app_file_nameS1, log_path, splunk_path, count_file_path, host_user, host_pwd

        print("run_script: Remote IP Address is : " + request.remote_addr)
        directory_name = request.remote_addr
        directory = user_path + directory_name
        print("run_script: full directory path is " + directory)
        result_log_path = directory + "/result.log"

        result_log_file = os.path.isfile(result_log_path)
        if not result_log_file:
            print("in if loop to create log file")
            with open(result_log_path, "w") as rk:
                rk.write("")
        with open(result_log_path, "r") as rk:
            result_log = rk.read()

        list_of_files = glob.glob(directory + "/*.txt")
        latest_file = max(list_of_files, key=os.path.getctime)
        head, tail = os.path.split(latest_file)
        print("run_script: file name " + tail)
        raw_setup_name = tail.split(".")
        setup_name = raw_setup_name[0]
        print("run_script: setup name " + setup_name)
        with open(latest_file) as rk:
            verify_problem = rk.read()
            print(verify_problem)

        error = re.findall(
            r"(?:\bwindows\b|\blinux\b|\bpowered\b|\bPassword\b)", str(verify_problem)
        )
        print("run_script: find error " + str(error))

        if not error:
            print("run_script: no error ")
            with open(latest_file) as rk:
                raw_ip = rk.readlines()
            raw_ip = list(map(lambda s: s.strip(), raw_ip))
            print("run_script: no error going to read file for IPs")

            if setup_name == "S1" and app_file_nameS1:
                run_count()
                user_log.result_log_write(result_log_path)
                user_log.result_log_append(
                    result_log_path,
                    "Your IP address is: " + request.remote_addr + " \n",
                )
                UPLOAD_FOLDER = directory + "/S1_app/"

                with open(UPLOAD_FOLDER + "pwd.txt", "r") as rk:
                    host_pwd = rk.read()
                print("run_script : password is")
                print(host_pwd)
                with open(UPLOAD_FOLDER + "radio.txt", "r") as rk:
                    radio_buttion = rk.readlines()
                app_file = glob.glob(UPLOAD_FOLDER + "*.tgz")
                if not app_file:
                    app_file = glob.glob(UPLOAD_FOLDER + "*.spl")

                q = Queue()
                for i in range(0, len(raw_ip)):
                    q.put(raw_ip[i])

                threads = []
                for i in range(len(raw_ip)):
                    conn1 = Script1.Connection1(
                        q.get(), host_user, host_pwd, result_log_path
                    )
                    th = threading.Thread(
                        target=conn1.S1,
                        args=(
                            (app_file_nameS1),
                            (radio_buttion),
                            (UPLOAD_FOLDER),
                            (log_path),
                        ),
                    )
                    threads.append(th)
                    th.start()
                for th in threads:
                    th.join()
                app_file_nameS1 = ""
                delete_app = ""
                app_file = delete_app.join(app_file)
                os.remove(str(app_file))
                user_log.result_log_append(
                    result_log_path,
                    "Total time taken to finish the task is  %d seconds\n"
                    % (time.time() - start_time),
                )
                with open(result_log_path, "r") as rk:
                    result_log = rk.read()
                print("S1 method done==========")

            if setup_name == "S2" and raw_ip:
                run_count()
                user_log.result_log_write(result_log_path)
                user_log.result_log_append(
                    result_log_path,
                    "Your IP address is: " + request.remote_addr + " \n",
                )
                raw_ip_list = []
                splunk_version_list = []
                print("run_script: length of IPs " + str(len(raw_ip)))
                UPLOAD_FOLDER = directory + "/S2_radio_option/"

                with open(UPLOAD_FOLDER + "pwd.txt", "r") as rk:
                    host_pwd = rk.read()
                print("run_script : password is")
                print(host_pwd)
                with open(UPLOAD_FOLDER + "radio.txt", "r") as rk:
                    radio_buttion = rk.readlines()
                for i in range(0, (len(raw_ip))):
                    ip_splunk = raw_ip[i].split(":")
                    final_ip = ip_splunk[0]
                    raw_ip_list.append(final_ip)
                    splunk_version = ip_splunk[1]
                    splunk_version_list.append(splunk_version)

                q_ip = Queue()
                q_version = Queue()

                for i in range(0, len(raw_ip_list)):
                    q_ip.put(raw_ip_list[i])

                for i in range(0, len(splunk_version_list)):
                    q_version.put(splunk_version_list[i])

                threads = []
                for i in range(len(raw_ip_list)):
                    conn2 = Script2.Connection2(
                        q_ip.get(), host_user, host_pwd, result_log_path
                    )
                    th = threading.Thread(
                        target=conn2.S2,
                        args=(
                            (q_version.get()),
                            (radio_buttion),
                            (splunk_path),
                            (log_path),
                            (raw_ip_list),
                        ),
                    )
                    threads.append(th)
                    th.start()
                for th in threads:
                    th.join()
                with open(latest_file, "w") as rk:
                    rk.write("")
                user_log.result_log_append(
                    result_log_path,
                    "Total time taken to finish the task is  %d seconds\n"
                    % (time.time() - start_time),
                )
                with open(result_log_path, "r") as rk:
                    result_log = rk.read()
                print("S2 method done==========")

            if setup_name == "S3" and raw_ip:
                run_count()
                user_log.result_log_write(result_log_path)
                user_log.result_log_append(
                    result_log_path,
                    "Your IP address is: " + request.remote_addr + " \n",
                )
                SH = raw_ip[0]
                print("run_script: search head is " + SH)
                print(result_log_path)
                UPLOAD_FOLDER = directory + "/S3_radio_option/"

                with open(UPLOAD_FOLDER + "pwd.txt", "r") as rk:
                    host_pwd = rk.read()
                print("run_script : password is")
                print(host_pwd)
                with open(UPLOAD_FOLDER + "radio.txt", "r") as rk:
                    radio_buttion = rk.readlines()
                print(radio_buttion)
                conn3 = Script3.Connection3(result_log_path, radio_buttion)
                for i in range(1, len(raw_ip)):
                    idx = raw_ip[i]
                    print(SH, idx)
                    conn3.S3(SH, host_user, host_pwd, idx)
                with open(latest_file, "w") as rk:
                    rk.write("")
                user_log.result_log_append(
                    result_log_path,
                    "Total time taken to finish the task is  %d seconds\n"
                    % (time.time() - start_time),
                )
                with open(result_log_path, "r") as rk:
                    result_log = rk.read()
                print("S3 method done==========")

            if setup_name == "S4" and raw_ip:
                run_count()
                user_log.result_log_write(result_log_path)
                user_log.result_log_append(
                    result_log_path,
                    "Your IP address is: " + request.remote_addr + " \n",
                )
                UPLOAD_FOLDER = directory + "/S4_radio_option/"
                print("run_script: Upload folder path " + UPLOAD_FOLDER)

                with open(UPLOAD_FOLDER + "pwd.txt", "r") as rk:
                    host_pwd = rk.read()
                print("run_script : password is")
                print(host_pwd)
                with open(UPLOAD_FOLDER + "radio.txt", "r") as rk:
                    radio_buttion = rk.readlines()
                print("run_script: check radio button " + str(radio_buttion))
                final_ip = []
                split_ip_splunk = raw_ip[0].split(":")
                splunk_version = split_ip_splunk[1]
                print("run_script: Splunk version is " + splunk_version)
                for i in range(0, len(raw_ip)):
                    raw_final_ip = raw_ip[i].split(":")
                    final_ip.append(raw_final_ip[0])

                CM = final_ip[0]
                DPL = final_ip[1]
                IDX1 = final_ip[2]
                IDX2 = final_ip[3]
                IDX3 = final_ip[4]
                SH1 = final_ip[5]
                SH2 = final_ip[6]
                SH3 = final_ip[7]
                print(CM)
                print(DPL)
                print(IDX1)
                print(IDX2)
                print(IDX3)
                print(SH1)
                print(SH2)
                print(SH3)

                print("run_script: final IPs are" + str(final_ip))

                q_ip = Queue()
                for i in range(0, len(final_ip)):
                    q_ip.put(final_ip[i])
                threads = []
                for i in range(len(final_ip)):
                    conn4 = Script4.Connection4(
                        q_ip.get(),
                        host_user,
                        host_pwd,
                        CM,
                        splunk_version,
                        result_log_path,
                    )
                    th = threading.Thread(
                        target=conn4.S4_untar,
                        args=((DPL), (radio_buttion), (splunk_path), (log_path),),
                    )
                    threads.append(th)
                    th.start()
                for th in threads:
                    th.join()

                conn4 = Script4.Connection4(
                    DPL, host_user, host_pwd, CM, splunk_version, result_log_path
                )
                conn4.S4_secret_copy(SH1, SH2, SH3)

                final_ip_restart = final_ip
                del final_ip_restart[0:2]
                print(final_ip_restart)
                q_ip = Queue()
                for i in range(0, len(final_ip_restart)):
                    q_ip.put(final_ip_restart[i])
                threads = []
                for i in range(len(final_ip_restart)):
                    conn4 = Script4.Connection4(
                        q_ip.get(),
                        host_user,
                        host_pwd,
                        CM,
                        splunk_version,
                        result_log_path,
                    )
                    th = threading.Thread(target=conn4.S4_restart_idx_sh)
                    threads.append(th)
                    th.start()
                for th in threads:
                    th.join()

                final_ip = []
                splunk_version = ""

                with open(latest_file, "w") as rk:
                    rk.write("")

                user_log.result_log_append(
                    result_log_path,
                    "Total time taken to finish the task is  %d seconds\n"
                    % (time.time() - start_time),
                )
                with open(result_log_path, "r") as rk:
                    result_log = rk.read()
                print("S4 method done==========")

            if setup_name == "S5" and raw_ip:
                run_count()
                UPLOAD_FOLDER = directory + "/S5_pwd/"
                print("run_script: Upload folder path " + UPLOAD_FOLDER)

                with open(UPLOAD_FOLDER + "pwd.txt", "r") as rk:
                    host_pwd = rk.read()
                print("run_script : password is")
                print(host_pwd)
                user_log.result_log_write(result_log_path)
                user_log.result_log_append(
                    result_log_path,
                    "Your IP address is: " + request.remote_addr + " \n",
                )
                print("run_script: setup 5 is started")
                conn5 = Script5.Connection5(result_log_path)
                conn5.S5(raw_ip, host_user, host_pwd)
                with open(latest_file, "w") as rk:
                    rk.write("")
                user_log.result_log_append(
                    result_log_path,
                    "Total time taken to finish the task is  %d seconds\n"
                    % (time.time() - start_time),
                )
                with open(result_log_path, "r") as rk:
                    result_log = rk.read()
                print("S5 method done==========")

            if setup_name == "S6" and raw_ip:
                run_count()
                user_log.result_log_write(result_log_path)
                user_log.result_log_append(
                    result_log_path,
                    "Your IP address is: " + request.remote_addr + " \n",
                )
                UPLOAD_FOLDER = directory + "/S6_app/"
                print("run_script: Upload folder path is " + UPLOAD_FOLDER)

                with open(UPLOAD_FOLDER + "pwd.txt", "r") as rk:
                    host_pwd = rk.read()
                print("run_script : password is")
                print(host_pwd)
                with open(UPLOAD_FOLDER + "app_list.txt", "r") as rk:
                    app_file_name = rk.readlines()
                print(app_file_name[0])
                print(app_file_name[1])

                app_file = glob.glob(UPLOAD_FOLDER + "*.tgz")
                if not app_file:
                    app_file = glob.glob(UPLOAD_FOLDER + "*.spl")
                print("run_script: app name with full path is: " + str(app_file))

                conn6 = Script6.Connection6(result_log_path)
                conn6.S6(raw_ip, host_user, host_pwd, app_file_name, UPLOAD_FOLDER)
                with open(latest_file, "w") as rk:
                    rk.write("")
                user_log.result_log_append(
                    result_log_path,
                    "Total time taken to finish the task is  %d seconds\n"
                    % (time.time() - start_time),
                )
                with open(result_log_path, "r") as rk:
                    result_log = rk.read()
                print("S6 method done==========")

            return render_template("result.html", readlog=result_log)

        else:
            print("run_script: there is an error " + str(error))
            print("-------------------------------------------------------")
            return ("", 204)
    finally:
        lock.release()
        print("run script: finally method called")


def run_count():
    global count_file_path
    with open(count_file_path, "r") as rk:
        script_run_count = rk.read()
    count = int(script_run_count) + 1
    with open(count_file_path, "w") as rk:
        rk.write(str(count))


def form_data(field_name, setup_name):
    global directory, host_user
    from_file_ip = []
    for i in range(1, 9):
        val = request.form[field_name + str(i)]
        print("form_data: IP is " + val)
        print(
            "form_data: setup name is "
            + setup_name
            + " Full directory path is "
            + directory
        )

        IPS = field_name + str(i)
        print("form_data: field name is " + IPS)
        pat = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}")
        test = pat.match(request.form[field_name + str(i)])

        if val and test:
            print("form_data: final IP after test is " + str(from_file_ip))
            if val not in from_file_ip:
                print("form_data: good value not in list ")
                from_file_ip
                print("form_data: from file, ip initially " + str(from_file_ip))
                All_IP = field_name + str(i)
                print("form_data: before write: " + All_IP)
                command = ["ping", "-c", "1", request.form[field_name + str(i)]]
                print("form_data: command executed ")
                print("form_data: check Return code below")
                return_code = subprocess.call(command)
                print(return_code)

                if return_code == 0:
                    with open("/opt/Flask_Project/ping_info.txt", "wb") as out:
                        out.write(subprocess.check_output(command))
                    with open("/opt/Flask_Project/ping_info.txt", "r") as rk:
                        ping_info = rk.read()
                    linux = re.findall(
                        r"(?:\bttl=64\b|\bttl=62\b|\bttl=60\b|\bttl=255\b)",
                        str(ping_info),
                    )
                    print("form_data:linux TTL is " + str(linux))
                    windows = re.findall(r"(?:\bttl=128\b)", str(ping_info))
                    print("form_data: Windows TTL is " + str(windows))

                    if linux:
                        print("form_data: if linux ")
                        print("======================check password as admin")
                        print(host_pwd)
                        if host_pwd == "admin":
                            print("yes password is admin")
                            with open(directory + "/" + setup_name + ".txt", "a") as rk:
                                print(
                                    "form_data: going to write IP in file with admin password error"
                                )
                                rk.write(
                                    request.form[field_name + str(i)]
                                    + " Error: Password should not be 'admin'\n"
                                )
                        else:
                            ssh = pxssh.pxssh()
                            try:
                                ssh.login(
                                    request.form[field_name + str(i)],
                                    host_user,
                                    host_pwd,
                                )
                                print("form_data: SSH session login successful")
                                ssh.logout()
                                with open(
                                    directory + "/" + setup_name + ".txt", "a"
                                ) as rk:
                                    print("form_data: going to write IP in file ")

                                    if setup_name == "S2":
                                        print(
                                            "form data: splunk version name "
                                            + request.form[
                                                field_name + str(i) + "_version"
                                            ]
                                        )
                                        rk.write(
                                            request.form[field_name + str(i)]
                                            + ":"
                                            + request.form[
                                                field_name + str(i) + "_version"
                                            ]
                                            + "\n"
                                        )
                                    elif setup_name == "S4":
                                        print(
                                            "form data: splunk version name "
                                            + request.form[field_name + "_version"]
                                        )
                                        rk.write(
                                            request.form[field_name + str(i)]
                                            + ":"
                                            + request.form[field_name + "_version"]
                                            + "\n"
                                        )
                                    else:
                                        rk.write(
                                            request.form[field_name + str(i)] + "\n"
                                        )
                                    print("form_data: written done ")
                            except pxssh.ExceptionPxssh:
                                print("form_data: Error: Incorrect Password")
                                with open(
                                    directory + "/" + setup_name + ".txt", "a"
                                ) as rk:
                                    print(
                                        "form_data: going to write IP in file with error "
                                    )
                                    rk.write(
                                        request.form[field_name + str(i)]
                                        + " Error: Incorrect Password\n"
                                    )
                                    print("form_data: written done ")

                    elif windows:
                        print("form_data: OS is windows")
                        with open(directory + "/" + setup_name + ".txt", "a") as rk:
                            print("form_data: going to write IP in file ")
                            rk.write(
                                request.form[field_name + str(i)]
                                + " Error: This IP address belongs to windows VM\n"
                            )
                            print("form_data: written done ")

                    else:
                        print("form_data: unable to find OS")
                        with open(directory + "/" + setup_name + ".txt", "a") as rk:
                            print(
                                "form_data: going to write IP in file that unable to find OS "
                            )
                            rk.write(
                                request.form[field_name + str(i)]
                                + " Error: This IP address does not belongs to windows or linux VM\n"
                            )
                            print("form_data: written done ")

                else:
                    print("form_data: final else loop for OS")
                    with open(directory + "/" + setup_name + ".txt", "a") as out:
                        print("form_data: going to write IP in file for OS ")
                        out.write(
                            request.form[field_name + str(i)]
                            + " Error: Either machine is powered off or the wrong IP entered\n"
                        )
                        print("form_data: written done ")

                with open(directory + "/" + setup_name + ".txt") as rk:
                    from_file = rk.readlines()
                    from_file[-1] = from_file[-1].strip()
                    print("form_data: final IPs from setup file")
                    print(from_file)
                    print("form_data: last IP is:")
                    print(from_file[-1])
                    from_file_ip.append(from_file[-1])
                    print(from_file_ip)

            else:
                print(
                    val
                    + " form_data: Value is already there in file so not going to save"
                )

        else:
            print("No valid IP")


def field_check(alphabet, count):
    global directory, setup_name
    with open(directory + "/" + setup_name + ".txt") as rk:
        from_file_ip = rk.readlines()
    print("field_check: IP from file" + str(from_file_ip))

    total_ip = len(from_file_ip)
    head = request.form[alphabet]
    print("field_check: search head ip " + head)
    patt = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}")
    test_ip = patt.match(request.form[alphabet])
    print(test_ip)

    if test_ip:
        print("field_check: after test head ip " + head)

        if total_ip < count:
            print("field_check: less than required IPS---------------------")
            # True when validated form
            return True
        return False

    else:
        print("field_check: else part")
        return True


def file_browse(attributename, setup_app_path):
    global access_rights
    app_file = request.files[attributename]
    app_file_name = secure_filename(app_file.filename)

    if (attributename == "file1") and (app_file_name == ""):
        print("file_browse app file name = " + app_file.filename)
        print("file_browse in if loop for file1")
        return True, app_file.filename

    print("file_browse: " + app_file_name)
    print("file_browse: " + setup_app_path)

    if not os.path.isdir(setup_app_path):
        os.mkdir(setup_app_path, access_rights)
    UPLOAD_FOLDER = setup_app_path + "/"
    print("file_browse: Upload path created for app")
    print("file_browse: Upload file path = " + UPLOAD_FOLDER)
    extenstion_check = (
        "." in app_file.filename
        and app_file.filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )
    print(extenstion_check)

    if not extenstion_check:
        print("file_browse: wrong extension")
        return True, app_file_name

    request.files[attributename].save(UPLOAD_FOLDER + app_file_name)
    size = os.stat(UPLOAD_FOLDER + app_file_name).st_size
    print("file_browse: Size " + str(size))
    print(
        "file_browse: Full file path with file name is: "
        + UPLOAD_FOLDER
        + app_file_name
    )

    if size > 51380224:
        print("file_browse: More than 49mb")
        os.remove(UPLOAD_FOLDER + app_file_name)
        print("file_browse: File Removed!")
        return True, app_file_name

    else:
        print("file_browse: Valid size ")
        return False, app_file_name


def read_ip(directory, setup_name):
    with open(directory + "/" + setup_name + ".txt") as rk:
        content = rk.read()
    final_content = content.translate({ord(c): None for c in string.whitespace})
    print("read_ip : contents " + final_content)
    return content


# run the application
if __name__ == "__main__":
    logging.basicConfig(filename="logger.log")
    app.run(host="10.0.0.1", port=8000, threaded=True, debug=True)
