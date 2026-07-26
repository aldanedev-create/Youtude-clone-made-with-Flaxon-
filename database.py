# database.py
import sqlite3
import hashlib
import secrets
from datetime import datetime
from pathlib import Path

DB_PATH = Path("youtube.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            filename TEXT NOT NULL,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()

def init_likes_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(video_id, user_id)
        )
    """)
    conn.commit()
    conn.close()

def init_all():
    init_db()
    init_likes_table()
    print("✅ Database initialized successfully!")

# ============================================================
# AUTO-INIT: This runs when the module is imported
# ============================================================
init_all()

def hash_password(password):
    salt = secrets.token_hex(16)
    hash_value = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hash_value}"

def verify_password(password, hashed):
    try:
        salt, hash_value = hashed.split("$")
        return hashlib.sha256((salt + password).encode()).hexdigest() == hash_value
    except ValueError:
        return False

def create_user(username, email, password):
    conn = get_db()
    cursor = conn.cursor()
    hashed = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, hashed)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and verify_password(password, user["password_hash"]):
        return dict(user)
    return None

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def create_video(user_id, title, description, filename):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO videos (user_id, title, description, filename) VALUES (?, ?, ?, ?)",
        (user_id, title, description, filename)
    )
    conn.commit()
    video_id = cursor.lastrowid
    conn.close()
    return video_id

def get_all_videos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.*, u.username as author 
        FROM videos v 
        JOIN users u ON v.user_id = u.id 
        ORDER BY v.created_at DESC
    """)
    videos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return videos

def get_video(video_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.*, u.username as author 
        FROM videos v 
        JOIN users u ON v.user_id = u.id 
        WHERE v.id = ?
    """, (video_id,))
    video = cursor.fetchone()
    conn.close()
    return dict(video) if video else None

def increment_views(video_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE videos SET views = views + 1 WHERE id = ?", (video_id,))
    conn.commit()
    conn.close()

def toggle_like(video_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM likes WHERE video_id = ? AND user_id = ?", (video_id, user_id))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("DELETE FROM likes WHERE video_id = ? AND user_id = ?", (video_id, user_id))
        cursor.execute("UPDATE videos SET likes = likes - 1 WHERE id = ?", (video_id,))
        liked = False
    else:
        cursor.execute("INSERT INTO likes (video_id, user_id) VALUES (?, ?)", (video_id, user_id))
        cursor.execute("UPDATE videos SET likes = likes + 1 WHERE id = ?", (video_id,))
        liked = True
    
    conn.commit()
    conn.close()
    return liked

def get_like_count(video_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT likes FROM videos WHERE id = ?", (video_id,))
    count = cursor.fetchone()
    conn.close()
    return count[0] if count else 0

def get_comments(video_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM comments WHERE video_id = ? ORDER BY created_at DESC
    """, (video_id,))
    comments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return comments

def add_comment(video_id, user_id, username, text):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comments (video_id, user_id, username, text) VALUES (?, ?, ?, ?)",
        (video_id, user_id, username, text)
    )
    conn.commit()
    comment_id = cursor.lastrowid
    cursor.execute("SELECT * FROM comments WHERE id = ?", (comment_id,))
    comment = cursor.fetchone()
    conn.close()
    return dict(comment)
