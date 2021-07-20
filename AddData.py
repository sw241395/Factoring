import random
import requests

primes = [7625597485003, 7666466646667, 7762868682677, 7777774777777,
          7777775552353, 7929188600987, 8212668876301, 8284590452353,
          8313667333393, 8401414020133, 9095665192937, 9203225223029, 
          9740985827329, 9876543244501, 9977770001777, 9999919199999,
          9999991111111, 9999999998987, 13791315212531, 14014014014159,
          14444999999999, 15154262241479, 15261281789861, 15275163131153,
          15307263442931, 15423094826093, 16000611609061, 13857000000001,
          13645500000001]


ipv4 = input("Enter the IP of the master server: ")

p = random.choice(primes)
q = random.choice(primes)
N = p * q

print('Adding N={} to DB'.format(N))

server_url = 'http://{}:5000/add'.format(ipv4)
json_content = {'N': str(N)}
requests.post(server_url, json=json_content)

print('Added')
