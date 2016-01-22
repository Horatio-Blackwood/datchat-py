# Author:   Adam Anderson
# Date:     Jan 5, 2015
# Updated:  Jan 21, 2016
# Python:   3.3.0+

from common import msg_header
import socket
import threading
import time

# TODO - Add special server message for getting the time; '/time'
# TODO - Add special server message for sending a private IM to a specific user; '/<username> <message>'



# Server Parameters
#	- empty string means to work on all network interfaces
HOST = ""
#	- port to listen for clients on
PORT = 55601
#	- Server Name
SERVER_NAME = "Server"
#	- Log File Name
LOG_NAME = "chatserver"
#	- Who to send messages to
ALL = "ALL"


class Server(object):

    def __init__(self):
        # initialize connection list
        self.connections = {}

        # initialize socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((HOST, PORT))

    def start(self):
        # Start Listening for Connections on separate thread.
        self.socket.listen(1)
        threading.Thread(target=self.listen_for_connections).start()

        # Listen for incoming messages and broadcast them.
        while True:
            to_remove = []
            try:
                for name, conn in self.connections.items():
                    try:
                        message = conn.recv(1500)
                        message = message.strip().decode()
                    except socket.error:
                        continue

                    print("Received message:  ", message, " from ", name)
                    message = self.check_msg(message)
                    if message is None:
                        print("Received invalid message from user, removing user.")
                        to_remove.append(name)
                        break

                    # Handle Special datchat messages
                    if message == "/quit":
                        # Handle quit messages
                        to_remove.append(name)

                    elif message == "/online":
                        # Handle - who's on datchat message
                        to_send = "Users on datchat:  \n"
                        for user, userconn in self.connections.items():
                            to_send += "  - "
                            to_send += user
                            to_send += "\n"
                        self.broadcast(name, SERVER_NAME, to_send)
                    else:
                        # Handle Normal Message
                        if message:
                            self.broadcast(ALL, name, message)

                time.sleep(1)

                # Remove any Bad Connections
                for name in to_remove:
                    del self.connections[name]
                    self.broadcast(ALL, SERVER_NAME, name + " has left the room.")

            except (SystemExit, KeyboardInterrupt):
                print("System Exit or Keyboard interrupt.")
                break

    def accept(self, conn, client_ip):

        def connect():
            name = None
            while name is None:
                conn.send("Please enter your name and click send.".encode())
                try:
                    # get three-tuple of hostname, ???, and IP Address
                    client_host = socket.gethostbyaddr(client_ip)
                    username = conn.recv(1500).strip().decode() + "@" + client_host[0]
                    name = self.check_msg(username)

                except socket.error:
                    print("Socket Error (0) on connection.  Did not add new chat user.  :(")
                    continue

                if name in self.connections:
                    print("Client tried to use an existing username: ", name)
                    conn.send("Name already in use.  Please try a different name.".encode())
                    name = None
                elif name:
                    print("Accepted new client: ", name)
                    conn.setblocking(False)
                    self.connections[name] = conn
                    self.broadcast(ALL, SERVER_NAME, name + " has entered the room.")

        threading.Thread(target=connect).start()
        print("Finished starting accept thread.")

    def broadcast(self, send_to, name, message):
        print("Broadcasting message: ", message, "to", send_to)
        broadcast_message = (name + ":  " + message)
        if send_to == ALL:
            to_remove = []
            for to_name, conn in self.connections.items():
                try:
                    conn.send(broadcast_message.encode())
                except socket.error:
                    to_remove.append(to_name)
                    pass

            # Remove any Bad Connections
            for name in to_remove:
                print("Socket error (4) when sending message to user", name, ".  Removing user.  :(")
                del self.connections[name]

        else:
            to_remove = []
            for to_name, conn in self.connections.items():
                try:
                    if to_name == send_to:
                        conn.send(broadcast_message.encode())
                except socket.error:
                    to_remove.append(to_name)
                    pass

            # Remove any Bad Connections
            for name in to_remove:
                print("Socket error (5) when sending message to user", name, ".  Removing user.  :(")
                del self.connections[name]

    def check_msg(self, message):
        if message.startswith(msg_header):
            message = message[len(msg_header):len(message)]
            return message
        else:
            return None

    def listen_for_connections(self):
        print("Listening on port " + str(PORT))
        while True:
            # Accept New Connections
            try:
                print("accepting connection")
                conn, addr = self.socket.accept()
                client_ip = str(addr[0])
                self.accept(conn, client_ip)
            except OSError as msg:
                print("Socket error 1.  :(")
                break
        print("Connection count:  ", len(self.connections.keys()))
