import os

import requests

save_path = input("Please input avatar save path : ")
while not os.path.exists(save_path):
    save_path = input("Path not find. Re-put : ")

