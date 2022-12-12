# Berkeley_Time_Server_with_Failures
# Berkeley Time Server with at least 5 nodes on different machines.
# The server should be able to handle failures of any node.

import sys
import time
import random
import socket
import threading
import traceback

import socket
import time
import threading
import random

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
client_address = (socket.gethostname(), 20001)
sock.bind(client_address)
buffSize = 1024

local_time = 15
drift = random.randrange(90, 110) / 100
lock = threading.Lock()

# Sends messages with a 5% chance of failure
def send_message(message, destination):
    if random.randrange(0, 100) >= 5:
        sock.sendto(message.encode(), destination)
        print("Sent {} to {}".format(message, destination))
        #Drift
    else:
        print("Message {} to {} failed".format(message, destination))
        drift = 0

# Thread that listens to local time requests from server
def respond_to_server():
    global local_time
    while True:
        data, address = sock.recvfrom(buffSize)
        if data.decode() == "TIME":
            send_message(str(local_time).encode(), address)

# Thread that receives responses from the server and corrects the local time
def receive_time():
    global local_time
    while True:
        data, address = sock.recvfrom(buffSize)
        if data.decode() != "TIME":
            local_time = float(data.decode())

# Thread that updates the local time
def update_time():
    global local_time
    while True:
        local_time += drift
        time.sleep(1)

def print_time():
    while True:
        print(local_time)
        time.sleep(5)

if __name__ == "__main__":
    # Start the threads
    threading.Thread(target=respond_to_server).start()
    threading.Thread(target=receive_time).start()
    threading.Thread(target=update_time).start()
    threading.Thread(target=print_time).start()