#!/bin/bash

echo 'Updating...'
sudo apt update
sudo apt -y upgrade
sudo apt -y autoremove

echo 'Installing Python 3...'
sudo apt install python3
sudo apt install python3-pip

echo 'Installing SQL Lite...'
sudo apt install sqlite3

echo 'Installing Python modules'
sudo pip3 install colorama
sudo pip3 install flask
sudo pip3 install requests
sudo pip3 install tqdm
