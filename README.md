
# 🧞‍♂️ Shadow Council - Powered by Sinbad AI

**Shadow Council** is an interactive story-based adventure game powered by AI. Players enter the name of any world (e.g., *Jurassic Park*, *One Piece*), and the AI generates a game universe with lore, characters, and dynamic storylines. The user plays as **Sinbad**, making choices in AI-generated scenes that shape the journey.

---

## 🚀 Features

- 🌍 Dynamic world-building based on user input
- 🧠 AI-generated lore, scenes, characters, and decisions
- 🎮 Interactive multi-choice game flow
- 🔐 Google OAuth for user login
- 💡 Built with React + FastAPI + LLMs

---

## 🗂 Project Structure

```
sinbad-ai/
│
├── backend/               # FastAPI backend with game logic & LLM agents
│   ├── main.py
│   └── requirements.txt
│
├── frontend/              # React frontend for user interface
│   ├── package.json
│   └── ... (components, pages, etc.)
│
├── .env                   # Root-level API keys & secrets
├── .env.local             # Frontend environment (inside /frontend)
└── README.md
```

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/sinbad-ai.git
cd sinbad-ai
```

### 2. Backend Setup (Python + FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

---

### 3. Frontend Setup (React + Next.js)

```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Environment Variables

### Root `.env`

Create a `.env` file in the root folder:

```
GOOGLE_REDIRECT_URI=<your_redirect_uri>
SECRET_KEY=<your_fastapi_secret>

GROQ_API_KEY=<your_groq_api_key>
GEMINI_API_KEY=<your_gemini_api_key>

NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<nextauth_secret>
```

### Frontend `.env.local`

Inside `frontend/`, create a `.env.local` file:

```
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<same_as_in_root_env>
```

---

## 💡 Tech Stack

- **Frontend:** React, Next.js, TailwindCSS
- **Backend:** FastAPI, Python, Uvicorn
- **Auth:** Google OAuth via NextAuth.js
- **AI:** OpenAI / Gemini / Groq LLM APIs

---

## 📸 Demo

(https://drive.google.com/file/d/1eMJqtoheiwn8LkqDPpkzBP83zBTLTw1T/view?usp=sharing)

---

## ✨ Future Improvements

- Save game sessions and progress
- Add custom avatars or character builder
- Enable multiplayer branching choices

---

## 🧑‍💻 Author

**Aryan Parab**  
[LinkedIn](https://linkedin.com/in/yourprofile) • [GitHub](https://github.com/yourusername)

---

## 📄 License

MIT License. See `LICENSE` file for details.
