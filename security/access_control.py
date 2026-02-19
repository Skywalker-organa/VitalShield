from datetime import datetime, timedelta

def is_access_allowed(status,created_at,days):
    if status!="Accepted":
        return False, "consent not accepted"
    
    created_date=datetime.strptime(created_at,"%Y-%m-%d")
    expiry_date=created_date+timedelta(days=days)
    
    if datetime.now() > expiry_date:
        return False,"Consent expired"
    return True, "Access Allowed"