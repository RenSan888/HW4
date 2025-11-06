import socket
import threading
import argparse
import os

# Track client connections
client_connections = {}  # client_id -> number of connections
total_connections = 0
lock = threading.Lock()


def get_client_id(client_socket):
    """
    Identify a client uniquely. We'll use IP + port tuple of the client socket as a simple approach.
    """
    return client_socket.getpeername()  # returns (ip, port) tuple


def handle_client(client_socket, maxclient):
    global total_connections
    client_id = get_client_id(client_socket)

    with lock:
        if client_id not in client_connections:
            client_connections[client_id] = 0

        if client_connections[client_id] >= maxclient:
            client_socket.sendall(
                b"HTTP/1.1 429 Too Many Requests\r\n\r\nToo many concurrent connections from this client.\n")
            client_socket.close()
            return

        client_connections[client_id] += 1

    try:
        request = client_socket.recv(4096).decode('utf-8')
        if not request:
            return

        # Parse requested file
        try:
            filename = request.split()[1][1:]  # remove leading '/'
            if filename == "":
                filename = "index.html"

            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    response_body = f.read()
                response_header = b"HTTP/1.1 200 OK\r\n\r\n"
            else:
                response_body = b"File not found"
                response_header = b"HTTP/1.1 404 Not Found\r\n\r\n"
        except Exception as e:
            response_body = f"Error: {e}".encode()
            response_header = b"HTTP/1.1 500 Internal Server Error\r\n\r\n"

        client_socket.sendall(response_header + response_body)
    finally:
        with lock:
            client_connections[client_id] -= 1
            if client_connections[client_id] == 0:
                del client_connections[client_id]
            total_connections -= 1
        client_socket.close()


def start_server(port, maxclient, maxtotal):
    global total_connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen(5)
    print(f"Server listening on port {port}")

    while True:
        client_socket, client_address = server_socket.accept()
        with lock:
            if total_connections >= maxtotal:
                client_socket.sendall(
                    b"HTTP/1.1 503 Service Unavailable\r\n\r\nServer busy. Try again later.\n")
                client_socket.close()
                continue
            total_connections += 1

        # Start a new thread for the client
        thread = threading.Thread(target=handle_client, args=(client_socket, maxclient))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concurrent HTTP Server")
    parser.add_argument("-p", type=int, required=True, help="Port to listen on")
    parser.add_argument("-maxclient", type=int, required=True, help="Maximum connections per client")
    parser.add_argument("-maxtotal", type=int, required=True, help="Maximum total connections")
    args = parser.parse_args()

    start_server(args.p, args.maxclient, args.maxtotal)
