import tkinter as tk
from tkinter import filedialog, END
from threading import Thread
from functools import partial

import socket
import select
import errno
import sys

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
my_username = input("Username: ")

fname = ''
HEIGHT = 600
WIDTH = 550


#-----------------------------Client Code------------------------------



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)

# Prepare username and header and send them
# We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)


def sendMessage(message):
    msg = str(message.get("1.0", 'end-1c'))
    message.delete(1.0, END)
    try:
        if message :
            msg = msg.encode('utf-8')
            message_header = f"{len(msg):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + msg)
            messageLog.insert(END, "Me: " + msg.decode('utf-8')+'\n')
    except Exception as e:
        print(e)


def receive_message():
    while True:
        try:
            # Now we want to loop over received messages (there might be more than one) and print them
            while True:

                # Receive our "header" containing username length, it's size is defined and constant
                username_header = client_socket.recv(HEADER_LENGTH)

                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                # Convert header to int value
                username_length = int(username_header.decode('utf-8').strip())

                # Receive and decode username
                username = client_socket.recv(username_length).decode('utf-8')

                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                # Print message
                print(f'{username} > {message}')
                messageLog.insert(END, f'{username}: {message}\n')
        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print(e)
                sys.exit()

            # We just did not receive anything
            continue

        except Exception as e:
            # Any other exception - something happened, exit
            print('Reading error: '.format(str(e)))
            sys.exit()


#-----------------------------Gui Code------------------------------

    
root = tk.Tk()
root.title("Chainage Avant")
saturer = tk.IntVar()

canvas = tk.Canvas(root, height = HEIGHT, width = WIDTH)
canvas.pack()

frame = tk.Frame(root, bg = '#f0f0f0')
frame.place(relwidth = 1, relheight = 1)
frame.filename = ''

message = tk.Text()
message.place(relx = 0.2, rely = 0.75, width = 300, height = 30)

        
button = tk.Button(frame, text = "Send", command = partial(sendMessage, message))
button.place(relx = 0.8, rely = 0.75, width = 80, height = 30)

messageLog = tk.Text()
messageLog.place(relx = 0.2, rely = 0.1, width = 350, height = 100)



receive_thread = Thread(target = receive_message)
receive_thread.start()

root.mainloop() #Start gui