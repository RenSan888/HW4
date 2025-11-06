import socket
import argparse
from urllib.parse import urlparse
import threading
import os
import time

def http_get(url, output_file):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port if parsed_url.port else 80
    path = parsed_url.path if parsed_url.path else "/"

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            request = f"GET {path} HTTP/1.0\r\nHost: {host}\r\n\r\n"
            s.sendall(request.encode())

            response = b""
            while True:
                data = s.recv(4096)
                if not data:
                    break
                response += data

        header_end = response.find(b"\r\n\r\n")
        if header_end != -1:
            body = response[header_end + 4:]
        else:
            body = response

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "wb") as f:
            f.write(body)

        print(f"Downloaded {url} -> {output_file} ({len(body)} bytes)")
    except Exception as e:
        print(f"Failed {url}: {e}")


def download_concurrent(urls, output_dir, max_threads):
    threads = []
    for i, url in enumerate(urls):
        output_file = os.path.join(output_dir, f"file{i}_{os.path.basename(url)}")
        t = threading.Thread(target=http_get, args=(url, output_file))
        t.start()
        threads.append(t)
        if len(threads) >= max_threads:
            for th in threads:
                th.join()
            threads = []

    for th in threads:
        th.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concurrent HTTP Client")
    parser.add_argument("-urls", nargs='+', required=True, help="List of URLs to download")
    parser.add_argument("-o", required=True, help="Output directory")
    parser.add_argument("-c", type=int, default=5, help="Max concurrent downloads")
    args = parser.parse_args()

    start_time = time.time()
    download_concurrent(args.urls, args.o, args.c)
    end_time = time.time()

    print(f"Elapsed time: {end_time - start_time:.2f} seconds")
