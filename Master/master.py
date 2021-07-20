import time
import socket
import threading
import sql
import FlaskAPI
from colorama import Fore, Style
import MasterFileHandler

 
# initialise the configs
file_handler = MasterFileHandler.MasterFileHandler()
# initialise sql connection
sql_connection = sql.sql()


# Method to start flask server in separate thread
def start_flask():
    FlaskAPI.app.run(host=file_handler.master_ip, debug=False)


# Start the flask api in an different thread
thread = threading.Thread(target=start_flask, args=(), daemon=True)
thread.start() 


# Start loop for checking running clients
while True:
    # Do a check every 5 mins
    time.sleep(300)
    print('[Check]: Starting check run...')

    # Get IPs from SQL and loop trough them
    for row in sql_connection.get_ips():
        # some preprocessing to format the list to only have the IPs
        ip = row[0]
        print('[Check]: Checking:', ip)

        response = None
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((ip, file_handler.client_port))
                s.sendall(b'check')
                response = s.recv(100)

            if response != b'Ok':
                raise socket.timeout('')
            print('[Check]: {} OK'.format(ip))

        except ConnectionRefusedError as e:
            print(Fore.RED, '[Check]: Error:')
            print(e, Style.RESET_ALL)
            print('[Check]: Error connecting with {}, removing from db'.format(ip))
            sql_connection.remove_ip_from_row(ip)  
    print('[Check]: Check run complete')  
