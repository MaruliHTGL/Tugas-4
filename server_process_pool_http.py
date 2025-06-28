from socket import *
import socket
import sys
import logging
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

# Fungsi untuk menangani koneksi client
def ProcessTheClient(connection, address):
    rcv = b""
    while True:
        try:
            data = connection.recv(1024)
            if data:
                rcv += data
                if b'\r\n\r\n' in rcv:
                    header_end = rcv.find(b'\r\n\r\n') + 4
                    header_part = rcv[:header_end].decode('utf-8', errors='ignore')

                    content_length = 0
                    for line in header_part.split('\r\n'):
                        if line.lower().startswith('content-length:'):
                            content_length = int(line.split(':')[1].strip())
                            break

                    if content_length > 0:
                        body_received = len(rcv) - header_end
                        if body_received < content_length:
                            continue

                    hasil = httpserver.proses(rcv)
                    hasil = hasil + b"\r\n\r\n"
                    connection.sendall(hasil)
                    break
            else:
                break
        except OSError:
            break
    connection.close()
    return


# Fungsi server utama
def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        my_socket.bind(('0.0.0.0', 8889))
        my_socket.listen(1)

        with ProcessPoolExecutor(20) as executor:
            while True:
                try:
                    connection, client_address = my_socket.accept()
                    p = executor.submit(ProcessTheClient, connection, client_address)
                    the_clients.append(p)

                    jumlah = ['x' for i in the_clients if i.running()]
                    print(jumlah)
                except KeyboardInterrupt:
                    print("Server Close")
                    break
    except Exception as e:
        print(f"Error starting server: {e}")
    finally:
        my_socket.close()


# Entry point
def main():
    Server()

if __name__ == "__main__":
    main()
