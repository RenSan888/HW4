# Members
Oscar Hernandez Lesage

Renatha Sanchez

# Questions

1. What is your strategy for identifying unique clients?
-------------------------------------------------------
In the server, a client is identified using their IP address. Each incoming connection’s IP address is used as a key in a dictionary to track the number of concurrent connections from that client. This allows the server to enforce a per-client connection limit, regardless of the client’s application or port.

2. How do you prevent the clients from opening more connections once they have opened the maximum number of connections?
------------------------------------------------------------------------------------------------------------------------
Before accepting a client request, the server checks the client’s current connection count in the dictionary. If the client has already reached the maximum allowed connections (`-maxclient`), the server immediately sends an HTTP 429 response:
    HTTP/1.1 429 Too Many Requests
and closes the connection. This prevents the client from exceeding its allowed concurrent connections.  
The same strategy is used for the total server-wide connections limit (`-maxtotal`), returning HTTP 503 if exceeded.

3. Report the times and speedup for concurrent fetch of the URLs in testcase 1 and 2 with the stock HTTP server
----------------------------------------------------------------------------------------------------------------
*Testcase 1:*
- Sequential fetch time: 0.01 seconds
- Concurrent fetch time (10 connections): 0.01 seconds
- Speedup = 1.0

*Testcase 2:*
- Sequential fetch time: 0.01 seconds
- Concurrent fetch time (10 connections): 0.01 seconds
- Speedup = 1.0

Explanation: The test files used are very small (14 bytes each). With such small files, the stock HTTP server completes requests almost instantly, so concurrent fetching does not provide a noticeable speedup.

4. Report the times and speedup for concurrent fetch of the URLs in testcase 1 and 2 with your http_server_conc. Are these numbers same as above? Why or why not?
---------------------------------------------------------------------------------------------------------------------------------
*Testcase 1 (http_server_conc):*
- Sequential fetch time: 0.01 seconds
- Concurrent fetch time (10 connections): 0.01 seconds
- Speedup = 1.0

*Testcase 2 (http_server_conc):*
- Sequential fetch time: 0.01 seconds
- Concurrent fetch time (10 connections): 0.01 seconds
- Speedup = 1.0

Explanation: The results are the same as the stock HTTP server because the test files are very small. The overhead of threads and network operations is larger than the time it takes to serve these tiny files. With larger files or more URLs, the concurrent server would demonstrate clear speedup compared to sequential fetching.

# How to run
On server

    python http_server_conc.py -p 20001 -maxclient 12 -maxtotal 60
    

On client

    python http_client_concurrent.py -urls http://localhost:20001/file1.txt http://localhost:20001/file2.txt -o downloads -c 10
    

Test sequential vs concurrent download (Speedup)

    python http_client_concurrent.py -urls http://localhost:20001/file1.txt http://localhost:20001/file2.txt -o downloads_seq -c 1

  &

    python http_client_concurrent.py -urls http://localhost:20001/file1.txt http://localhost:20001/file2.txt -o downloads_conc -c 10

  &

    python http_client_concurrent.py -urls http://localhost:20001/testfiles1/file1.txt http://localhost:20001/testfiles1/file2.txt ... -o downloads_conc -c 10

