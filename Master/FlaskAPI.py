from flask import Flask, request, jsonify
from colorama import Fore, Style
import sql
import socket
import threading
import time
import MasterFileHandler


# initialise the API
app = Flask(__name__)
# initialise the configs
file_handler = MasterFileHandler.MasterFileHandler()
# initialise sql connection
sql_connection = sql.sql()


@app.route('/connect', methods=['GET'])
def initial_connect():
    '''
    Where clients come to get a range to work on
    '''
    # setting up initial variables for returned vale
    returned_message = 'No ranges to assign'
    status_code = 503 # Service Unavailable
    
    try:
        # get the ipv4 of the client
        ipv4 = request.remote_addr
        # assign IP to a range
        N, Lower_Limit, Upper_Limit = sql_connection.assign_client_to_row(str(ipv4))

        returned_message = jsonify({'N': N, 'Lower_Limit': Lower_Limit, 'Upper_Limit': Upper_Limit})
        status_code = 200
    # if there is an error in the json sent
    except KeyError as e: 
        returned_message, status_code = __print_malformed_json_error(e)
    # if there are no ranges to assign
    except TypeError as e:
        print(Fore.RED, '[Flask]: Error:')
        print(e, Style.RESET_ALL)
        
    print('[Flask]: returned message:', returned_message, ', Status Code:',status_code)
    return returned_message, status_code


@app.route('/solution', methods=['POST'])
def check_solution():
    '''
    Clients post here when they have completed the work
    If the solution received is 0, it means no solution was found
    '''
    # setting up initial variables for returned vale
    returned_message = 'Solution found'
    status_code = 200

    try:
        # get the json and parameters
        request_data = request.get_json()
        N = request_data['N']
        Lower_Limit = request_data['Lower_Limit']
        Upper_Limit = request_data['Upper_Limit']
        solution = request_data['solution']
        # get the IP
        ipv4 = request.remote_addr

        if solution == "0" or solution == 0:
            sql_connection.remove_completed_row(N, Lower_Limit, Upper_Limit, ipv4)
            returned_message = 'Removed row'
        # check solution
        elif int(N) % int(solution) == 0:
            # save the result
            file_handler.update_solution_file(N, solution)
            
            # send kill message to clients (in separate thread)  
            killing_thread = threading.Thread(target=__kill_clients, args=(N,), daemon=True)
            killing_thread.start() 
            # wait to give the db time to get the results before deleting them
            time.sleep(5)

            # remove all N from table
            sql_connection.remove_completed_N(N)
        # If solution is wrong
        else:
            returned_message = 'Wrong solution'
            status_code = 406 # 406 Not Acceptable
    # if there is an error in the json sent
    except KeyError as e: 
        returned_message, status_code = __print_malformed_json_error(e)
    
    # return data ready to be processed
    print('[Flask]: returned message:', returned_message, ', Status Code:',status_code)
    return returned_message, status_code


# Way to add new integers to the DB
@app.route('/add', methods=['POST'])
def add_new_n():
    '''
    Method to add new values of N into the DB
    '''
    # setting up initial variables for returned vale
    returned_message = 'Added'
    status_code = 200
    
    try:
        # get the json and ipv4 parameter
        request_data = request.get_json()
        N = request_data['N']

        # Check N is an int and not in the DB already
        if sql_connection.check_N_availability(N) == 0 and N.isdigit():
            # Do initial check for the primes 2 and 3 as the clients cannot check these values
            if int(N) % 2 == 0:
                # add solution to file
                file_handler.update_solution_file(N, '2')
            elif int(N) % 3 == 0:
                # add solution to file
                file_handler.update_solution_file(N, '3')
            else:
                adding_partitions_thread = threading.Thread(target=__add_partitions, args=(N,), daemon=True)
                adding_partitions_thread.start()               
            
        # N is not available or not an int
        else:
            returned_message = 'Error with N'        
    # if there is an error in the json sent
    except KeyError as e: 
        # Print the error
        returned_message, status_code = __print_malformed_json_error(e)
    
    print('[Flask]: returned message:', returned_message, ', Status Code:',status_code)
    return returned_message, status_code




# functions to run in another thread as can take a while to run

def __add_partitions(N):
    '''
    Internal function to run in a separate thread so that large values of N 
    can be added to the DB and not crash the server
    '''
    # create partitions and add to DB
    print('[Partitions]: Starting to add {}...'.format(N))
    sqrt_N = int(int(N)**0.5) + 1 # int will always round down
    lower_bound = 1
    upper_bound = file_handler.partition_size
    partitions = []

    while lower_bound < sqrt_N - file_handler.partition_size:
        partitions.append((N, lower_bound, upper_bound))

        lower_bound += file_handler.partition_size
        upper_bound += file_handler.partition_size

        # submit the max number of partitions
        if file_handler.max_partition_submit <= len(partitions):
            print('[Partitions]: Submitting {} rows...'.format(file_handler.max_partition_submit))
            sql_connection.insert_partitions_into_table(partitions)
            partitions = []

    partitions.append((N, lower_bound, sqrt_N))

    # Add partitions to DB
    sql_connection.insert_partitions_into_table(partitions)
    print('[Partitions]: Partitions added')


def __kill_clients(N):
    '''
    Internal function used byu another thread too kill the clients that have 
    been working an a value N that has been solved
    '''
    print('[Killing Thread]: Stopping clients...')
    for row in sql_connection.get_ip_working_on_N(N):
        # some preprocessing to format the list to only have the IPs
        ip = row[0]
        print('[Killing Thread]: Stopping:', ip)

        response = None
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((ip, file_handler.client_port))
                s.sendall(b'stop')
                response = s.recv(100)

            if response != b'Ok':
                raise socket.timeout('')
            print('[Killing Thread]: {} stopped'.format(ip))

        except socket.timeout as e:
            print('[Killing Thread]: Error connecting with {}, removing from db'.format(ip))
            sql_connection.remove_ip_from_row(ip) 
    print('[Killing Thread]: Clients stopped')


def __print_malformed_json_error(exception):
    '''
    Basic internal function to print the malformed json error
    '''
    print(Fore.RED, '[Flask]: Error:')
    print(exception, Style.RESET_ALL) 
    returned_message = 'Malformed Json'
    status_code = 400
    return returned_message, status_code
