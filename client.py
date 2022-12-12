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
drift = random.randrange(95, 110) / 100
lock = threading.Lock()

# Sends messages with a 5% chance of failure
def send_message(message, destination):
    if random.randrange(0, 100) >= 5:
        sock.sendto(message.encode(), destination)
        print("Sent {} to {}".format(message, destination))
    else:
        print("Message {} to {} failed".format(message, destination))

# Thread that listens to local time requests from server
def respond_to_server():
    global local_time
    while True:
        data, address = sock.recvfrom(buffSize)
        print("MESSAGE RECEIVED FROM SERVER")
        if data.decode() == "TIME":
            send_message(str(local_time).encode(), address)
            print("--> Sent local time to server")
        else:
            local_time += float(data.decode())
            print("<-- Correction given by server: {}".format(data.decode()))

# Thread that updates the local time
def update_time():
    global local_time
    while True:
        local_time += drift
        time.sleep(1)

def print_time():
    while True:
        print("Current local time is: {}".format(local_time))
        time.sleep(5)

if __name__ == "__main__":
    # Join the system
    if sock.sendto("JOIN".encode(), ("83.255.206.155", 20001)):
        print("JOIN MESSAGE SENT")
    else:
        print("JOIN MESSAGE FAILED")
    # Start the threads
    threading.Thread(target=respond_to_server).start()
    threading.Thread(target=update_time).start()
    threading.Thread(target=print_time).start()