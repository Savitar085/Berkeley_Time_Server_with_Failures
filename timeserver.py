# Description: A simple timeserver that returns the current time in seconds since the epoch
import socket
import time
import threading
import random
import node

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = (socket.gethostname, 20001)
sock.bind(server_address)
buffSize = 1024
# List of clients as node-objects
client_list = []


# Sends messages with a 5% chance of failure
def send_message(message, destination):
    if random.randrange(0, 100) >= 5:
        sock.sendto(message.encode(), destination)
        print("Sent {} to {}".format(message, destination))
    else:
        print("Message {} to {} failed".format(message, destination))


# Thread that sends local time requests to clients
def request_time():
    while True:
        if num_clients_to_respond() > 0:
            for client in client_list:
                send_message("TIME", client)
                client.expects_answer = 1
            receive_responses()
            time.sleep(5)


# Function that receives local time responses from clients and calculates the average time to send to the clients,
# if client message is not received within 5 seconds, it is removed from the client list
def receive_responses():
    start_time = time.time()
    response_recv = 0
    while True:
        data, address = sock.recvfrom(buffSize)
        if data.decode() == "JOIN":
            print("New client joined with address {}".format(address))
            add_client(address)
        else:
            for client in client_list:
                if client.address == address:
                    response_recv += 1
                    client.time = float(data.decode())
                    # If all clients respond in time
                    if response_recv == len(client_list):
                        response_recv = 0
                        calculate_average_time()
                    # If time has passed and not all clients have responded
                    elif time.time() - start_time == 5:
                        calculate_average_time()
                        response_recv = 0


# Calculates the average time and sends corrections to the clients
def calculate_average_time():
    average_time = 0
    for client in client_list:
        if client.expects_answer == 1:
            average_time += client.time
    average_time /= num_clients_to_respond()
    for client in client_list:
        if client.expects_answer == 1:
            send_message(str(average_time - client.time), client.address)
            client.expects_answer = 0


def num_clients_to_respond():
    num_clients = 0
    for client in client_list:
        if client.expects_answer == 1:
            num_clients += 1
    return num_clients


# Function that adds new clients to the client list
def add_client(address):
    client_list.append(node.Node(address))
    print("Added {} to client list".format(address))


if __name__ == "__main__":
    threading.Thread(target=request_time).start()

