# 🎭 Shadow Council

> **A Multi-Agent AI RPG powered by Sinbad AI**

Shadow Council is an interactive narrative-driven game where you can enter ANY universe you imagine, and watch it come to life through coordinated AI agents. Built with 10+ specialized AI agents working in concert to create living, breathing worlds that remember, react, and evolve with your choices.

**🏆 Winner - "Most Tech Savvy" at USC Claude Hackathon 2024**

Play here: https://sinbad-ai.vercel.app/
Watch here: https://tinyurl.com/39cncmda

---

## 🌟 Features

### 🌍 **Infinite Worlds**
Enter any universe you can imagine:
- **Jurassic Park** - Navigate dinosaur-infested jungles
- **One Piece** - Sail the Grand Line as a pirate
- **Cyberpunk City** - Become a netrunner in neon-lit streets
- **Medieval Fantasy** - Quest as a knight or sorcerer
- **Post-Apocalyptic** - Survive in a wasteland
- *...or literally anything else*

### 🤖 **Multi-Agent AI System**
Powered by **Sinbad AI** - a sophisticated orchestration of 10+ specialized agents:
- **World Builder Agent** - Constructs rich, detailed universes
- **NPC Manager** - Creates dynamic characters with personalities
- **Quest Designer** - Generates adaptive objectives
- **Dialogue Specialist** - Crafts authentic conversations
- **Lore Keeper** - Weaves mythology and backstory
- **Scene Director** - Orchestrates dramatic moments
- **Memory Manager** - Tracks persistent game state
- **Story Coordinator** - Ensures narrative coherence
- **Character Developer** - Manages protagonist growth
- **Threat Analyzer** - Creates dynamic challenges

### 💾 **Persistent Progress**
- **Automatic saving** to MongoDB Atlas
- **Cross-session continuity** - Resume anytime, anywhere
- **Guest sessions** supported - No login required to play
- **Optional Google OAuth** for cloud sync across devices

### 🎮 **Dynamic Gameplay**
- **NPCs remember** every interaction
- **Choices have consequences** that ripple through the story
- **Adaptive quest lines** that respond to your decisions
- **Branching narratives** with multiple outcomes
- **Rich lore** that unfolds as you explore

---

## 🏗️ Architecture

### Multi-Agent Orchestration

```
┌─────────────────────────────────────────────────┐
│           Orchestrator Agent                     │
│     (Coordinates all specialized agents)         │
└─────────────────┬───────────────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
┌─────▼─────┐ ┌──▼──────┐ ┌─▼────────┐
│  World    │ │   NPC   │ │  Quest   │
│  Builder  │ │ Manager │ │ Designer │
└───────────┘ └─────────┘ └──────────┘
      │           │           │
┌─────▼─────┐ ┌──▼──────┐ ┌─▼────────┐
│ Dialogue  │ │  Lore   │ │  Scene   │
│Specialist │ │ Keeper  │ │ Director │
└───────────┘ └─────────┘ └──────────┘
      │           │           │
      └───────────┼───────────┘
                  │
            ┌─────▼─────┐
            │  Memory   │
            │  Manager  │
            └───────────┘
```

### Tech Stack

**Backend:**
- FastAPI (Python) - High-performance API framework
- Agno Framework - Multi-agent orchestration
- MongoDB Atlas - Persistent game state storage
- SQLite - Local development database

**AI Models:**
- Claude Sonnet 4 (Anthropic) - Primary reasoning
- Gemini 1.5 Flash (Google) - Fast generation
- Groq Gemma-2-9B - Specialized tasks

**Frontend:**
- Next.js 15 - React framework with App Router
- TypeScript - Type-safe development
- Tailwind CSS - Utility-first styling
- NextAuth.js - Authentication

**Deployment:**
- Vercel - Frontend hosting
- Render - Backend API hosting
- MongoDB Atlas - Database (M0 Free Tier)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (free tier)
- API Keys:
  - Anthropic Claude API key
  - Google Gemini API key
  - Groq API key

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/aryanparab/SinbadAI.git
cd SinbadAI
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
ENVIRONMENT=development
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
# MongoDB URI only needed for production
# MONGODB_URI=mongodb+srv://...
EOF

# Run backend
uvicorn main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << EOF
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-here
NEXT_PUBLIC_API_URL=http://localhost:8000
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EOF

# Run frontend
npm run dev
```

Frontend will be available at `http://localhost:3000`

---

## 📖 Usage

### Starting a New Game

1. Visit the homepage
2. Click "Begin New Journey"
3. Enter any world/universe you want to explore
4. Start playing!

### Making Choices

- Read the AI-generated scene narration
- Choose from 2-6 dynamic options
- Watch the world react to your decisions
- NPCs remember your actions
- Your choices shape the narrative

### Saving Progress

**Development (SQLite):**
- Progress automatically saves to `data/agent_memory.db`
- Works offline, no account needed

**Production (MongoDB):**
- Sign in with Google (optional)
- Progress syncs to MongoDB Atlas
- Resume from any device

---

## 🎯 How It Works

### Multi-Agent Workflow

