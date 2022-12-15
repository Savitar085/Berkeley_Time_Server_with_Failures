import socket
import time
import threading
import random
import node

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (socket.gethostname(), 20001)
sock.bind(server_address)
buffSize = 1024


#Globala
client_list = [('212.85.93.80', 20005),
               ('78.66.64.176',20006)]





# Sends messages with a 5% chance of failure
def send_message(message, destination):
    if random.randrange(0, 100) >= 5:
        sock.sendto(message.encode(), destination)
        print("Sent {} to {}".format(message, destination))
    else:
        print("Message {} to {} failed".format(message, destination))

if __name__ == "__main__":
    print("Server running...")