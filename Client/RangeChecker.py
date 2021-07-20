import os
import time
import requests
import json
import math
import tqdm
from colorama import Fore, Style
import ClientFileHandler


class RangeChecker:
    '''
    Class to handle to functionality of testing if a value in the range given is a factor of N
    '''


    def __init__(self):
        '''
        Initialize the object with the variable _running as true.
        As long as this stays on true, this thread will keep on looping to keep testing ranges
        '''
        self._running = True
        file_handler = ClientFileHandler.ClientFileHandler()

        # static variables
        self.connect_url = 'http://' + file_handler.master_ip + ':' + str(file_handler.master_port) + '/connect'
        self.solution_url = 'http://' + file_handler.master_ip + ':' + str(file_handler.master_port) + '/solution'
        self.saved_solution_filename = 'saved_solution.json'


    def terminate(self):
        '''
        Set the _running parameter to False indicating to kill this thread 
        '''
        self._running = False


    def run(self):
        '''
        Main body of the thread, will keep the tread live unless told to terminate
        '''
        print('[Thread]: Thread Started')
        while self._running:
            solution_json = None
            try:
                # # check there is a saved solution
                self.__check_for_saved_solution()
                                
                # get new N and range
                print('[Thread]: Requesting new range')
                response = requests.get(self.connect_url)
                if response.status_code == 200:
                    # Get json parameters from response
                    json_object = response.json()
                    N = int(json_object['N'])
                    lower_limit = int(json_object['Lower_Limit'])
                    upper_limit = int(json_object['Upper_Limit'])
                    print('[Thread]: Response received: ')
                    print('[Thread]:', json_object)

                    # Start process for factoring
                    solution = self.__check_range(N, lower_limit, upper_limit)
                    
                    # to to see if loop has been terminated before sending response
                    if self._running:
                        # Send response
                        solution_json = {
                            'N': str(N),
                            'Lower_Limit': str(lower_limit),
                            'Upper_Limit': str(upper_limit),
                            'solution': str(solution)
                        }
                        # if the server goes down when sending the response it will save
                        # this repose ready to be sent back when the server is back up
                        requests.post(self.solution_url, json=solution_json)
                        print('[Thread]: Search completed, response sent:')
                        print('[Thread]:', solution_json)

                        # sleep for 5 seconds to wait for the server to update
                        time.sleep(5)
                else:
                    raise requests.ConnectionError(response.text)

            except requests.ConnectionError as e:
                # save the solution ready to be sent out again if restarted
                if solution_json != None:
                    print('[Thread]: Soultion could not be sent to sever, saving solution')
                    with open(self.saved_solution_filename, 'w') as file:
                        json.dump(solution_json, file)
                print(Fore.RED, '[Thread]: Error:')
                print(e, Style.RESET_ALL)
                print('[Thread]: Could not successfully connect to server, waiting 5 minutes to retry')

                # Sleep for 5 mins before trying again
                time.sleep(300)

        time.sleep(5)
        print('[Thread]: Thread terminated')


    def __check_for_saved_solution(self):
        '''
        internal function to check if a saved solution file exists.
        If so then send that saved solution to the client
        '''
        if os.path.exists(self.saved_solution_filename):
            print('[Thread]: Saved solution found, resending to server')
            saved_json = json.load(open(self.saved_solution_filename))
            # resend the json, will raise exception to restart loop if cannot be sent
            print('[Thread]: Saved solution sent: ')
            print('[Thread]:', saved_json)
            requests.post(self.solution_url, json=saved_json)
            # delete file
            os.remove(self.saved_solution_filename) 
            # some time to help wait for the DB to update
            time.sleep(5)


    def __check_range(self, N, lower_limit, upper_limit):
        '''
        Method for looping thorugh the number range given to find a factor for N
        '''
        # Set up progress bar
        numb_of_checks = 2 * math.floor(((upper_limit + 1) - (lower_limit - 1))/6)
        progress_bar = tqdm.tqdm(total=numb_of_checks)
        # in the progress bar the total number represents the number of values +- a multiple of 6

        remainder = upper_limit % 6
        k = -1
        multiple = (upper_limit - remainder) - (6 * k)
        solution = 0

        # loop through range for a solution
        while lower_limit <= multiple:
            # Initial check to see if the process has been terminated
            if not self._running:
                break

            # Checking for factors
            check1 = multiple + 1
            if N % check1 == 0:
                solution = check1
                break
            progress_bar.update(1)

            check2 = multiple - 1
            if N % check2 == 0:
                solution = check2
                break
            progress_bar.update(1)

            k += 1
            multiple = (upper_limit - remainder) - (6 * k)
        
        progress_bar.close()
        # Will return 0 is no factors are found
        return solution