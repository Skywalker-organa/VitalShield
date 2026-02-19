from security.hashing import add_log, verify_logs

add_log("REQUEST", "Org1", "Blood Report")
add_log("ACCEPT", "Patient1", "Approved")
add_log("REVOKE", "Patient1", "Revoked")

print("Logs valid?", verify_logs())
