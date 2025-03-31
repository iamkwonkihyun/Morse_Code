import time
from functions.functions import receive_morse_code, total_people

while True:
    total_people()
    receive_morse_code()
    time.sleep(1)