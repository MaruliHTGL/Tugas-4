import socket
import logging
from pathlib import Path

class HTTPClient:
    # # Thread Pool
    # def __init__(self, host='172.16.16.101', port=8885):
    #     self.server_location = (host, port)
    #     logging.basicConfig(level=logging.WARNING)

    # Process Pool
    def __init__(self, host='172.16.16.101', port=8889):
        self.server_location = (host, port)
        logging.basicConfig(level=logging.WARNING)

    def create_connection(self):
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect(self.server_location)
            return connection
        except Exception as err:
            logging.warning(f"Connection error: {err}")
            return None

    def execute_request(self, request_data):
        conn = self.create_connection()
        if not conn:
            return None

        try:
            conn.sendall(request_data.encode())

            response = []
            while True:
                chunk = conn.recv(2048)
                if not chunk:
                    break
                response.append(chunk.decode())
                if "\r\n\r\n" in response[-1]:
                    break

            return ''.join(response)
        except Exception as err:
            logging.warning(f"Error saat mengirim/terima data: {err}")
            return None
        finally:
            conn.close()


class FileOperations(HTTPClient):
    def fetch_file_list(self):
        request = "GET /list HTTP/1.1\r\nHost: 172.16.16.101\r\n\r\n"
        result = self.execute_request(request)
        print("\nServer response:")
        print(result)

    def send_file(self, file_path):
        try:
            file_content = Path(file_path).read_bytes()
            file_name = Path(file_path).name

            request_headers = (
                "POST /upload HTTP/1.1\r\n"
                "Host: localhost\r\n"
                f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
                f"Content-Length: {len(file_content)}\r\n"
                "\r\n"
            )

            with self.create_connection() as conn:
                if not conn:
                    return

                conn.sendall(request_headers.encode())
                conn.sendall(file_content)

                response = []
                while True:
                    data = conn.recv(2048)
                    if not data:
                        break
                    response.append(data.decode())
                    if "\r\n\r\n" in response[-1]:
                        break

                print("\nFile upload response:")
                print(''.join(response))

        except Exception as err:
            print(f"\nError during upload: {err}")

    def remove_file(self, file_name):
        payload = file_name + "\r\n"

        request = (
            "POST /delete HTTP/1.1\r\n"
            "Host: localhost\r\n"
            f"Content-Length: {len(payload)}\r\n"
            "\r\n"
            f"{payload}"
        )

        result = self.execute_request(request)
        print("\nServer response:")
        print(result)

def interactive_menu():
    client = FileOperations()

    while True:
        print("1. Lihat daftar file di server")
        print("2. Upload file ke server")
        print("3. Hapus file dari server")
        pilihan = input("\nPilih operasi (1-3): ").strip()

        if pilihan == '1':
            client.fetch_file_list()
            print("-"*50)
            print("\n")

        elif pilihan == '2':
            file_path = input("Masukkan nama file yang ingin diupload: ").strip()
            if Path(file_path).is_file():
                client.send_file(file_path)
            else:
                print("File tidak ditemukan.")
            print("-"*50)
            print("\n")

        elif pilihan == '3':
            file_name = input("Masukkan nama file yang ingin dihapus: ").strip()
            client.remove_file(file_name)
            print("-"*50)
            print("\n")

        else:
            print("Pilihan operasi 1-3.")
            print("-"*50)

if __name__ == "__main__":
    interactive_menu()
