import os
import time
import tempfile
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import email
from email import policy

MYCALLSIGN = "K0MDT"
WATCH_PATH = f"c:/RMS Express/{MYCALLSIGN}/Messages/"

def print_with_notepad(text: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as f:
        f.write(text)
        temp_path = f.name
    subprocess.run(['notepad.exe', '/p', temp_path], check=True)

def extract_mime_message_text(filepath):
    with open(filepath, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    msg_date = msg.get("Date", "Unknown")
    msg_from = msg.get("From", "Unknown")
    msg_to   = msg.get("To", "Unknown")
    msg_subject = msg.get("Subject", "Unknown")

    body = ""
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_content()
            break
    if not body:
        body = "(No message body found)"
    
    formatted = (
        f"---- Winlink Message ----\n"
        f"Date: {msg_date}\n"
        f"From: {msg_from}\n"
        f"To: {msg_to}\n"
        f"Subject: {msg_subject}\n\n"
        f"{body}\n"
        f"---------------------------"
    )
    return formatted

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".mime"):
            print(f"[NEW MIME MESSAGE FILE] {os.path.basename(event.src_path)}")
            message_text = extract_mime_message_text(event.src_path)
            print_with_notepad(message_text)

if __name__ == "__main__":
    if not os.path.exists(WATCH_PATH):
        print(f"Error: Path does not exist: {WATCH_PATH}")
        exit(1)

    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=False)
    observer.start()

    print(f"Watching for new Winlink MIME messages in: {WATCH_PATH}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
