#include <iostream>
#include <string>

#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>

#include "HTTP_Handler.cpp"

using std::string;
using std::cerr;

int main() {
    std::cout << "Opening Server on localhost port 8080...\n";

    int server_len, BUFFER_SIZE = 30720;
    struct sockaddr_in server;
    WSADATA wsaData;
    SOCKET server_socket, client_socket;
    HTTP_Handler http_handler = HTTP_Handler();

    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
        cerr << "Unable to initialize the server\n\n";

    server_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (server_socket == INVALID_SOCKET)
        cerr << "Unable to create the server socket\n\n";

    server.sin_family = AF_INET;
    server.sin_addr.s_addr = inet_addr("127.0.0.1");
    server.sin_port = htons(8080);
    server_len = sizeof(server);

    if (bind(server_socket, (SOCKADDR*)&server, server_len) != 0)
        cerr << "Unable to bind server to localhost port 8080\n\n";

    if (listen(server_socket, 20) != 0)
        cerr << "Unable to begin listening to the port\n\n";

    std::cout << "Listening on localhost port 8080...\n\n";

    int bytes = 0;
    string request, response, header;

    while(true) {
        client_socket = accept(server_socket, (SOCKADDR*)&server, &server_len);
        if(client_socket == INVALID_SOCKET) {
            cerr << "Unable to create the client socket\n\n";
            continue;
        }

        char buffer[30720] = {};
        bytes = recv(client_socket, buffer, BUFFER_SIZE, 0);
        if (bytes <= 0) {
            cerr << "Unable to read client request\n\n";
            continue;
        }
        
        request = string(buffer);

        cerr << "Request: " << request << "\n\n\n";

        header = request.substr(0, request.find("\r\n"));
        response = http_handler.handleRequest(request);

        cerr << "Response: " << response << "\n\n\n";

        int bytes_sent = 0; 
        unsigned int total_bytes = 0;
        while (total_bytes < response.size()) {
            bytes_sent = send(client_socket, response.c_str(), response.size(), 0);
            if (bytes_sent < 0)
                cerr << "Unable to send the server response\n\n";
            else
                total_bytes += bytes_sent;
        }
        
        closesocket(client_socket);
    }

    closesocket(server_socket);
    WSACleanup();
    
    return 1;
}