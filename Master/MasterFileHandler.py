import json


class MasterFileHandler:
    '''
    A basic class to handle importing the configs from the config.json.
    Also too handle all other parts when relating too files.
    '''


    def __init__(self):
        '''
        When the class is initialized, get all the configs from the json
        '''
        # Open the config file
        with open('MasterConfig.json', 'r') as json_file:
            json_content = json_file.read()
        json_object = json.loads(json_content)
        
        # SQL configs
        self.db_name = json_object['master']['sql']['db']
        self.table_name = json_object['master']['sql']['table_name']

        # Master network configs
        self.master_ip = json_object['master']['network']['ipv4']
        self.master_port = json_object['master']['network']['port']
        
        # Master parameters
        self.partition_size = json_object['master']['parameters']['partition_size']
        self.max_partition_submit = json_object['master']['parameters']['max_partition_submit']
        self.solutions_file_path = json_object['master']['parameters']['solutions_file_path']

        # Client network configs
        self.client_port = json_object['client']['network']['port']
    

    def update_solution_file(self, N, solution):
        '''
        Update the solutions file to store factors for a Int
        '''
        solutions_file = open(self.solutions_file_path, "a")
        solutions_file.write("N = " + N + '\n')
        solutions_file.write("p = " + solution + '\n')
        solutions_file.write("q = " + str(int(int(N)/int(solution))) + '\n')
        solutions_file.write("\n")
        solutions_file.close
        print('[Flask]: Value {} has a factor of {}'.format(N, solution))
    