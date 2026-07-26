
# FlaxTube - YouTube Clone

A fully functional YouTube clone built with **Flaxon** framework, featuring user authentication, video uploads, likes, comments, and a responsive UI.

![FlaxTube](https://img.shields.io/badge/FlaxTube-v1.0.0-red)
[![Built with Flaxon](https://img.shields.io/badge/Built%20with-Flaxon-3776AB)](https://github.com/aldanedev-create/Flaxon-Backend-Framework)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Live Demo


---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **User Authentication** | Sign up, login, and logout with session management |
| 📹 **Video Upload** | Upload MP4/WebM videos with title and description |
| ▶️ **Video Player** | Watch uploaded videos with a built-in player |
| ❤️ **Like System** | Like/unlike videos (requires login) |
| 💬 **Comments** | Post and view comments on videos |
| 👁️ **View Counter** | Track video views automatically |
| 📋 **Video List** | Browse all uploaded videos with metadata |
| 📱 **Responsive** | Works on desktop and mobile |
| 💾 **SQLite Database** | Lightweight file-based database |

---

## 🛠️ Tech Stack

| Technology | Description |
|------------|-------------|
| **Flaxon** | Python async-first backend framework |
| **SQLite** | Lightweight database |
| **Jinax** | Jinja2 template engine for HTML rendering |
| **HTML5** | Semantic markup |
| **CSS3** | Modern styling with responsive design |
| **Vanilla JS** | Client-side interactivity |

---

## 📸 Screenshots

┌──────────────────────────────────────────────────────────┐
│ ▶ FlaxTube Home Upload Login Sign Up │
├──────────────────────────────────────────────────────────┤
│ │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │ ▶ │ │ ▶ │ │ ▶ │ │
│ │ Title 1 │ │ Title 2 │ │ Title 3 │ │
│ │ 100 views│ │ 50 views │ │ 75 views │ │
│ └──────────┘ └──────────┘ └──────────┘ │
│ │
└──────────────────────────────────────────────────────────┘

text

### Watch Page
┌──────────────────────────────────────────────────────────┐
│ ▶ FlaxTube Home Upload 👤 User Logout │
├──────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────────────────────────────────────────┐ │
│ │ Video Player │ │
│ │ │ │
│ └──────────────────────────────────────────────────┘ │
│ │
│ Video Title │
│ 100 views • 2024-01-01 • By: Author │
│ ❤️ 5 Likes │
│ │
│ ─── Comments ─── │
│ [Write a comment...] [Post] │
│ │
│ User1: Great video! │
│ User2: Awesome content! │
│ │
└──────────────────────────────────────────────────────────┘

text

---

## 📦 Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/flaxtube.git
cd flaxtube
Create Virtual Environment
bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install Dependencies
bash
pip install flaxon uvicorn jinja2
Or use requirements.txt:

bash
pip install -r requirements.txt
Initialize Database
bash
python -c "import database; database.init_all()"
Run the Application
bash
flaxon run app:app --reload
Visit the App
Open your browser and go to: http://localhost:8000

🗂️ Project Structure
text
flaxtube/
├── app.py              # Main application
├── database.py         # Database operations
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── templates/
│   ├── base.html       # Base template
│   ├── index.html      # Home page
│   ├── watch.html      # Video watch page
│   ├── upload.html     # Video upload page
│   ├── login.html      # Login page
│   └── signup.html     # Sign up page
├── static/
│   ├── style.css       # Stylesheet
│   └── script.js       # JavaScript
└── videos/             # Uploaded videos storage
🚢 Deployment
Deploy on Render
Push code to GitHub

Go to Render.com

Click "New +" → "Web Service"

Connect your GitHub repo

Use these settings:

yaml
Build Command: pip install -r requirements.txt
Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
Click "Create Web Service"

Environment Variables (Optional)
Variable	Description	Default
FLAXON_ENV	Environment mode	production
FLAXON_DEBUG	Debug mode	false
PORT	Server port (Render sets this)	8000
📡 API Endpoints
Method	Endpoint	Description
GET	/	Home page
GET	/watch/<id>	Watch video
GET	/upload	Upload page
POST	/api/videos	Upload video
POST	/api/videos/<id>/like	Like video
POST	/api/videos/<id>/comments	Add comment
POST	/api/videos/<id>/view	Increment views
GET	/api/videos	List videos
GET	/login	Login page
POST	/login	Login API
GET	/signup	Sign up page
POST	/signup	Sign up API
GET	/logout	Logout
🧪 Testing
bash
# Run the app
flaxon run app:app --reload

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/videos
🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Built with ❤️ using Flaxon

Inspired by YouTube

👤 Author
Aldane Hutchinson

GitHub: @aldanedev-create

Twitter: @aldane

⭐ Star History
If you find this project useful, please give it a star! ⭐

📬 Contact
For questions or support, please open an issue on GitHub.

Made with ❤️ and Python

### Home Page
