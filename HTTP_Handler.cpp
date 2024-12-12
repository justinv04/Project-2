
#include <string>
#include <iostream>
#include <sstream>
#include <utility>
#include <vector>
#include <map>

using std::string;
using std::vector;
using std::pair;
using std::map;

static const string SERVER_URL = 
            "http://127.0.0.1:8080";

static const string OPTIONS_APPENDIX =
            "Access-Control-Allow-Origin: *\r\n"
            "Access-Control-Allow-Methods: POST, GET, OPTIONS\r\n"
            "Access-Control-Allow-Headers: Content-Type\r\n"
            "Access-Control-Max-Age: 3600\r\n";

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
    
    private:

        REQUEST_TYPE getRequestType(const string request_type_str) {
            switch(request_type_str[0]) {
                case 'C':           return REQUEST_TYPE::CON;
                case 'D':           return REQUEST_TYPE::DEL;
                case 'G':           return REQUEST_TYPE::GET;
                case 'H':           return REQUEST_TYPE::HED;
                case 'O':           return REQUEST_TYPE::OPT;
                case 'T':           return REQUEST_TYPE::TRC;
                case 'P': {
                    switch(request_type_str[1]) {
                        case 'A':   return REQUEST_TYPE::PAT;
                        case 'O':   return REQUEST_TYPE::POS;
                        case 'U':   return REQUEST_TYPE::PUT;
                        default: {}
                }}
                default: return REQUEST_TYPE::UNK;
            }
        };

    public: 

        string handleRequest(const string request) {
            string message_json = request.substr(request.find('{') - 1, request.find('}') + 1);
            return makeResponse(200, "application/json", message_json);
        };

        static string makeResponse(const int status, const string content_type = "", const string content = "") {
            string response = "HTTP/1.1 " + std::to_string(status) + " " + STATUS_CODE_MAP[status] + "\r\n";
                
            if(status != 204)
                response += ("Content-Type: " + content_type + "\r\n");
            
            response += OPTIONS_APPENDIX;
            response += ("Content-Length: " + std::to_string(content.length()) + "\r\nConnection: keep-alive\r\n\r\n" + content);

            return response;
        };
};