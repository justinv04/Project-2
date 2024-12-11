import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import json
import datetime
import threading

SERVER_URL = "http://10.9.139.189:8080"

def add_message_to_chat(chat_widget, msg):
    """Add a message to the chat log (no timestamp, no user)."""
    chat_widget.config(state='normal')
    chat_widget.insert(tk.END, f"{msg}\n")
    chat_widget.config(state='disabled')
    chat_widget.see(tk.END)  # scroll to bottom

def update_chat(chat_widget, messages):
    """Update the chat widget with all messages received from the server."""
    chat_widget.config(state='normal')
    chat_widget.delete(1.0, tk.END)
    chat_widget.config(state='disabled')

    for m in messages:
        # Assuming each message is just a dict with a "message" field.
        # If the server returns strings directly, adjust accordingly.
        # If the server returns {"message":"Hello"}, then do:
        # msg_text = m.get("message", "")
        # If the server just returns strings, no get needed.
        msg_text = m.get("message", "") if isinstance(m, dict) else str(m)
        add_message_to_chat(chat_widget, msg_text)

def send_message(message_entry, chat_widget):
    """Send a POST request with the message and display it immediately."""
    msg = message_entry.get().strip()
    if not msg:
        return  # Don't send empty messages

    payload = {"message": msg}
    try:
        print("In the send try")
        response = requests.post(SERVER_URL + "/messages", json=payload, timeout=3)
        response.raise_for_status()

        # Attempt to print as JSON
        try:
            print("JSON response:", response.json())
        except ValueError:
            # If the response isn't valid JSON, print raw text
            print("Non-JSON response:", response.text)

        message_entry.delete(0, tk.END)
        # Immediately display the message sent.
        add_message_to_chat(chat_widget, msg)
    except requests.RequestException as e:
        print("RequestException occurred:", str(e))
        # Silently ignore send errors for now
        pass

def gui():
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
    chat_log.grid(row=0, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W), pady=5)

    # Message entry and Send
    message_entry = ttk.Entry(main_frame, width=60)
    message_entry.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
    main_frame.columnconfigure(0, weight=1)

    send_button = ttk.Button(main_frame, text="Send",
                             command=lambda: send_message(message_entry, chat_log))
    send_button.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

    root.mainloop()

if __name__ == "__main__":
    gui()