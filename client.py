import socket
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 5008
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024

cwd = os.getcwd()
CLIENT_DATA_PATH = os.path.join(cwd,"client_data")

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    while True:
        info = client.recv(SIZE).decode(FORMAT)
        print(f"{info}")
        
        raw_data = input("> ")
        mod_data = raw_data.split("@")
        cmd = mod_data[0]

        if cmd == "HELP":
            client.send(raw_data.encode(FORMAT))
        elif cmd == "SEND":
            client.send(raw_data.encode(FORMAT))
        elif cmd == "LOGOUT":
            client.send(raw_data.encode(FORMAT))
            break
        elif cmd == "DOWNLOAD":
            filename = mod_data[1]
            client.send(raw_data.encode(FORMAT))
            data = client.recv(1024).decode(FORMAT)
            print(data)
            if data[:9] == "[SUCCESS]":
                filesize = int(data[23:])
                filepath = os.path.join(CLIENT_DATA_PATH, filename)
                f = open(filepath, 'wb')
                data = client.recv(1024)
                totalRecv = len(data)
                f.write(data)
                while totalRecv < filesize:
                    data = client.recv(1024)
                    totalRecv += len(data)
                    f.write(data)
                print("Download Complete!")
                f.close()
            else:
                print("File Does Not Exist!")

    print("Disconnected from the server")
    client.close()

main()