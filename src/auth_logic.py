import sqlite3
import hashlib
import os

# Ensures the database is stored in the data/ folder
DB_PATH = os.path.join('data', 'users.db')

def init_db():
    """Creates the users table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

def hash_password(password):
    """Securely hashes passwords."""
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(username, password):
    """Registers a new user."""
    if not username or not password:
        return False
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users(username, password) VALUES (?,?)', 
                  (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    """Validates user credentials."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
              (username, hash_password(password)))
    data = c.fetchone()
    conn.close()
    return data