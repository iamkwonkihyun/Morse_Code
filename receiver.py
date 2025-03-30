import time
from functions.functions import receive_thread

while True:
    receive_thread()
    time.sleep(1)