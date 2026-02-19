import hashlib
import time

logs = []

def create_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def add_log(action, user, details):
    timestamp = str(time.time())
    prev_hash = logs[-1]["hash"] if logs else "0"

    log_data = f"{action}|{user}|{details}|{timestamp}|{prev_hash}"
    log_hash = create_hash(log_data)

    log_entry = {
        "action": action,
        "user": user,
        "details": details,
        "timestamp": timestamp,
        "prev_hash": prev_hash,
        "hash": log_hash
    }

    logs.append(log_entry)
    return log_entry

def verify_logs():
    for i in range(1, len(logs)):
        prev = logs[i - 1]
        curr = logs[i]

        recomputed = create_hash(
            f"{curr['action']}|{curr['user']}|{curr['details']}|{curr['timestamp']}|{curr['prev_hash']}"
        )

        if recomputed != curr["hash"]:
            return False

        if curr["prev_hash"] != prev["hash"]:
            return False

    return True
