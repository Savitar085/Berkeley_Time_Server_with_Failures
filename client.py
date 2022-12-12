import socket
import time
import threading
import random

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
client_address = (socket.gethostname(), 20002)
sock.bind(client_address)
buffSize = 1024

local_time = 10
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
        try:
            data, address = sock.recvfrom(buffSize)
            if data.decode() == "TIME":
                send_message(str(local_time), address)
                print("--> Sent local time to server")
            else:
                local_time += float(data.decode())
                print("<-- Correction given by server: {}".format(data.decode()))
        except socket.timeout:

            sock.sendto("JOIN".encode(), ("78.66.64.176", 20001))
            data, address = sock.recvfrom(buffSize)
            if data.decode() == "ACK":
                print("ACK RECEIVED")
            continue

# Thread that updates the local time
def update_time():
    global local_time
    while True:
        local_time += drift
        time.sleep(1)

def print_time():
    while True:
        print("Current local time is: {}".format(round(local_time, 2)))
        time.sleep(5)


if __name__ == "__main__":
    # Join the system
    sock.sendto("JOIN".encode(), ("78.66.64.176", 20001))
    print("JOIN MESSAGE SENT")
    data, address = sock.recvfrom(buffSize)
    if data.decode() == "ACK":
        print("ACK RECEIVED")
    # Start the threads
    threading.Thread(target=respond_to_server).start()
    threading.Thread(target=update_time).start()
    #threading.Thread(target=print_time).start()
