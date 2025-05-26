import sqlite3
import os
import streamlit as st
from hashlib import sha256
from datetime import datetime

# Database Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def initialize_database():
    """Initialize the database with secure tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Get a secure database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password, salt=None):
    """Hash password with salt using SHA-256"""
    salt = salt or os.urandom(16).hex()
    return sha256((password + salt).encode()).hexdigest(), salt

def authenticate_user(username, password):
    """Secure user authentication with hashed passwords"""
    try:
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", 
            (username,)
        ).fetchone()
        
        if user:
            input_hash = sha256((password + user['salt']).encode()).hexdigest()
            if input_hash == user['password_hash']:
                conn.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now(), user['id'])
                )
                conn.commit()
                return True
        return False
    except sqlite3.Error as e:
        st.error(f"Authentication error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def register_user(username, password):
    """Secure user registration with password hashing"""
    try:
        conn = get_db_connection()
        
        if conn.execute(
            "SELECT 1 FROM users WHERE username = ?", 
            (username,)
        ).fetchone():
            return False
            
        password_hash, salt = hash_password(password)
        
        conn.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Registration error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def users_exist():
    """Check if any users exist in database"""
    try:
        conn = get_db_connection()
        return conn.execute("SELECT 1 FROM users").fetchone() is not None
    except sqlite3.Error:
        return False
    finally:
        if conn:
            conn.close()