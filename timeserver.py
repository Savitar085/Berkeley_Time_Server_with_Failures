# Description: A simple timeserver that returns the current time in seconds since the epoch
import socket
import time
import threading
import random
import node

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = (socket.gethostname(), 20001)
sock.bind(server_address)
buffSize = 1024
# List of clients as node-objects
client_list = []
average_global = 0


# Sends messages with a 5% chance of failure
def send_message(message, destination):
    if random.randrange(0, 100) >= 5:
        sock.sendto(message.encode(), destination)
    else:
        print("\nMessage {} to {} failed\n".format(message, destination))


# Thread that sends local time requests to clients
def request_time():
    while True:
        if len(client_list) > 0:
            for client in client_list:
                send_message("TIME", client.address)
        time.sleep(2)


# Thread that receives local time responses from clients and calculates the average time to send to the clients,
# if client message is not received within 5 seconds, it is removed from the client list.format()
def receive_responses():
    response_recv = 0
    while True:
        start_time = time.time()
        data, address = sock.recvfrom(buffSize)
        if data.decode() == "JOIN":
            print("New client joined with address {}".format(address))
            add_client(address)
        else:
            for client in client_list:
                if client.address == address:
                    response_recv += 1
                    client.time = float(data.decode())
                    client.expects_answer = 1
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
    global average_global
    average_time = 0
    for client in client_list:
        if client.expects_answer == 1:
            average_time += client.time
    if num_clients_to_respond() > 0:
        average_time /= num_clients_to_respond()
        average_global = average_time
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
    if not client_exists(address):
        client_list.append(node.Node(address))
        send_message("ACK", address)
        print("Added {} to client list\n".format(address))
    else:
        send_message("ACK", address)
        print("{} is back\n".format(address))


def client_exists(address):
    for client in client_list:
        if client.address == address:
            return True
    return False


def print_local_times():
    time.sleep(7)
    while True:
        if len(client_list) > 0:
            print("Client times:")
            for client in client_list:
                if client.oldTime != client.time:
                    print(f"{round(client.time, 2)} for client with address {client.address}")
                    client.oldTime = client.time
                    client.disc = 0
                elif client.disc >= 3:
                    client_list.remove(client)
                    print(f"Client with address {client.address} removed")
                else:
                    print(f"{round(client.time, 2)} for client with address {client.address} seems disconnected")
                    client.disc += 1
        time.sleep(7)


if __name__ == "__main__":
    print("Server running...")
    threading.Thread(target=request_time).start()
    threading.Thread(target=receive_responses).start()
    threading.Thread(target=print_local_times).start()


