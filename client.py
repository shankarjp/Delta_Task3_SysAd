import socket
import os
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 5017
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
            if data[:9] == "[SUCCESS]":
                filesize = int(data[23:])
                message = input("File exists, " + str(filesize) + "Bytes, download? (Y/N)? ")
                if message == 'Y':
                    client.send("OK".encode(FORMAT))
                    filepath = os.path.join(CLIENT_DATA_PATH, filename)
                    f = open(filepath, 'wb')
                    data = client.recv(1024)
                    totalRecv = len(data)
                    f.write(data)
                    while totalRecv < filesize:
                        data = client.recv(1024)
                        totalRecv += len(data)
                        f.write(data)
                    print("Download Completed!")
                    f.close()
            else:
                print("File Does Not Exist!")
        elif cmd == "UPLOAD":
            filename = mod_data[1]
            client.send(raw_data.encode(FORMAT))
            filepath = os.path.join(CLIENT_DATA_PATH, filename)
            if os.path.isfile(filepath):
                time.sleep(0.01)
                client.send(f"[SUCCESS] File Exists! {str(os.path.getsize(filepath))}".encode(FORMAT))
                time.sleep(0.01)
                serverResponse = client.recv(SIZE).decode(FORMAT)
                if serverResponse[:2] == "OK":
                    with open(filepath, 'rb') as f:
                        num = float(os.path.getsize(filepath))/1024
                        cnum = 0
                        while True:
                            file_data = f.read(SIZE)
                            cnum += 1
                            per = (cnum/num) * 100
                            print(f"{per}% uploaded")
                            if file_data:
                                client.send(file_data)
                            else:
                                print("File Uploaded")
                                break
                else:
                    client.send("[ERROR] File Not Found!")
                time.sleep(0.01)
        elif cmd == "REMOVE":
            client.send(raw_data.encode(FORMAT))

    print("Disconnected from the server")
    client.close()

main()