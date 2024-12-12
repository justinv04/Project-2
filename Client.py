import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import json
import threading
import time

SERVER_URL = "http://10.9.139.189:8080 "  # Adjust to your server's IP if needed

def add_message_to_chat(chat_widget, msg):
    chat_widget.config(state='normal')
    chat_widget.insert(tk.END, f"{msg}\n")
    chat_widget.config(state='disabled')
    chat_widget.see(tk.END)  # scroll to bottom

def update_chat(chat_widget, messages):
    chat_widget.config(state='normal')
    chat_widget.delete(1.0, tk.END)
    chat_widget.config(state='disabled')

    for m in messages:
        msg_text = m.get("message", "") if isinstance(m, dict) else str(m)
        add_message_to_chat(chat_widget, msg_text)

def fetch_messages(chat_widget):
    try:
        response = requests.get(SERVER_URL + "/messages", timeout=3)
        response.raise_for_status()
        data = response.json()
        msgs = data.get("messages", [])
        update_chat(chat_widget, msgs)
    except requests.RequestException as e:
        print("Error fetching messages:", e)

def poll_messages(chat_widget):
    while True:
        fetch_messages(chat_widget)
        time.sleep(2)  # Poll every 2 seconds

def send_message(message_entry, chat_widget):
    msg = message_entry.get().strip()
    if not msg:
        return

    payload = {"message": msg}
    try:
        response = requests.post(SERVER_URL, json=payload, timeout=1)
        response.raise_for_status()
        print(response.json())
        message_entry.delete(0, tk.END)
        # After sending, fetch updated messages
        fetch_messages(chat_widget)
    except requests.RequestException as e:
        print("RequestException occurred:", str(e))

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

    chat_log = scrolledtext.ScrolledText(main_frame, width=80, height=25, wrap='word', state='disabled')
    chat_log.grid(row=0, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W), pady=5)

    message_entry = ttk.Entry(main_frame, width=60)
    message_entry.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
    main_frame.columnconfigure(0, weight=1)

    send_button = ttk.Button(main_frame, text="Send",
                             command=lambda: send_message(message_entry, chat_log))
    send_button.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

    # Start a thread to poll messages from the server
    threading.Thread(target=poll_messages, args=(chat_log,), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    gui()