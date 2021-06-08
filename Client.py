import socket
import threading
import sys
import argparse
import os

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('-l',
                       metavar='-l',
                       type=str,
                       help='listening port number')

parser.add_argument('-p',
                       metavar='-p',
                       type=str,
                       help='connect server port')

args = parser.parse_args()

#Wait for incoming data from server
#.decode is used to turn the message in bytes to a string

def download_file(s, file):
    filetodown = open(os.path.join(name, file), "wb")
    print("Receiving....")
    while True:
       data = s.recv(32)
       if data == b"DONE":
               print("Done Receiving.")
               break
       filetodown.write(data)
    filetodown.close()


def receive(socket, signal):
    while signal:
        try:
            data = socket.recv(32)
            if data.decode('utf-8').split(',')[0] == 'f':
                file = " ".join(data.decode('utf-8').split(',')[1:])
                download_file(socket, file)
                print('You: Enter an Option: ("m", "f", "x"):\n'
                      '(m)esage (send)\n'
                      '(f)ile (request)\n'
                      'e(x)it >> ')
            else:
                print(str(data.decode("utf-8")))
                print('You: Enter an Option: ("m", "f", "x"):\n'
                      '(m)esage (send)\n'
                      '(f)ile (request)\n'
                      'e(x)it >> ')

        except:
            print("You have been disconnected from the server")
            signal = False
            break



#Get host and port
host = 'localhost'
port = int(args.p)

name = input("CREATING NEW ID:\nEnter username: ")

if not os.path.exists(name):
    os.makedirs(name)

#Attempt connection to server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.send(str.encode(name))

except:
    print("Could not make a connection to the server")
    input("Press enter to quit")
    sys.exit(0)

#Create new thread to wait for data
receiveThread = threading.Thread(target = receive, args = (sock, True))
receiveThread.start()

print('You: Enter an Option: ("m", "f", "x"):\n'
      '(m)esage (send)\n'
      '(f)ile (request)\n'
      'e(x)it >> ')

#Send data to server
#str.encode is used to turn the string message into bytes so it can be sent across the network
while True:
    selection = input()

    if selection == 'm':
        msg = 'm,'
        message = input('Enter Your Message >> ')
        sock.sendall(str.encode(msg+message))
        # s.send(str.encode(msg + msg_input))
    elif selection == 'f':
        msg = 'f,'
        owner = input('Who Owns the file? >> ')
        file = input('Which file you need? >> ')
        sock.sendall(str.encode(msg + owner + ',' + file))

    elif selection == 'x':
        print('Closing Your Socket!... Goodbye!')
        sock.sendall(b'tata')
        break

sys.exit(0)

