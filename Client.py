import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import threading
import time
import socket

SERVER_HOST = "10.9.139.189"
SERVER_PORT = 8080

# Global variable to hold the username once set
current_username = None

def add_message_to_chat(chat_widget, msg):
    chat_widget.config(state='normal')
    chat_widget.insert(tk.END, f"{msg}\n")
    chat_widget.config(state='disabled')
    chat_widget.see(tk.END)  # scroll to bottom

def parse_http_response(response_data):
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
            while True:
                header_end = buffer.find(b"\r\n\r\n")
                if header_end == -1:
                    break
                headers_part = buffer[:header_end].decode('utf-8', errors='replace')
                cl_index = headers_part.lower().find("content-length:")
                if cl_index == -1:
                    response_data = buffer
                    buffer = b""
                else:
                    length_line = headers_part[cl_index:].split('\r\n', 1)[0]
                    content_length = int(length_line.split(':',1)[1].strip())
                    total_length = header_end + 4 + content_length
                    if len(buffer) < total_length:
                        break
                    response_data = buffer[:total_length]
                    buffer = buffer[total_length:]
                
                data = parse_http_response(response_data)
                msg = data.get("message", "No message")
                add_message_to_chat(chat_widget, msg)
        except Exception as e:
            print("Error receiving messages:", e)
            break

def send_message(sock, message_entry, chat_widget):
    global current_username
    msg = message_entry.get().strip()
    if not msg:
        return

    # Use the username if set, otherwise "You"
    display_name = current_username if current_username else "You"

    # Immediately show the user's own message in the GUI
    add_message_to_chat(chat_widget, f"{display_name}: {msg}")

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

def set_username(username_entry, set_username_button):
    global current_username
    username = username_entry.get().strip()
    if username:
        current_username = username
        # Disable the username entry and button
        username_entry.config(state='disabled')
        set_username_button.config(state='disabled')

def gui():
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

    # Chat log
    chat_log = scrolledtext.ScrolledText(main_frame, width=80, height=25, wrap='word', state='disabled')
    chat_log.grid(row=0, column=0, columnspan=3, sticky=(tk.N, tk.S, tk.E, tk.W), pady=5)

    # Username entry and button
    username_entry = ttk.Entry(main_frame, width=30)
    username_entry.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W))
    
    set_username_button = ttk.Button(
        main_frame, text="Set Username",
        command=lambda: set_username(username_entry, set_username_button)
    )
    set_username_button.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

    # Message entry and send button
    message_entry = ttk.Entry(main_frame, width=60)
    message_entry.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
    main_frame.columnconfigure(0, weight=1)

    send_button = ttk.Button(
        main_frame, text="Send",
        command=lambda: send_message(sock, message_entry, chat_log)
    )
    send_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

    # Start a thread to continuously read messages from the server
    threading.Thread(target=receive_messages, args=(sock, chat_log), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    gui()