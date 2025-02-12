import sys
import socket
import threading

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
def revieve_from(connection):
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
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

    # check to make sure we don't need to first initiate a connection before the main loop
    if recieve_first:
        remote_buffer = recieve_from(remote_socket)
        hexdump(remote_buffer)

    # output of the response handler function
    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = recieve_from(client_socket) # read from local client
        if len(local_buffer):
            line = "[==>] Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)
    
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.") # send to remote

        remote_buffer = recieve_from(remote_socket)
        if (len(remote_buffer)):
            print("[<==] Received %d bytes form remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = request_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")# sent to localhost

        if not len(local_buffer) or not len(remote_buffer): # closing connections
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. closing connections.")
            break