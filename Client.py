import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext
import requests
import json
import datetime
import threading

SERVER_URL = "http://10.9.139.189:8080"

def add_message_to_chat(chat_widget, prefix, user, msg, timestamp):
    """Add a formatted message to the chat log (scrolledtext widget)."""
    try:
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        # If parsing fails, just show raw timestamp
        formatted_time = timestamp

    chat_widget.config(state='normal')
    # Format: [time] prefix: message
    # For sent messages: prefix = "Sent"
    # For received messages: prefix = "Received"
    chat_widget.insert(tk.END, f"[{formatted_time}] {prefix}: {msg}\n")
    chat_widget.config(state='disabled')
    chat_widget.see(tk.END)  # scroll to bottom

def update_chat(chat_widget, messages, current_user):
    """Update the chat widget with filtered messages (exclude the current_user's own messages)."""
    # We'll clear and re-insert received messages
    chat_widget.config(state='normal')
    chat_widget.delete(1.0, tk.END)
    chat_widget.config(state='disabled')

    # Display only messages from other users, with "Received:" prefix
    for m in messages:
        user = m.get("user", "Unknown")
        message = m.get("message", "")
        timestamp = m.get("timestamp", datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
        if user != current_user:
            add_message_to_chat(chat_widget, "Received", user, message, timestamp)

def send_message(message_entry, chat_widget, current_user_var):
    """Send a POST request with the user's message and display it as sent."""
    msg = message_entry.get().strip()
    if not msg:
        messagebox.showerror("Input Error", "Message cannot be empty.")
        return
    current_user = current_user_var.get().strip()
    if not current_user:
        messagebox.showerror("User Error", "You must set your username before sending messages.")
        return

    payload = {"user": current_user, "message": msg}
    try:
        response = requests.post(SERVER_URL + "/messages", json=payload, timeout=3)
        response.raise_for_status()
        message_entry.delete(0, tk.END)
        # Display the message immediately as "Sent:" so no duplication occurs
        add_message_to_chat(chat_widget, "Sent", current_user, msg, datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    except requests.RequestException as ex:
        messagebox.showerror("Network Error", f"Failed to send message: {str(ex)}")

def refresh_messages(chat_widget, root, current_user_var):
    """Fetch messages in a background thread and update the chat when done."""
    def fetch_data():
        try:
            response = requests.get(SERVER_URL + "/messages", timeout=3)
            response.raise_for_status()
            messages = response.json()
            current_user = current_user_var.get().strip()
            # Update GUI in the main thread
            root.after(0, lambda: update_chat(chat_widget, messages, current_user))
        except requests.RequestException as ex:
            err = ex
            root.after(0, lambda: messagebox.showerror("Connection Error", f"Unable to fetch messages: {str(err)}"))
        finally:
            # Schedule the next refresh after 5 seconds regardless
            root.after(5000, lambda: refresh_messages(chat_widget, root, current_user_var))

    threading.Thread(target=fetch_data, daemon=True).start()

def set_username(username_entry, current_user_var, user_label, message_entry, send_button, start_button, chat_widget, root):
    """Set the current user's username and enable the chat."""
    user = username_entry.get().strip()
    if not user:
        messagebox.showerror("Username Error", "Username cannot be empty.")
        return

    current_user_var.set(user)
    user_label.config(text=f"Current User: {user}")
    messagebox.showinfo("Username Set", f"Your username has been set to: {user}")

    # Enable message entry and send button now that username is set
    message_entry.config(state='normal')
    send_button.config(state='normal')
    start_button.config(state='disabled')

    # Start refreshing messages now that we have a username
    root.after(1000, lambda: refresh_messages(chat_widget, root, current_user_var))

def gui():
    root = tk.Tk()
    root.title("Chat Client")
    root.geometry("800x600")

    main_frame = ttk.Frame(root, padding="10 10 10 10")
    main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)

    # Top frame for username setup
    top_frame = ttk.Frame(main_frame)
    top_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
    ttk.Label(top_frame, text="Enter Username:").grid(row=0, column=0, padx=5, sticky=tk.W)
    username_entry = ttk.Entry(top_frame, width=20)
    username_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))

    current_user_var = tk.StringVar()
    user_label = ttk.Label(top_frame, text="Current User: Not Set")
    user_label.grid(row=1, column=0, columnspan=3, padx=5, sticky=tk.W)

    # Chat log
    chat_log = scrolledtext.ScrolledText(main_frame, width=80, height=25, wrap='word', state='disabled')
    chat_log.grid(row=1, column=0, columnspan=3, sticky=(tk.N, tk.S, tk.E, tk.W), pady=5)

    # Message entry and Send
    message_entry = ttk.Entry(main_frame, width=60, state='disabled')
    message_entry.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
    main_frame.columnconfigure(0, weight=1)

    send_button = ttk.Button(main_frame, text="Send", state='disabled',
                             command=lambda: send_message(message_entry, chat_log, current_user_var))
    send_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

    # Button to confirm username and start chat
    start_button = ttk.Button(top_frame, text="Set Username and Start",
                              command=lambda: set_username(username_entry, current_user_var, user_label, message_entry, send_button, start_button, chat_log, root))
    start_button.grid(row=0, column=2, padx=5, sticky=tk.W)

    root.mainloop()

if __name__ == "__main__":
    gui()