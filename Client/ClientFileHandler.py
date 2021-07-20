import json
import requests

class ClientFileHandler:
    '''
    A basic class to handle importing the configs from the config.json.
    Also too handle all other parts when relating too files.
    '''


    def __init__(self):
        '''
        When the class is initialized, get all the configs from the json
        '''
        # Open the config file
        with open('ClientConfig.json', 'r') as json_file:
            json_content = json_file.read()
        json_object = json.loads(json_content)

        # Master network configs
        self.master_ip = json_object['master']['network']['ipv4']
        self.master_port = json_object['master']['network']['port']

        # Client network configs
        self.client_ip = json_object['client']['network']['ipv4']
        self.client_port = json_object['client']['network']['port']

        # Get external IP if no ip is given
        if self.client_ip == 0:
            self.client_ip = requests.get('https://api.ipify.org').text

        

    