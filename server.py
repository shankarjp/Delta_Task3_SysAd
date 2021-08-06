import os
import socket
import threading
import time
from Crypto.Cipher import AES

IP = socket.gethostbyname(socket.gethostname())
PORT = 5022
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
KEY = b'\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18'
cipher = AES.new(KEY)

cwd = os.getcwd()
SERVER_DATA_PATH = os.path.join(cwd,"server_data")

def pad(data):
    return data + ((16 - len(data) % 16)*'{')

def pad_file(data):
    return data + ((16 - len(data) % 16) * b"\0")

def encrypt(data):
    global cipher
    return cipher.encrypt(pad(data))

def encrypt_file(filename):
    global cipher
    with open(filename, 'rb') as f:
        info = f.read()
    enc = cipher.encrypt(pad_file(info))
    with open(filename + ".enc", 'wb') as f:
        f.write(enc)
    os.remove(filename)

def decrypt(data):
    global cipher
    dec = cipher.decrypt(data).decode(FORMAT)
    l = dec.count("{")
    return dec[:len(dec)-l]

def decrypt_file(filename):
    global cipher
    with open(filename, 'rb') as f:
        info = f.read()
    dec = cipher.decrypt(info)
    l = dec.count(b"\0")
    dec = dec[:len(dec)-l]
    with open(filename[:-4], 'wb') as f:
        f.write(dec)
    os.remove(filename)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connnected")
    conn.send("Welcome to the File Server!".encode(FORMAT))

    while True:
        data = conn.recv(SIZE)
        data = decrypt(data)
        data = data.split("@")
        cmd = data[0]
        if cmd == "LOGOUT":
            break
        elif cmd == "HELP":
            conn.send("HELP Section\n".encode(FORMAT))
            conn.send("SEND@<message> : send a message to server\n".encode(FORMAT))
            conn.send("UPLOAD@<filename> : upload file to server_data\n".encode(FORMAT))
            conn.send("DOWNLOAD@<filename> : download file from server_data\n".encode(FORMAT))
            conn.send("REMOVE@<filename> : remove file from server_data\n".encode(FORMAT))
            conn.send("LIST@server : list files in server directory\n".encode(FORMAT))
            conn.send("LIST@client : list files in client directory\n".encode(FORMAT))
            conn.send("HELP : help section\n".encode(FORMAT))
            conn.send("LOGOUT : logout of client\n".encode(FORMAT))
        elif cmd == "SEND":
            alert = f"[MESSAGE] {addr} {data[1]}"
            print(f"{alert}")
            time.sleep(0.01)
            conn.send("Message Received!\n".encode(FORMAT))
        elif cmd == "DOWNLOAD":
            filename = data[1]
            filepath = os.path.join(SERVER_DATA_PATH, filename)
            if os.path.isfile(filepath):
                conn.send(f"[SUCCESS] File Exists! {str(os.path.getsize(filepath))}".encode(FORMAT))
                userResponse = conn.recv(1024).decode(FORMAT)
                if userResponse[:2] == "OK":
                    encrypt_file(filepath)
                    with open(filepath + ".enc", 'rb') as f:
                        while True:
                            file_data = f.read(1024)
                            if file_data:
                                conn.send(file_data)
                            else:
                                print("File Downloaded!")
                                break
                    decrypt_file(filepath + ".enc")
                            
            else:
                conn.send("[ERROR] File Not Found!".encode(FORMAT))
            time.sleep(0.1)
            conn.send("Task finished!\n".encode(FORMAT))
        elif cmd == "UPLOAD":
            filename = data[1]
            data = conn.recv(SIZE).decode(FORMAT)
            time.sleep(0.01)
            print("check1")
            if data[:9] == "[SUCCESS]":
                print("check2")
                filesize = int(data[23:])
                conn.send("OK".encode(FORMAT))
                filepath = os.path.join(SERVER_DATA_PATH, filename)
                f = open(filepath + ".enc", 'wb')
                time.sleep(0.01)
                data = conn.recv(SIZE)
                totalRecv = len(data)
                f.write(data)
                time.sleep(0.01)
                while totalRecv < filesize:
                    data = conn.recv(SIZE)
                    totalRecv += len(data)
                    f.write(data)
                print("Upload Completed!")
                f.close()
                decrypt_file(filepath + ".enc")
                conn.send("Task Finished!\n".encode(FORMAT))
            else:
                print("check3")
                conn.send("File Does Not Exist!\n".encode(FORMAT))
                print("check4")
        elif cmd == "CONTINUE":
            conn.send(" ".encode(FORMAT))
            time.sleep(0.01)
        else:
            conn.send("Invalid Command! Try Again.\n".encode(FORMAT))
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