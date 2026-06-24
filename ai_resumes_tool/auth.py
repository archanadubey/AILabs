import bcrypt
from database import get_user_by_username, create_user

def hash_password(password):
    """Hash password with bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def register_user(username, email, password, password_confirm):
    """Register new user"""
    if password != password_confirm:
        return False, "Passwords do not match"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if not email or "@" not in email:
        return False, "Invalid email"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    password_hash = hash_password(password)
    success = create_user(username, email, password_hash)
    
    if success:
        return True, "Account created successfully"
    else:
        return False, "Username or email already exists"

def login_user(username, password):
    """Login user"""
    user = get_user_by_username(username)
    
    if user is None:
        return None, "Username not found"
    
    user_id, username, email, password_hash = user
    
    if verify_password(password, password_hash):
        return user_id, "Login successful"
    else:
        return None, "Incorrect password"