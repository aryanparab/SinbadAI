# Sinbad AI

A dynamic adventure with a planned ending, recurring characters, consequential
choices, and playable combat, infiltration and rescue missions.

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

Next.js/React frontend → same-origin API proxy → FastAPI → Groq narrative director.
SQLite locally, or PostgreSQL when DATABASE_URL is set, stores canonical campaign snapshots and daily generation quotas.

Three editable prompts in `backend/prompts/` define the director:

- `story.md`: immersive prose, character agendas, branching decisions and endings.
- `mission.md`: meaningful objectives, aftermath, inventory and collectible rules.
- `combat.md`: playable encounters and clickable scene props.

One model request normally resolves an approach and generates the next story beat; an invalid response gets at most one format-repair request, counted in the shared quota. The legacy tactical endpoint remains compatible with existing clients, but the current UI uses contextual narrative actions. The backend reconciles
inventory deltas, relationship changes, objectives and campaign progress. Client
state is never the authority for owned items or turn counts.

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
and the shared daily model-request cap. The production build validates types and
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

Docker build/run validation remains pending because Docker Desktop was stopped.
Before sharing, verify guest start/resume, a narrative action, Google sign-in/out,
and save persistence after a backend restart.

## DnD-style direction

This is a base for a dynamic tabletop-style RPG. Character attributes, dice checks,
initiative and party play can be added above the same canonical state and encounter
engine. The current product does not claim to implement DnD's official rules.
