import sys
import socket
import os

class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def connect_to_server(self, server_ip, server_port, username, clientIP, local_port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))

        # Send the CONNECT request to the server
        connect_request = f"CONNECT {username} {clientIP} {local_port}"
        client_socket.send(connect_request.encode())    

        # Receive and print the server's response
        response = client_socket.recv(1024).decode()
        print(response)

        # Close the client socket
        client_socket.close()

    def disconnect_from_server(self, server_ip, server_port, username):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))

        # Send the DISCONNECT request to the server
        disconnect_request = f"DISCONNECT {username}"
        client_socket.send(disconnect_request.encode())

        # Receive and print the server's response
        response = client_socket.recv(1024).decode()
        print(response)

        # Close the client socket
        client_socket.close()

    def get_content_list(self, server_ip, server_port):
        # Connect to the server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server_ip, server_port))

        # Send getting content list request
        request = f"CONTENTLIST {self.ip} {self.port}"
        server_socket.send(request.encode())

        # Receive and process content list
        response = server_socket.recv(1024).decode()
        contents = response.split(",")
        print("\nSelect content to download: ")
        for content in contents:
            print(content)
        print(" ")

        # Close the server connection
        server_socket.close()

    def download_content(self, content_name, source_ip, source_port):
        # Connect to the source peer
        source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        source_socket.connect((source_ip, source_port))

        # Send download request
        request = f"DOWNLOAD {content_name}"
        source_socket.send(request.encode())

        # Receive content chunks
        content_chunks = []
        while True:
            chunk = source_socket.recv(1024)
            if not chunk:
                break
            content_chunks.append(chunk)

        # Save the content to a file
        with open(content_name, "wb") as file:
            for chunk in content_chunks:
                file.write(chunk)

        print(f"\nDownloaded content '{content_name}' from {source_ip}:{source_port}")

        # Close the source connection
        source_socket.close()

    def upload_content(self, content_path, server_ip, server_port):
        # Connect to the server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server_ip, server_port))

        # Send upload request
        request = f"UPLOAD {os.path.basename(content_path)}"
        server_socket.send(request.encode())

        # Read content from the file
        with open(content_path, "rb") as file:
            while True:
                chunk = file.read(1024)
                if not chunk:
                    break
                server_socket.send(chunk)

        print(f"\nUploaded content '{os.path.basename(content_path)}' to the server")

        # Close the server connection
        server_socket.close()

    def get_user_list(self, server_ip, server_port):
        # Connect to the server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server_ip, server_port))

        # Send getting user list request
        request = f"LIST_USERS {self.ip} {self.port}"
        server_socket.send(request.encode())

        # Receive and print user list
        response = server_socket.recv(1024).decode()
        print("\nActive Users:")
        print(response)

        # Close the server connection
        server_socket.close()


def main():
    server_ip = input("Enter the IP address of the server: ")
    server_port = int(input("Enter the port of the server: "))

    clientIP = input("Enter the IP address of this client: ")
    local_port = int(input("Enter the port to listen for connections: "))
    username = input("Enter your username: ")

    client = Client(clientIP, local_port)

    # Connect to the server
    client.connect_to_server(server_ip, server_port, username, clientIP, local_port)

    while True:
        print("\nChoose an option:")
        print("1. Get Content List")
        print("2. Download Content")
        print("3. Upload Content")
        print("4. Get User List")
        print("5. Disconnect from Server")
        print("6. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            client.get_content_list(server_ip, server_port)
        elif choice == "2":
            content_name = input("Enter the name of the content to download: ")
            source_ip = input("Enter the IP address of the source peer: ")
            source_port = int(input("Enter the port of the source peer: "))
            client.download_content(content_name, source_ip, source_port)
        elif choice == "3":
            content_path = input("Enter the path to the content file: ")
            client.upload_content(content_path, server_ip, server_port)
        elif choice == "4":
            client.get_user_list(server_ip, server_port)
        elif choice == "5":
            client.disconnect_from_server(server_ip, server_port, username)
            break
        elif choice == "6":
            client.disconnect_from_server(server_ip, server_port, username)
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
