import sys
import socket
import threading
import time

# HEXFILTER string, contains ASCII printable chars (0-255) and (.) if not
HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

# hexdump function that takes some input as bytes of strings and prints to console
def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()#convert to printable string 

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])

        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexawidth = length*3
        results.append(f'{i:04x} {hexa:<{hexawidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results

# for recieveing both local and remote data
def recieve_from(connection):
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(16384)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer

# modifying the request
def request_handler(buffer):
    # perform packet modificatons
    return buffer

# modifying response
def response_handler(buffer):
    # perform packer modifications
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, recieve_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port)) # connect to remote host

    remote_buffer = b""
    # check to make sure we don't need to first initiate a connection before the main loop
    if recieve_first:
        remote_buffer = recieve_from(remote_socket)
        hexdump(remote_buffer)

    # output of the response handler function
    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    idle_counter = 0
    while True:
        local_buffer = recieve_from(client_socket) # read from local client
        if len(local_buffer):
            line = "[==>] Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)
    
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.") # send to remote
            idle_counter = 0

        remote_buffer = recieve_from(remote_socket)
        if (len(remote_buffer)):
            print("[<==] Received %d bytes form remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = request_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")# sent to localhost
            idle_counter = 0

        if not len(local_buffer) and not len(remote_buffer): # closing connections if both sides return on data
            idle_counter += 1
            time.sleep(5)
            if idle_counter > 50:
                client_socket.close()
                remote_socket.close()
                print("[*] Connection idle. closing connections.")
                break

# function to setup and manage the connection
def server_loop(local_host, local_port, remote_host, remote_port, recieve_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem on bind: %r' %e)

        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # print out the local connnection information
        line = "> Recieved incoming connnection from %s:%d" % (addr[0], addr[1])
        print(line)
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, recieve_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [recieve_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    recieve_first = sys.argv[5]

    if "True" in recieve_first:
        recieve_first = True
    else:
        recieve_first = False

    server_loop(local_host, local_port, remote_host, remote_port, recieve_first)

if __name__ == "__main__":
    main()