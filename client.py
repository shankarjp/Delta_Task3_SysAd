import os
import socket
import time
from Crypto.Cipher import AES

IP = socket.gethostbyname(socket.gethostname())
PORT = 5018
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
KEY = b'\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18'
cipher = AES.new(KEY)

cwd = os.getcwd()
CLIENT_DATA_PATH = os.path.join(cwd,"client_data")

def pad(data):
    return data + ((16 - len(data) % 16)*'{')

def encrypt(data):
    global cipher
    return cipher.encrypt(pad(data))

def encrypt_file(filename):
    global cipher
    with open(filename, 'rb') as f:
        info = f.read()
    enc = cipher.encrypt(pad(info))
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
    dec = cipher.decrypt(info).decode(FORMAT)
    l = dec.count("{")
    dec = dec[:len(dec)-l]
    with open(filename[:-4], 'wb') as f:
        f.write(dec)
    os.remove(filename)

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
            raw_data = encrypt(raw_data)
            client.send(raw_data)
        elif cmd == "SEND":
            raw_data = encrypt(raw_data)
            print(raw_data)
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
            raw_data = encrypt(raw_data)
            client.send(raw_data)
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
            raw_data = encrypt(raw_data)
            client.send(raw_data)

    print("Disconnected from the server")
    client.close()

main()