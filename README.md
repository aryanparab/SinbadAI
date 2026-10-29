# Sinbad AI

A dynamic adventure with a planned ending, recurring characters, consequential
choices, and playable combat, infiltration and rescue missions.

**[Play the live adventure](https://sinbad-ai.vercel.app)** ·
[Backend health](https://sinbad-api.onrender.com/)

Choose a world, try a mission, and watch your decisions change the story. Guest
play is available immediately; Google sign-in is optional. The opening counts as
the first story turn.

The demo runs on free hosting. After inactivity, the backend can take about a
minute to wake. Groq also enforces free-tier rate limits: if prompted, wait about
a minute before retrying. Failed generations leave the saved story turn unchanged.

## How it plays

- Choose a world and a campaign length: 30 story turns by default, or 5–60.
- Story turns are major decisions: choose an allegiance, route, sacrifice or mission.
- Play through scene-specific choices or describe your own approach, like a tabletop adventure.
- Fight, bargain, involve an ally, or use an object in the surroundings. Each committed
  approach spends one story turn; inspection is free. The next passage resolves the attempt.
- Challenges have fictional stakes, not abstract progress meters. Adjudication is narrative;
  this version does not simulate dice rolls or a full D&D ruleset.
- Collectibles, durability, relationships, encounter outcomes and completed quests
  persist. Defeat or retreat changes the route instead of ending the campaign.
- The final turn must contain an explicit epilogue. Failed generations do not
  advance the story.

## Architecture

| Layer | Technology | Deployed on |
| --- | --- | --- |
| Interface and Google login | Next.js, React, NextAuth | Vercel |
| Game API and state reconciliation | FastAPI, Python 3.12 | Render Free, Docker |
| Persistent saves and shared quota | PostgreSQL | Neon Free |
| Narrative generation | Groq, `openai/gpt-oss-120b` | Groq API |

The browser calls same-origin Next.js API routes, which proxy requests to FastAPI.
The backend loads canonical state, requests a scene from Groq, validates the response,
reconciles inventory and objectives, then saves the result in PostgreSQL. SQLite
provides the same storage interface for local development.

Per-campaign locks and stale-scene checks prevent duplicate actions. The backend
owns turn counts and inventory; an invalid model response receives at most one
repair attempt, counted against the shared quota. Opening outlines are required,
and the final turn must resolve the campaign with an epilogue.

Three editable prompts in `backend/prompts/` define the director:

- `story.md`: immersive prose, character agendas, branching decisions and endings.
- `mission.md`: meaningful objectives, aftermath, inventory and collectible rules.
- `combat.md`: playable encounters and clickable scene props.

The current interface uses contextual narrative actions. The older deterministic
tactical endpoint remains compatible with legacy clients; it is not the current
player-facing loop.

The old Agno and Mongo memory experiments remain as historical source files;
the deployed application does not import them. Runtime dependencies are locked
in `backend/requirements.lock`.

## Local setup

Use Python 3.12 and Node 22 (see `frontend/.nvmrc`).

```sh
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.lock
```

Create a root `.env` containing `GROQ_API_KEY`. Optional settings:

```dotenv
GROQ_MODEL=openai/gpt-oss-120b
DAILY_AI_CALL_LIMIT=100
```

Start the backend from `backend/`:

```sh
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Start the frontend from `frontend/`:

```sh
npm ci
BACKEND_URL=http://127.0.0.1:8000 npm run dev
```

On Node 25, prefix the frontend command with
`NODE_OPTIONS=--no-experimental-webstorage`. Prefer the documented Node version.
Google sign-in is available through NextAuth alongside guest play. Both modes currently
use the same browser-local player ID for saves; signing in does not enable cross-device
save sync. Copy `frontend/.env.example` to `frontend/.env.local` and configure the Google
credentials and NextAuth secret to enable login locally. The backend example is `.env.example`.

## Checks

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -m unittest discover -s tests -v
```

From `frontend/`:

```sh
npm run build
npm audit --omit=dev
```

The tests cover inventory quantities and durability, persistent relationships and
objectives, complete 30-turn campaigns, final epilogue requirements, failed model
calls, tactical actions, duplicate requests, one-shot caches, rewards, stale scenes
and the shared daily model-request cap. Additional regressions cover missing
opening-outline repair and actionable provider rate-limit responses. The production build validates types and
lint. Existing hook dependency warnings are visible; checks are not bypassed.

## Free hosting: Vercel + Render + Neon

The frontend stays on the existing Vercel project. `render.yaml` defines a **Free**
Docker web service for the backend, and Neon Free PostgreSQL stores campaign saves
and the shared daily quota. No paid disk is required. Render Free sleeps after
15 minutes idle, so the first request after inactivity can take longer.

1. Create a Neon Free PostgreSQL project (Oregon, to match the backend). Copy its
   connection string with `sslmode=require`; treat it as a password.
2. In Render, create a Web Service from this repository, branch `main`, root
   directory `backend`, runtime Docker, and **Free ($0/month)** compute. Alternatively,
   import the root `render.yaml` as a Blueprint.
3. Set the protected Render variables:

| Variable | Value |
| --- | --- |
| `GROQ_API_KEY` | Your existing Groq API key |
| `DATABASE_URL` | Neon PostgreSQL connection string with SSL |
| `GROQ_MODEL` | `openai/gpt-oss-120b` |
| `DAILY_AI_CALL_LIMIT` | `100` |
| `ALLOWED_ORIGINS` | `https://sinbad-ai.vercel.app` |

4. Deploy and verify the Render `/` health endpoint. Keep one replica and one
   worker: per-campaign action locks are process-local.
5. Set Vercel's production `BACKEND_URL` to the Render HTTPS origin (without
   `/game/interact`) and redeploy. Retain `NEXTAUTH_URL`, `NEXTAUTH_SECRET`,
   `GOOGLE_CLIENT_ID`, and `GOOGLE_CLIENT_SECRET` in Vercel.
6. In Google Cloud, retain the authorized callback
   `https://sinbad-ai.vercel.app/api/auth/callback/google`.

`DATABASE_URL` selects PostgreSQL; local development without it uses SQLite.
Render refuses campaign writes without `DATABASE_URL` so a restart cannot silently
lose saves or reset the shared quota. Existing local SQLite campaigns are not
copied automatically to the hosted database. Signed-in and guest saves currently
remain tied to the browser's player ID, not a cross-device account.

The cap counts model calls per UTC day, including failures and format repairs;
it is not a dollar spending guarantee. Set provider spending controls separately.
Free hosting does not remove the model provider's limits. Neon and Render free
plans have resource allowances; do not enable a paid plan for this setup.

References: [Render Free](https://render.com/docs/free),
[Render Blueprint specification](https://render.com/docs/blueprint-spec),
[Neon Free](https://neon.com/blog/neon-free-plan-1-gb-per-project),
[NextAuth Google callback](https://next-auth.js.org/providers/google).

### Validation

Run the default suite as above. For the optional real PostgreSQL integration tests,
set `TEST_DATABASE_URL` to a **dedicated disposable database** before running the
suite. These tests truncate their campaign and quota tables. They verify save
updates, guest isolation, rollback and concurrent quota enforcement.

Deployment checks completed:

- The Docker image built and launched successfully on Render.
- Production requests pass through Vercel → Render → Neon.
- Live gameplay reached turn 4 with journal entries and a collected artifact.
- Refresh recovery restored the hosted campaign.
- The Google OAuth provider remains available; full sign-in/sign-out was not
  repeated as part of the final deployment check.
- The latest default suite passed 20 tests; three PostgreSQL integration tests
  were skipped without `TEST_DATABASE_URL`. Those three passed separately against
  a real temporary PostgreSQL database during storage validation.
- The frontend production build passed, and the backend dependency audit found
  no known vulnerabilities at deployment time.

Local Docker Desktop validation was not performed. Free-tier cold starts and
model-provider limits remain relevant to demo availability.

## DnD-style direction

This is a base for a dynamic tabletop-style RPG. Character attributes, dice checks,
initiative and party play can be added above the same canonical state and encounter
engine. The current product does not claim to implement DnD's official rules.
