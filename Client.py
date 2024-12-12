import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import threading
import time
import socket

SERVER_HOST = "10.9.139.189"
SERVER_PORT = 8080

# Protocol Notes:
# The server sends messages as HTTP responses. Each incoming message is a full HTTP response.
# We can parse the "Content-Length" header to know how many bytes of the body to read.

def add_message_to_chat(chat_widget, msg):
    chat_widget.config(state='normal')
    chat_widget.insert(tk.END, f"{msg}\n")
    chat_widget.config(state='disabled')
    chat_widget.see(tk.END)  # scroll to bottom

def parse_http_response(response_data):
    # Simple parser for HTTP response body based on Content-Length
    # response_data is a full HTTP response in bytes.
    try:
        response_str = response_data.decode('utf-8', errors='replace')
        # Split headers and body
        headers, body = response_str.split("\r\n\r\n", 1)
        # Parse JSON body if possible
        data = json.loads(body)
        return data
    except:
        return {"message": response_data.decode('utf-8', errors='replace')}

def receive_messages(sock, chat_widget):
    buffer = b""
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                # Server disconnected
                break
            buffer += chunk
            # We may receive multiple responses in one go or partial responses.
            # We'll try to parse them one by one.
            while True:
                # Try to find the end of the header section
                header_end = buffer.find(b"\r\n\r\n")
                if header_end == -1:
                    # Not enough data for one full response yet
                    break
                
                headers_part = buffer[:header_end].decode('utf-8', errors='replace')
                # Find Content-Length to know how much body to read
                cl_index = headers_part.lower().find("content-length:")
                if cl_index == -1:
                    # No Content-Length found, assume the rest of the buffer is body
                    # This is unusual for a proper HTTP response, but let's handle gracefully
                    response_data = buffer
                    buffer = b""
                else:
                    # Parse content-length
                    # Extract line after "Content-Length:"
                    length_line = headers_part[cl_index:].split('\r\n', 1)[0]
                    # length_line like: "Content-Length: 23"
                    content_length = int(length_line.split(':',1)[1].strip())
                    total_length = header_end + 4 + content_length
                    if len(buffer) < total_length:
                        # Not all body received yet
                        break
                    response_data = buffer[:total_length]
                    buffer = buffer[total_length:]
                
                # Now parse the response_data into JSON if possible
                data = parse_http_response(response_data)
                msg = data.get("message", "No message")
                # Add message to chat
                add_message_to_chat(chat_widget, msg)
        except Exception as e:
            print("Error receiving messages:", e)
            break

def send_message(sock, message_entry, chat_widget):
    msg = message_entry.get().strip()
    if not msg:
        return

    # Immediately show the user's own message in the GUI
    add_message_to_chat(chat_widget, f"You: {msg}")

    # Construct an HTTP POST request to send the message
    payload = {"message": msg}
    payload_str = json.dumps(payload)
    request = (
        f"POST / HTTP/1.1\r\n"
        f"Host: {SERVER_HOST}:{SERVER_PORT}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(payload_str)}\r\n"
        "Connection: keep-alive\r\n\r\n"
        f"{payload_str}"
    )

    try:
        sock.sendall(request.encode('utf-8'))
        message_entry.delete(0, tk.END)
    except Exception as e:
        print("Failed to send message:", e)

def gui():
    # Create socket connection to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))

    root = tk.Tk()
    root.title("Simple Chat Client")
    root.geometry("800x600")

    main_frame = ttk.Frame(root, padding="10 10 10 10")
    main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)

    chat_log = scrolledtext.ScrolledText(main_frame, width=80, height=25, wrap='word', state='disabled')
    chat_log.grid(row=0, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W), pady=5)

    message_entry = ttk.Entry(main_frame, width=60)
    message_entry.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
    main_frame.columnconfigure(0, weight=1)

    send_button = ttk.Button(
        main_frame, text="Send",
        command=lambda: send_message(sock, message_entry, chat_log)
    )
    send_button.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

    # Start a thread to continuously read messages from the server
    threading.Thread(target=receive_messages, args=(sock, chat_log), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    gui()