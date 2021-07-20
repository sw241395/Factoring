import socket
import time
import threading
from colorama import Fore, Style
import ClientFileHandler
import RangeChecker

# Get configs
file_handler = ClientFileHandler.ClientFileHandler()

# start thread for the range checker
range_tester = RangeChecker.RangeChecker()
thread = threading.Thread(target=range_tester.run, args=(), daemon=True)
thread.start()

# start socket to let the server know its still running
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('[Socket]: Opening socket...')
    s.bind((file_handler.client_ip, file_handler.client_port))
    s.listen()
    while True:
        print('[Socket]: Socket waiting for connection...')
        conn, addr = s.accept()
        data = conn.recv(100)

        print('[Socket]: Socket connection established')
        if data == b"check":
            conn.sendall(b"Ok")
            print('[Socket]: Check responded successfully')
        elif data == b"stop":
            print('[Socket]: Solution found, restarting thread...')
            # Stop the thread
            range_tester.terminate()
            while thread.is_alive():
                print('[Socket]: Waiting for thread to close...')
                time.sleep(5)

            # restart the thread
            range_tester = RangeChecker.RangeChecker()
            thread = threading.Thread(target=range_tester.run, args=(), daemon=True)
            thread.start()
            print('[Socket]: Thread restarted')
            conn.sendall(b"Ok")

        conn.close()
