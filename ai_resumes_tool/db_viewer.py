import sqlite3

DB_FILE = "resumes.db"

def view_all_users():
    """Get all users from database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, created_at FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        return []

def view_all_resumes():
    """Get all resumes from database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                r.id, 
                u.username, 
                r.original_resume, 
                r.improved_resume, 
                r.job_description, 
                r.created_at
            FROM resumes r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.created_at DESC
        """)
        resumes = cursor.fetchall()
        conn.close()
        return resumes
    except Exception as e:
        return []

def get_user_count():
    """Get total number of users"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        return 0

def get_resume_count():
    """Get total number of resumes"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM resumes")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        return 0

def delete_all_data():
    """Delete all data from database (for testing/reset)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM resumes")
        cursor.execute("DELETE FROM users")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def get_database_stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get stats
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM resumes")
        resume_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(LENGTH(improved_resume)) FROM resumes")
        avg_resume_length = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "users": user_count,
            "resumes": resume_count,
            "avg_length": int(avg_resume_length)
        }
    except Exception as e:
        return {"users": 0, "resumes": 0, "avg_length": 0}
