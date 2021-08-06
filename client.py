import os
import socket
import time
from Crypto.Cipher import AES

IP = socket.gethostbyname(socket.gethostname())
PORT = 5021
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
KEY = b'\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18'
cipher = AES.new(KEY)

cwd = os.getcwd()
SERVER_DATA_PATH = os.path.join(cwd,"server_data")
GENERAL_DATA_PATH = os.path.join(cwd,"client_data")

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
    l = dec.count('{')
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

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    connection = True
    domain = input(">> Enter your Domain (web/app/sys) : ")
    if domain == "web":
        CLIENT_DATA_PATH = os.path.join(GENERAL_DATA_PATH, "web")
    elif domain == "app":
        CLIENT_DATA_PATH = os.path.join(GENERAL_DATA_PATH, "app")
    elif domain == "sys":
        CLIENT_DATA_PATH = os.path.join(GENERAL_DATA_PATH, "sys")
    else:
        connection = False
    while connection:
        info = client.recv(SIZE).decode(FORMAT)
        print(f"{info}")
        
        raw_data = input("> ")
        mod_data = raw_data.split("@")
        cmd = mod_data[0]

        if cmd == "HELP":
            raw_data = encrypt(raw_data)
            client.send(raw_data)
        elif cmd == "SEND":
            raw_data = encrypt(raw_data)
            client.send(raw_data)
        elif cmd == "LOGOUT":
            raw_data = encrypt(raw_data)
            client.send(raw_data)
            break
        elif cmd == "DOWNLOAD":
            filename = mod_data[1]
            raw_data = encrypt(raw_data)
            client.send(raw_data)
            data = client.recv(1024).decode(FORMAT)
            if data[:9] == "[SUCCESS]":
                filesize = int(data[23:])
                message = input("File exists, " + str(filesize) + "Bytes, download? (Y/N)? ")
                if message == 'Y':
                    client.send("OK".encode(FORMAT))
                    filepath = os.path.join(CLIENT_DATA_PATH, filename)
                    f = open(filepath + ".enc", 'wb')
                    data = client.recv(1024)
                    totalRecv = len(data)
                    f.write(data)
                    while totalRecv < filesize:
                        data = client.recv(1024)
                        totalRecv += len(data)
                        f.write(data)
                    print("Download Completed!")
                    f.close()
                    decrypt_file(filepath + ".enc")
            else:
                print("File Does Not Exist!")
        elif cmd == "UPLOAD":
            filename = mod_data[1]
            raw_data = encrypt(raw_data)
            client.send(raw_data)
            filepath = os.path.join(CLIENT_DATA_PATH, filename)
            if os.path.isfile(filepath):
                time.sleep(0.01)
                client.send(f"[SUCCESS] File Exists! {str(os.path.getsize(filepath))}".encode(FORMAT))
                time.sleep(0.01)
                serverResponse = client.recv(SIZE).decode(FORMAT)
                if serverResponse[:2] == "OK":
                    encrypt_file(filepath)
                    with open(filepath + ".enc", 'rb') as f:
                        while True:
                            file_data = f.read(SIZE)
                            if file_data:
                                client.send(file_data)
                            else:
                                print("File Uploaded")
                                break
                    decrypt_file(filepath + ".enc")
                else:
                    client.send("[ERROR] File Not Found!")
                time.sleep(0.01)
        elif cmd == "REMOVE":
            files = os.listdir(CLIENT_DATA_PATH)
            filename = mod_data[1]
            if len(files) == 0:
                print("Client Directory is empty!")
            else:
                if filename in files:
                    os.system(f"rm {CLIENT_DATA_PATH}/{filename}")
                    print("File Successfully Removed!")
                else:
                    print("File Not Found!")
            client.send(encrypt("CONTINUE"))
        elif cmd == "LIST":
            section = mod_data[1]
            if section == "server":
                files = os.listdir(SERVER_DATA_PATH)
                for f in files:
                    print(f"{f}")
                    client.send(encrypt("CONTINUE"))
                    time.sleep(0.01)
            elif section == "client":
                files = os.listdir(CLIENT_DATA_PATH)
                for f in files:
                    print(f"{f}")
                    client.send(encrypt("CONTINUE"))
                    time.sleep(0.01)
            else:
                client.send(encrypt("RANDOM"))
                time.sleep(0.01)
        else:
            raw_data = encrypt(raw_data)
            client.send(raw_data)

    print("Disconnected from the server")
    client.close()

main()