```python
User Input → Orchestrator Agent
             ↓
    Analyzes context and player history
             ↓
    Distributes tasks to specialized agents
             ↓
    ┌────────┬────────┬────────┬────────┐
    │ World  │  NPC   │ Quest  │ Scene  │
    │Builder │Manager │Designer│Director│
    └───┬────┴───┬────┴───┬────┴───┬────┘
        │        │        │        │
        └────────┴────┬───┴────────┘
                      │
              Aggregates results
                      ↓
              Validates coherence
                      ↓
            Generates final scene
                      ↓
             Saves to memory
                      ↓
            Returns to player
```

### Memory System

**Short-term Memory:**
- Current scene context
- Recent choices (last 20)
- Active NPCs and quests

**Long-term Memory:**
- Complete game history
- NPC relationship levels
- Discovered lore and secrets
- Major story events
- Player preferences

---

## 🛠️ Development

### Project Structure

```
SinbadAI/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── routes/
│   │   ├── game.py            # Game endpoints
│   │   └── memory_service.py  # Memory operations
│   ├── agents/
│   │   ├── agents_final_nices.py  # Agent definitions
│   │   └── data_validate_game.py  # Response validation
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── data/
│   │   ├── storage.py         # Database selector
│   │   └── mongo_memory.py    # MongoDB adapter
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx       # Home page
│   │   │   ├── game/
│   │   │   │   └── page.tsx   # Game interface
│   │   │   └── api/
│   │   │       ├── auth/      # NextAuth routes
│   │   │       ├── init/      # Game initialization
│   │   │       └── interact/  # Game interaction
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   ├── HomeScreen.tsx
│   │   │   └── GameScreenEnhance.jsx
│   │   ├── hooks/
│   │   │   ├── useGameLogic.ts
│   │   │   └── useGameMemory.ts
│   │   └── styles/
│   ├── package.json
│   └── next.config.js
│
└── README.md
```

### Adding New Agents

```python
# In backend/agents/agents_final_nices.py

new_agent = Agent(
    name="Your Agent Name",
    role="Specialized role description",
    model=gemini_model,  # or groq_model
    instructions=[
        "What this agent should do",
        "Guidelines and constraints"
    ],
    markdown=True
)

# Add to team
team = AgentTeam(
    name="Game Coordination Team",
    agents=[orchestrator_agent, new_agent, ...],
    mode="coordinator"
)
```

### Customizing Worlds

Modify the world generation prompt in `agents_final_nices.py`:

```python
world_builder_agent = Agent(
    instructions=[
        "Generate immersive {world_type} worlds",
        "Include custom elements: ...",
        # Add your customizations
    ]
)
```

---

## 🚢 Deployment

### Backend (Render)

1. Create new Web Service on Render
2. Connect your GitHub repository
3. Set root directory to `backend`
4. Add environment variables:
   ```
   ENVIRONMENT=production
   MONGODB_URI=mongodb+srv://...
   GEMINI_API_KEY=...
   GROQ_API_KEY=...
   ANTHROPIC_API_KEY=...
   ```
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. Import project from GitHub
2. Set root directory to `frontend`
3. Framework: Next.js
4. Add environment variables:
   ```
   NEXTAUTH_URL=https://your-app.vercel.app
   NEXTAUTH_SECRET=<generated-secret>
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   ```
5. Deploy!

---

## 📊 Performance

- **Response Time:** ~3-5 seconds per turn
- **Concurrent Users:** Supports 100+ simultaneous players
- **Database:** MongoDB Atlas M0 (512MB free tier)
- **Cost:** ~$0 for hobby projects (free tiers)

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## 🐛 Known Issues

- OAuth occasionally requires multiple attempts on first login
- Long responses (>2000 chars) may timeout - agent optimizations in progress
- Mobile UI needs responsive design improvements

---

## 🗺️ Roadmap

- [ ] Voice narration with text-to-speech
- [ ] Image generation for scenes and characters
- [ ] Multiplayer co-op mode
- [ ] Community-shared worlds
- [ ] Mobile app (React Native)
- [ ] Discord bot integration
- [ ] Mod support for custom agents

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **USC Claude Club** - For organizing the hackathon
- **Anthropic** - For Claude API and sponsorship
- **Agno Framework** - For multi-agent orchestration
- **Vercel & Render** - For free hosting
- **MongoDB Atlas** - For free database tier

---

## 📧 Contact

**Aryan Parab**
- GitHub: [@aryanparab](https://github.com/aryanparab)
- LinkedIn: [@aryanparab](https://www.linkedin.com/in/aryan-parab-0b44991b2/)
- Email: aryanparab@usc.edu

---

## ⭐ Star History

If you found this project interesting, please consider giving it a star! It helps others discover the project.

[![Star History Chart](https://api.star-history.com/svg?repos=aryanparab/SinbadAI&type=Date)](https://star-history.com/#aryanparab/SinbadAI&Date)

---

<div align="center">

**Built with ❤️ by a USC student**

*Turning AI agents into storytellers, one adventure at a time.*

[🎮 Play Now](https://sinbad-ai.vercel.app) • [🐛 Report Bug](https://github.com/aryanparab/SinbadAI/issues) • [💡 Request Feature](https://github.com/aryanparab/SinbadAI/issues)

</div>
