from pathlib import Path
from datetime import datetime
import os
import secrets
from flaxon import Flaxon, HTTPException, Response, Request
from flaxon.jinax import Jinax
from flaxon.validation import Schema
from flaxon.validation.fields import StrField
from flaxon.files import FileUpload, FileStorage
from flaxon.middleware import CORSMiddleware
import database as db

# ============================================================
# Application Setup
# ============================================================

app = Flaxon("youtube-clone", debug=False)

# CORS
app.add_middleware(CORSMiddleware, allowed_origins=["*"])

# Templates
app.use_templates(Jinax("templates", auto_reload=False))

# File storage
videos_path = os.environ.get("VIDEOS_PATH", "videos")
storage = FileStorage(videos_path)
upload_handler = FileUpload(max_size=100 * 1024 * 1024)

# ============================================================
# Session Management
# ============================================================

sessions = {}

def get_session(request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        user_id = sessions[session_id]
        return db.get_user_by_id(user_id)
    return None

def set_session(response, user_id):
    session_id = secrets.token_hex(32)
    sessions[session_id] = user_id
    response.headers["Set-Cookie"] = f"session_id={session_id}; Path=/; HttpOnly; Max-Age=604800; SameSite=Lax"
    return session_id

def clear_session(response):
    response.headers["Set-Cookie"] = "session_id=; Path=/; HttpOnly; Max-Age=0; SameSite=Lax"

# ============================================================
# Validation Schemas
# ============================================================

class SignupSchema(Schema):
    username = StrField(required=True, min_length=3, max_length=30)
    email = StrField(required=True, max_length=100)
    password = StrField(required=True, min_length=6, max_length=100)

class LoginSchema(Schema):
    username = StrField(required=True)
    password = StrField(required=True)

class CommentCreate(Schema):
    text = StrField(required=True, min_length=1, max_length=500)

# ============================================================
# Routes - Pages
# ============================================================

@app.get("/")
async def index(request):
    user = get_session(request)
    videos = db.get_all_videos()
    return await request.render("index.html", {"videos": videos, "user": user})

@app.get("/watch/<int:video_id>")
async def watch(request, video_id: int):
    user = get_session(request)
    video = db.get_video(video_id)
    
    if not video:
        raise HTTPException(404, "Video not found")
    
    db.increment_views(video_id)
    video = db.get_video(video_id)
    comments = db.get_comments(video_id)
    
    return await request.render("watch.html", {
        "video": video,
        "comments": comments,
        "user": user
    })

@app.get("/upload")
async def upload_page(request):
    user = get_session(request)
    if not user:
        return Response("", status_code=302, headers={"Location": "/login"})
    return await request.render("upload.html", {"user": user})

@app.get("/login")
async def login_page(request):
    user = get_session(request)
    if user:
        return Response("", status_code=302, headers={"Location": "/"})
    return await request.render("login.html", {"user": None})

@app.get("/signup")
async def signup_page(request):
    user = get_session(request)
    if user:
        return Response("", status_code=302, headers={"Location": "/"})
    return await request.render("signup.html", {"user": None})

@app.get("/logout")
async def logout(request):
    response = Response("", status_code=302, headers={"Location": "/"})
    clear_session(response)
    return response

# ============================================================
# Routes - API
# ============================================================

@app.post("/api/videos")
async def upload_video(request):
    user = get_session(request)
    if not user:
        raise HTTPException(401, "Please login to upload")
    
    files = await upload_handler.parse(request)
    title = ""
    description = ""
    filename = ""
    
    for file in files:
        if file.field_name == "title":
            title = file.file.read().decode("utf-8")
        elif file.field_name == "description":
            description = file.file.read().decode("utf-8")
        elif file.field_name == "video":
            filename = f"{user['id']}_{int(datetime.now().timestamp())}_{file.filename}"
            path = storage.save(file, filename=filename)
    
    video_id = db.create_video(user['id'], title, description, filename)
    return {"success": True, "video_id": video_id}

@app.post("/api/videos/<int:video_id>/like")
async def like_video(request, video_id: int):
    user = get_session(request)
    if not user:
        raise HTTPException(401, "Please login to like")
    
    db.toggle_like(video_id, user['id'])
    count = db.get_like_count(video_id)
    return {"likes": count}

@app.post("/api/videos/<int:video_id>/comments")
async def add_comment(request, video_id: int, data: CommentCreate):
    user = get_session(request)
    if not user:
        raise HTTPException(401, "Please login to comment")
    
    comment = db.add_comment(video_id, user['id'], user['username'], data.text)
    return {"comment": comment}

@app.post("/api/videos/<int:video_id>/view")
async def increment_view(video_id: int):
    db.increment_views(video_id)
    return {"success": True}

@app.get("/api/videos")
async def list_videos():
    return {"videos": db.get_all_videos()}

# ============================================================
# Routes - Auth
# ============================================================

@app.post("/signup")
async def signup(request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON body")
    
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")
    
    # Validation
    if not username or len(username) < 3:
        raise HTTPException(400, "Username must be at least 3 characters")
    
    if not email:
        raise HTTPException(400, "Email is required")
    
    if not password or len(password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    
    if password != confirm_password:
        raise HTTPException(400, "Passwords do not match")
    
    # Create user
    user_id = db.create_user(username, email, password)
    if not user_id:
        raise HTTPException(400, "Username or email already exists")
    
    # Auto-login after signup
    user = db.get_user_by_id(user_id)
    response = Response({"success": True, "user": user}, status_code=200)
    set_session(response, user_id)
    return response

@app.post("/login")
async def login(request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON body")
    
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username or not password:
        raise HTTPException(400, "Username and password required")
    
    user = db.get_user(username, password)
    
    if not user:
        raise HTTPException(401, "Invalid username or password")
    
    response = Response({"success": True, "user": user}, status_code=200)
    set_session(response, user['id'])
    return response

# ============================================================
# Routes - Static Files
# ============================================================

@app.get("/static/<path:file_path>")
async def serve_static(file_path: str):
    base_dir = Path("static").resolve()
    target_file = (base_dir / file_path).resolve()
    
    # Prevent path traversal security vulnerabilities
    if not target_file.is_relative_to(base_dir) or not target_file.exists():
        raise HTTPException(404, "File not found")
    
    ext = target_file.suffix.lower()
    content_types = {
        ".css": "text/css",
        ".js": "application/javascript",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".ico": "image/x-icon"
    }
    content_type = content_types.get(ext, "text/plain")
    
    return Response(target_file.read_bytes(), media_type=content_type)

@app.get("/uploads/<path:file_path>")
async def serve_video(file_path: str):
    base_dir = Path(videos_path).resolve()
    target_file = (base_dir / file_path).resolve()
    
    # Prevent path traversal security vulnerabilities
    if not target_file.is_relative_to(base_dir) or not target_file.exists():
        raise HTTPException(404, "File not found")
    
    ext = target_file.suffix.lower()
    content_type = "video/webm" if ext == ".webm" else "video/mp4"
    
    return Response(target_file.read_bytes(), media_type=content_type)

# ============================================================
# Routes - Health Check
# ============================================================

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "flaxtube"}

@app.get("/debug/session")
async def debug_session(request):
    user = get_session(request)
    cookies = request.cookies
    return {
        "has_session": user is not None,
        "user": user,
        "cookies": dict(cookies),
        "sessions": list(sessions.keys()) if sessions else []
    }

# ============================================================
# Run the Application
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
