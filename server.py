import socket
import os
import threading


class Server:
    def __init__(self, ip, ports):
        self.ip = ip
        self.connected_users = {}
        self.ports = ports

    def serve_content(self, content_path):
        serving_sockets = self.create_serving_sockets()

        self.display_active_users()

        while True:
            for serving_socket in serving_sockets:
                serving_socket.settimeout(1)

                try:
                    client_socket, client_address = serving_socket.accept()
                    request = client_socket.recv(1024).decode()
                    request_parts = request.split(" ")
                    command = request_parts[0]

                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, content_path, command, request_parts),
                    )
                    client_thread.start()

                except socket.timeout:
                    pass

    def create_serving_sockets(self):
        serving_sockets = []
        for port in self.ports:
            serving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serving_socket.bind((self.ip, port))
            serving_socket.listen(1)
            serving_sockets.append(serving_socket)
            print(f"Listening for download requests on {self.ip}:{port}")

        return serving_sockets

    def display_active_users(self):
        if len(self.connected_users) > 0:
            print("Active Users:")
            for username, (ip, port) in self.connected_users.items():
                print(f"Username: {username}, IP: {ip}, Port: {port}")
        else:
            print("No active users.")

    def handle_client(self, client_socket, content_path, command, request_parts):
        if command == "CONTENTLIST":
            self.send_content_list(client_socket, content_path)
        elif command == "DOWNLOAD":
            content_name = request_parts[1]
            content_file_path = os.path.join(content_path, content_name)
            self.send_content(client_socket, content_file_path)
        elif command == "LIST_USERS":
            self.send_user_list(client_socket)
        elif command == "CONNECT":
            username = request_parts[1]
            clientIP = request_parts[2]
            clientPort = request_parts[3]
            self.add_user(client_socket, username, clientIP, clientPort)
            message = "User connected."
            client_socket.send(message.encode())
        elif command == "DISCONNECT":
            username = request_parts[1]
            self.remove_user(username)
            message = "User disconnected."
            client_socket.send(message.encode())
        elif command == "UPLOAD":
            content_name = request_parts[1]
            self.receive_content(client_socket, content_path, content_name)

        client_socket.close()

    def add_user(self, client_socket, username, clientIP, clientPort):
        self.connected_users[username] = (clientIP, clientPort)

    def remove_user(self, username):
        if username in self.connected_users:
            del self.connected_users[username]

    def send_user_list(self, client_socket):
        user_list = "\n".join([f"{username} ({ip}:{port})" for username, (ip, port) in self.connected_users.items()])
        client_socket.send(user_list.encode())

    def send_content_list(self, client_socket, content_path):
        try:
            content_list = os.listdir(content_path)
            content_list_str = ",".join(content_list)
            client_socket.send(content_list_str.encode())
        except FileNotFoundError:
            print(f"Content path '{content_path}' not found.")

    def send_content(self, client_socket, content_file_path):
        try:
            with open(content_file_path, "rb") as file:
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        break
                    client_socket.send(chunk)
        except FileNotFoundError:
            print(f"Content '{content_file_path}' not found.")

    def receive_content(self, client_socket, content_path, content_name):
        content_file_path = os.path.join(content_path, content_name)

        try:
            with open(content_file_path, "wb") as file:
                while True:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        break
                    file.write(chunk)

            print(f"\nReceived content '{content_name}' from client.")

        except IOError as e:
            print(f"Error receiving content '{content_name}': {str(e)}")


def main():
    ip = input("Enter the IP address of the server: ")
    ports = input("Enter the ports for serving the content (comma-separated): ")
    content_path = input("Enter the path to the directory where the content is stored: ")

    ports = [int(port) for port in ports.split(",")]

    server = Server(ip, ports)
    server.serve_content(content_path)


if __name__ == "__main__":
    main()
