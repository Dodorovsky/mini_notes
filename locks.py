import hashlib
import tempfile
import os


def get_lock_path(file_path):
    h = hashlib.md5(file_path.encode("utf-8")).hexdigest()
    lock_dir = os.path.join(tempfile.gettempdir(), "mini_notes_locks")
    os.makedirs(lock_dir, exist_ok=True)
    return os.path.join(lock_dir, f"{h}.lock")

def is_file_already_open(file_path):
    lock_path = get_lock_path(file_path)
    return os.path.exists(lock_path)

def create_file_lock(file_path):
    lock_path = get_lock_path(file_path)
    with open(lock_path, "w") as f:
        f.write("locked")

def remove_file_lock(file_path):
    lock_path = get_lock_path(file_path)
    if os.path.exists(lock_path):
        os.remove(lock_path)