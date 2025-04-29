import socket
import pickle
import os
import random
import time

SOCKETPATH = "/tmp/telemSocket"

# Remove existing socket file if it exists
if os.path.exists(SOCKETPATH):
    os.remove(SOCKETPATH)

# Create a Unix socket and listen
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKETPATH)
server.listen(1)

print("Server is waiting for connection...")
sock, _ = server.accept()
print("Client connected.")

while True:
    # Randomize socket data
    values = [random.uniform(0.0, 100.0) for i in range(15)]

    # send data
    data = pickle.dumps(values)
    sock.sendall(data)

    time.sleep(0.5)