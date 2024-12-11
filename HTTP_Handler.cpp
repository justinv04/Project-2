
#include <string>
#include <iostream>
#include <sstream>
#include <utility>
#include <map>
#include <vector>

using std::string;
using std::vector;
using std::pair;
using std::map;

static const string SERVER_URL = "http://127.0.0.1:8080";

static const string RESPONSE_404 =
    "HTTP/1.1 404 Not Found\r\n"
    "Content-Type: text/plain\r\n"
    "Content-Length: 13\r\n\r\n"
    "404 Not Found";

static const string RESPONSE_401 =
    "HTTP/1.1 401 Unauthorized\r\n"
    "Content-Type: text/plain\r\n"
    "Content-Length: 22\r\n\r\n"
    "User Not Unauthorized";

enum class REQUEST_TYPE {
    CON,            // CONNECT - Establish a network connection to a resource
    DEL,            // DELETE - Delete a resource
    GET,            // GET - Request a resource
    HED,            // HEAD - Request headers for a resource (no body)
    POS,            // POST - Submit data to be processed
    PUT,            // PUT - Replace a resource or create it if it doesn't exist
    PAT,            // PATCH - Apply partial modifications to a resource
    OPT,            // OPTION - Request communication options available for a resource
    TRC,            // TRACE - Echo back the received request (used for debugging)
    UNK             // Unable to establish type
};

static map<int, string> STATUS_CODE_MAP = {
    {200, "OK"},
    {201, "Created"},
    {202, "Accepted"},
    {204, "No Content"},

    {400, "Bad Request"},
    {401, "Unauthorized"},
    {403, "Forbidden"},
    {404, "Not Found"}
};

class HTTP_Handler {
    using enum REQUEST_TYPE;
    
    private:

        REQUEST_TYPE getRequestType(const string request_type_str) {
            switch(request_type_str[0]) {
                case 'C':           return CON;
                case 'D':           return DEL;
                case 'G':           return GET;
                case 'H':           return HED;
                case 'O':           return OPT;
                case 'T':           return TRC;
                case 'P': {
                    switch(request_type_str[1]) {
                        case 'A':   return PAT;
                        case 'O':   return POS;
                        case 'U':   return PUT;
                        default: {}
                }}
                default: return UNK;
            }
        };

        string handleGetRequest(const string endpoint, const string data_str, const string client_url) {
            int status;
            string content_type, content;

            // DO SOMETHING

            status = 200, content_type = "application/json";
            return makeResponse(status, client_url, content_type, content);
        };

        string handlePostRequest(const string endpoint, const string data_str, const string client_url) {
            int status;
            string content_type, content;

            // DO SOMETHING

            status = 200;
            content_type = "text/plain";
            return makeResponse(status, client_url, content_type, content);
        };

        static void parseRequestElements(const string &request, string &type, string &endpoint, string &data, string &client_url) {
            size_t index = 0;

            while(request[index] != ' ') 
                type += request[index++];

            index += 2;

            while(request[index] != ' ')
                endpoint += request[index++];

            while(request[index] != '\r')

            index = request.find("\r\n\r\n") + 4;
            data = request.substr(index, request.length() - index);
        }

        static string makeOptionsAppendix (const string client_url) {
            string response = "Access-Control-Allow-Origin: " + client_url + "\r\n";
            response += "Access-Control-Allow-Methods: POST, GET, OPTIONS\r\n";
            response += "Access-Control-Allow-Headers: Content-Type\r\n";
            response += "Access-Control-Max-Age: 3600\r\n";
            return response;
        }

    public: 

        string handleRequest(const string request) {

            std::cout << request << "\n\n";

            string type_str, endpoint_str, data_str, client_url;
            parseRequestElements(request, type_str, endpoint_str, data_str, client_url);

            REQUEST_TYPE request_type = getRequestType(type_str);

            string content;
            switch(request_type) {
                case GET: {
                    content = handleGetRequest(endpoint_str, data_str, client_url);
                    break;
                }
                case POS: {
                    content = handlePostRequest(endpoint_str, data_str, client_url);
                    break;
                }
                case OPT: {
                    content = makeResponse(204, client_url);
                    break;
                }
                default: content = RESPONSE_404;
            }
            return content;
        };

        static string makeResponse(const int status,  const string client_url, const string content_type = "", const string content = "") {
            string response = "HTTP/1.1 " + std::to_string(status) + " " + STATUS_CODE_MAP[status] + "\r\n";
                
            if(status != 204)
                response += ("Content-Type: " + content_type + "\r\n");
            
            response += makeOptionsAppendix(client_url);
            response += ("Content-Length: " + std::to_string(content.length()) + "\r\nConnection: keep-alive\r\n\r\n" + content);

            return response;
        };
};