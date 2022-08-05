# AlphaQ File Server

Dipesh needs a file server to share files between members. Your task is to create a file server and client to send and receive files using sockets.

## Normal Mode

 - Clients must be able to receive files of respective domains(SysAd, WebDev, AppDev) from the file server.
 - Multiple clients must be able to download files at same time.
 - Dockerize the server.

## Superuser Mode

 - Users must be able to upload files to the server.
 - Users must be able to search for files in the server using regex.
 - Enable authentication for uploading/downloading/removing files.
 - Encrypt the files being transfered using (AES-256).

## Note(For all modes):

Use `Python` for the server. You are not allowed to use any third-party libraries for implementing the file server and client. Consult your mentor before using any libraries. You are allowed to use the `pycrypto` library for AES encryption.

## Deadline

10th Aug 2021 | 11.59 pm

_NOTE: Normal Mode is necessary to complete the task. Superuser mode is highly encouraged_

## Resources

 - [Python Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html)
 - [Real Python tutorial for sockets](https://realpython.com/python-sockets/)
 - [Threading](https://realpython.com/intro-to-python-threading/)
 - [Pycrypto library for AES](https://www.dlitz.net/software/pycrypto/api/current/)