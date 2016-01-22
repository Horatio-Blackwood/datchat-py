# Author:   Adam Anderson
# Date:     Jan 5, 2015
# Updated:  Jan 21, 2016
# Python:   3.4.0+

from common import msg_header
import socket
import sys
import threading
import tkinter as tk

# Server Parameters
HOST = "localhost"
PORT = 55601


class Client(object):

    def __init__(self):
        self.name = "Me"

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(True)
        self.display = ClientDisplay(self.connect, self.send_message)
        self.display.launch()

    def connect(self, host, port):
        try:
            print("connecting.")
            self.socket.connect((host, port))
        except socket.error:
            print("Unable to connect to server:  ", host, ":", port)
            sys.exit()

        # Listen for incoming messages
        threading.Thread(target=self.receive).start()

    def receive(self):
        print("Started listening thread.")
        while True:
            try:
                if self.socket is not None:
                    message = self.socket.recv(1500).decode()
                    self.display.show_incoming_msg(message)
            except OSError as msg:
                print("Socket error 1.  :(")
                break

    def send_message(self, message):
        self.socket.send(message.encode())
        if message == "/quit":
            print("i have quit")
            self.socket.close()
            self.display.show_incoming_msg("Disconnected from server.")


class ClientDisplay(object):

    def __init__(self, connect_function, msg_sender):
        self.connect_function = connect_function
        self.msg_sender = msg_sender

        self.root = tk.Tk()
        main_frame = tk.Frame(self.root)
        self.root.wm_title("datchat v1.0")

        # IP Field
        ip_label = tk.Label(main_frame, text="Server IP:").grid(row=0, column=0, padx=2, pady=2, sticky=tk.E)
        self.ip_field = tk.Entry(main_frame)
        self.ip_field.grid(row=0, column=1, padx=2, pady=2, sticky=(tk.N, tk.S, tk.W, tk.E))
        self.ip_field.insert(tk.END, HOST)

        # Port Field
        port_label = tk.Label(main_frame, text="Server Port:").grid(row=0, column=2, padx=2, pady=2, sticky=tk.E)
        self.port_field = tk.Entry(main_frame)
        self.port_field.grid(row=0, column=3, padx=2, pady=2, sticky=(tk.N, tk.S, tk.W, tk.E))
        self.port_field.insert(tk.END, str(PORT))

        # Connect Button
        self.connect_button = tk.Button(main_frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=4, padx=2, pady=2, sticky=(tk.N, tk.S, tk.W, tk.E))

        # Chat Area
        self.chat_area = tk.Text(main_frame)
        self.chat_area.grid(row=1, column=0, columnspan=5, padx=2, pady=2)

        # Chat Entry
        self.msg_entry = tk.Entry(main_frame)
        self.msg_entry.grid(row=5, column=0, columnspan=4, padx=2, pady=2, sticky=(tk.N, tk.S, tk.W, tk.E))
        self.msg_entry.bind('<Return>', self.__send_message)

        # Send Button
        self.send_button = tk.Button(main_frame, text="Send", command=self.__send)
        self.send_button.grid(row=5, column=4, padx=2, pady=2, sticky=(tk.N, tk.S, tk.W, tk.E))

        main_frame.grid(row=0, column=0)

    def launch(self):
        self.root.mainloop()

    def connect(self):
        host = self.ip_field.get()
        port = int(self.port_field.get())
        print("Connecting to server(", host, " on port number", port)
        self.connect_function(host, port)

    def show_incoming_msg(self, message):
        self.chat_area.insert(tk.END, message)
        self.chat_area.insert(tk.END, "\n")
        self.chat_area.yview(tk.END)

    def __send(self):
        self.__send_message(None)

    def __send_message(self, button):
        message = self.msg_entry.get()
        self.msg_sender(msg_header + message)
        self.msg_entry.delete(0, tk.END)
