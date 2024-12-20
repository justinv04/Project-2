#include <iostream>
#include <string>
#include <vector>

#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>

#include "HTTP_Handler.cpp"

using std::string;
using std::cerr;
using std::vector;

int main() {
    std::cout << "Opening Server on localhost port 8080...\n";

    int server_len, BUFFER_SIZE = 30720;
    struct sockaddr_in server;
    WSADATA wsaData;
    SOCKET server_socket;
    vector<SOCKET> client_sockets = {};

    vector<string> messages = {};
    HTTP_Handler http_handler = HTTP_Handler();

    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
        cerr << "Unable to initialize the server\n\n";

    server_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (server_socket == INVALID_SOCKET)
        cerr << "Unable to create the server socket\n\n";

    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY; // allow connection from all computers on the local network
    server.sin_port = htons(8080);  // ensure your firewall is disabled for this port
    server_len = sizeof(server);

    if (bind(server_socket, (SOCKADDR*)&server, server_len) != 0)
        cerr << "Unable to bind server to localhost port 8080\n\n";

    if (listen(server_socket, 20) != 0)
        cerr << "Unable to begin listening to the port\n\n";

    std::cout << "Listening on localhost port 8080...\n\n";

    fd_set readfds;
    char buffer[30720];

    while (true) {
        FD_ZERO(&readfds);

        // add the server socket to the set
        FD_SET(server_socket, &readfds);
        SOCKET max_socket = server_socket;

        // add all client sockets to the set
        for (SOCKET client_socket : client_sockets) {
            FD_SET(client_socket, &readfds);

            if (client_socket > max_socket)
                max_socket = client_socket;
        }

        // wait for activity on any socket
        int activity = select(max_socket + 1, &readfds, NULL, NULL, NULL);
        if (activity < 0) {
            cerr << "Error during select\n\n";
            continue;
        }

        // check for new connections on the server socket
        if (FD_ISSET(server_socket, &readfds)) {
            SOCKET client_socket = accept(server_socket, (SOCKADDR*)&server, &server_len);

            if (client_socket == INVALID_SOCKET)
                cerr << "Unable to create the client socket\n\n";
            else { // new valid socket
                client_sockets.push_back(client_socket);

                string welcome_response = HTTP_Handler::makeResponse(200, "application/json", "{\"user\": \"Server\", \"message\": \"Connection Established\"}");

                for (SOCKET curr_client_socket : client_sockets) {
                    if (curr_client_socket != client_socket) {  // Avoid sending to the sender
                        int bytes_sent = 0, total_bytes = 0;
                        
                        while (total_bytes < welcome_response.size()) {
                            bytes_sent = send(curr_client_socket, welcome_response.c_str() + total_bytes, welcome_response.size() - total_bytes, 0);
                            if (bytes_sent < 0) {
                                cerr << "Unable to send the server response\n\n";
                                break;
                            }
                            total_bytes += bytes_sent;
                        }
                    }
                }
            }
        }

        // check each client socket for incoming data
        for (size_t i = 0; i < client_sockets.size(); ++i) {
            SOCKET client_socket = client_sockets[i];

            if (FD_ISSET(client_socket, &readfds)) {
                memset(buffer, 0, BUFFER_SIZE);
                int bytes = recv(client_socket, buffer, BUFFER_SIZE, 0);

                if (bytes <= 0) {
                    if (bytes == 0) 
                        continue;
                    else {
                        cerr << "Client disconnected or error occurred.\n\n";
                        closesocket(client_socket);
                        client_sockets.erase(client_sockets.begin() + i);
                        --i;
                        continue;
                    }
                }

                string request(buffer);
                cerr << "Request:\n" << request << "\n\n";

                string response = http_handler.handleRequest(request);
                cerr << "Response:\n" << response << "\n\n---------------------------------------------------------\n\n";

                // Send the response to all connected clients
                for (SOCKET curr_client_socket : client_sockets) {
                    if (curr_client_socket != client_socket) {  // Avoid sending to the sender
                        int bytes_sent = 0, total_bytes = 0;
                        
                        while (total_bytes < response.size()) {
                            bytes_sent = send(curr_client_socket, response.c_str() + total_bytes, response.size() - total_bytes, 0);
                            if (bytes_sent < 0) {
                                cerr << "Unable to send the server response\n\n";
                                break;
                            }
                            total_bytes += bytes_sent;
                        }
                    }
                }
            }
        }
    }

    closesocket(server_socket);
    WSACleanup();
    
    return 1;
}