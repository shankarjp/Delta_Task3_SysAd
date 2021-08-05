import os
import socket
import threading
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 5017
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

cwd = os.getcwd()
SERVER_DATA_PATH = os.path.join(cwd,"server_data")

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connnected")
    conn.send("Welcome to the File Server!".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
        if cmd == "LOGOUT":
            break
        elif cmd == "HELP":
            conn.send("HELP Section\n".encode(FORMAT))
            conn.send("SEND@<message> : send a message to server\n".encode(FORMAT))
            conn.send("UPLOAD@<filename> : upload a file to server_data\n".encode(FORMAT))
            conn.send("DOWNLOAD@<filename> : download a file from server_data\n".encode(FORMAT))
            conn.send("HELP : help section\n".encode(FORMAT))
            conn.send("LOGOUT : logout of client".encode(FORMAT))
        elif cmd == "SEND":
            alert = f"[MESSAGE] {addr} {data[1]}"
            print(f"{alert}")
            conn.send("Message Received!".encode(FORMAT))
        elif cmd == "DOWNLOAD":
            filename = data[1]
            filepath = os.path.join(SERVER_DATA_PATH, filename)
            if os.path.isfile(filepath):
                conn.send(f"[SUCCESS] File Exists! {str(os.path.getsize(filepath))}".encode(FORMAT))
                userResponse = conn.recv(1024).decode(FORMAT)
                if userResponse[:2] == "OK":
                    with open(filepath, 'rb') as f:
                        num = float(os.path.getsize(filepath))/1024
                        cnum = 0
                        while True:
                            file_data = f.read(1024)
                            cnum += 1
                            per = (cnum/num) * 100
                            print(f"{per}% downloaded")
                            if file_data:
                                conn.send(file_data)
                            else:
                                print("File Downloaded!")
                                break
                            
            else:
                conn.send("[ERROR] File Not Found!")
            time.sleep(0.1)
            conn.send("Task finished!".encode(FORMAT))
        elif cmd == "SUCCESS":
            msg = data[1]
            print(f"{msg}")
    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()


def main():
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

main()