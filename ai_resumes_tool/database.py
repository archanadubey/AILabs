import sqlite3
import os 
from datetime import datetime

DB_FILE = "resumes.db"

def init_db():
    """Initialize the database and create users and resumes tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Resume table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            original_resume TEXT NOT NULL,
            improved_resume TEXT NOT NULL,
            job_description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

def get_user_by_username(username):
    """Get user by username from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, email, password_hash):
    """Create new user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def save_resume(user_id, original, improved, job_description):
    """Save resume improvement to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO resumes (user_id, original_resume, improved_resume, job_description) VALUES (?, ?, ?, ?)",
        (user_id, original, improved, job_description)
    )
    conn.commit()
    conn.close()

def get_user_resumes(user_id):
    """Get all resumes for a user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, original_resume, improved_resume, job_description, created_at FROM resumes WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    resumes = cursor.fetchall()
    conn.close()
    return resumes

# Initialize DB on module load
init_db()