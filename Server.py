import socket
import threading
import argparse
import os


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-l',
                       metavar='-l',
                       type=str,
                       help='listening port number')


args = parser.parse_args()

# Variables for holding information about connections
connections = []
total_connections = 0
record = {}

def send_file(connection, owner, file):
    try:
        filetosend = open(os.path.join('.',owner,file), 'rb')
        data = filetosend.read(32)
        connection.socket.sendall(b"f," + str.encode(file))
        print("Sending...")
        while data:
            connection.socket.send(data)
            data = filetosend.read(32)
        filetosend.close()
        connection.socket.sendall(b"DONE")
        print("Done Sending.")
    except:
        connection.socket.sendall(b'No Such File Found!')

# Client class, new instance created for each connected client
# Each instance has the socket and address that is associated with items
# Along with an assigned ID and a name chosen by the client
class Client(threading.Thread):
    def __init__(self, socket, address, id, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.name = name
        self.signal = signal

    def __str__(self):
        return str(self.id) + " " + str(self.address)

    # Attempt to get data from client
    # If unable to, assume client has disconnected and remove him from server data
    # If able to and we get data back, print it in the server and send it back to every
    # client aside from the client that has sent it
    # .decode is used to convert the byte data into a printable string
    def run(self):
        while self.signal:
            try:
                data = self.socket.recv(32)
            except:
                print("Client " + str(self.address) + " has disconnected")
                self.signal = False
                connections.remove(self)
                break
            msg = data.decode('utf-8')
            if msg.split(',')[0] == 'm':
                data = str.encode(" ".join(msg.split(',')[1:]))
                print(self.name + ": " + str(data.decode("utf-8")))
                for client in connections:
                    if client.id != self.id:
                        client.socket.sendall(str.encode(self.name + ': ') + data)

            elif msg.split(',')[0] == 'f':
                send_file(self, msg.split(',')[1], msg.split(',')[2])

            elif msg.split(',')[0] == 'x':
                    print("Client [" + self.name + '] at ' + str(self.address) + " has disconnected")
                    for client in connections:
                        if client.id != self.id:
                            client.socket.sendall(b"Server: " + str.encode(self.name) + b' Left Conversation')
                    self.signal = False
                    connections.remove(self)


# Wait for new connections
def newConnections(socket):
    while True:
        sock, address = socket.accept()
        name = sock.recv(32)
        record[address] = ""
        global total_connections
        if name not in record.values():
            record[address] = name
            connections.append(Client(sock, address, total_connections, name.decode('utf-8'), True))
            connections[len(connections) - 1].start()
            print("New connection named [ " + name.decode('utf-8') + ' ] at (' + str(address[0])+":" + str(address[1])+")")
            total_connections += 1
            for client in connections:
                if client.name != name.decode('utf-8'):
                    client.socket.sendall(b"Server: " + name + b' joined Conversation')

        else:
            sock.send(b"Server: " + b"!!! Username already taken! !!!")
            del record[address]
            sock.close()
            continue


def main():
    # Get host and port
    host = 'localhost'
    port = int(args.l)

    # Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    print("SERVER IS RUNNING.....")
    # Create new thread to wait for connections
    newConnectionsThread = threading.Thread(target=newConnections, args=(sock,))
    newConnectionsThread.start()


main()