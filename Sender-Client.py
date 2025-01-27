import socket
from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, END, Frame, Toplevel, filedialog
from PIL import Image, ImageTk
import io

class RemoteControllerClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Raspberry Pi Remote Controller")
        self.root.geometry("800x600")
        self.client_socket = None

        # Server connection fields
        self.server_ip_label = Label(root, text="Server IP:")
        self.server_ip_label.grid(row=0, column=0, padx=5, pady=5)
        self.server_ip_entry = Entry(root, width=20)
        self.server_ip_entry.grid(row=0, column=1, padx=5, pady=5)

        self.server_port_label = Label(root, text="Server Port:")
        self.server_port_label.grid(row=0, column=2, padx=5, pady=5)
        self.server_port_entry = Entry(root, width=10)
        self.server_port_entry.grid(row=0, column=3, padx=5, pady=5)
        self.server_port_entry.insert(0, "5000")

        self.connect_button = Button(root, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=4, padx=5, pady=5)

        # Command buttons
        self.sysinfo_button = Button(root, text="System Info", command=self.get_sysinfo)
        self.sysinfo_button.grid(row=1, column=0, padx=5, pady=5)

        self.list_files_button = Button(root, text="List Files", command=self.list_files)
        self.list_files_button.grid(row=1, column=1, padx=5, pady=5)

        self.screenshot_button = Button(root, text="Take Screenshot", command=self.take_screenshot)
        self.screenshot_button.grid(row=1, column=2, padx=5, pady=5)

        self.restart_button = Button(root, text="Restart", command=lambda: self.send_command("restart"))
        self.restart_button.grid(row=1, column=3, padx=5, pady=5)

        self.shutdown_button = Button(root, text="Shutdown", command=lambda: self.send_command("shutdown"))
        self.shutdown_button.grid(row=1, column=4, padx=5, pady=5)

        # Output area
        self.output_frame = Frame(root)
        self.output_frame.grid(row=3, column=0, columnspan=5, padx=5, pady=5)

        self.output_text = Text(self.output_frame, wrap="word", height=20, width=80, state="disabled")
        self.output_text.pack(side="left", fill="both", expand=True)

        self.scrollbar = Scrollbar(self.output_frame, command=self.output_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=self.scrollbar.set)

    def connect_to_server(self):
        server_ip = self.server_ip_entry.get()
        server_port = int(self.server_port_entry.get())

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, server_port))
            self.display_output(f"Connected to server at {server_ip}:{server_port}")
        except Exception as e:
            self.display_output(f"Connection failed: {e}")

    def send_command(self, command):
        if self.client_socket:
            try:
                self.client_socket.send(command.encode())
                response = self.client_socket.recv(4096).decode()
                self.display_output(response)
            except Exception as e:
                self.display_output(f"Error: {e}")
        else:
            self.display_output("Not connected to any server.")

    def get_sysinfo(self):
        self.send_command("sysinfo")

    def list_files(self):
        self.send_command("list_files .")

    def take_screenshot(self):
        if self.client_socket:
            try:
                self.client_socket.send(b"take_screenshot")
                screenshot_data = self.client_socket.recv(65536)
                screenshot_image = Image.open(io.BytesIO(screenshot_data))
                screenshot_image.show()  # Display the screenshot
            except Exception as e:
                self.display_output(f"Error: {e}")

    def display_output(self, message):
        self.output_text.config(state="normal")
        self.output_text.insert(END, f"{message}\n")
        self.output_text.config(state="disabled")
        self.output_text.see(END)

if __name__ == "__main__":
    root = Tk()
    app = RemoteControllerClient(root)
    root.mainloop()
