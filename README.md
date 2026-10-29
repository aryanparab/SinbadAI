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
SQLite stores canonical campaign snapshots and daily generation quotas.

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

## Hosting: Vercel + Railway

The repository is prepared for a Vercel frontend and a Railway backend. The
configuration is checked in; hosting accounts, production domains, secrets and
Google OAuth callback registration still need to be configured.

### 1. Backend on Railway

1. Connect this GitHub repository and select the `prod` branch.
2. Set the service **Root Directory** to `/backend`. Railway detects `Dockerfile`;
   configuration lives in `backend/railway.json` (select `/backend/railway.json`
   as the config file path if the dashboard does not detect it).
3. Attach a persistent volume at `/app/data` **before allowing real play**.
4. Set the variables below. Generate a public backend domain and save its origin.
5. Use one service replica and one Uvicorn worker. The container reads the platform's
   `PORT`; health checks request `/`.

| Backend variable | Value |
| --- | --- |
| `GROQ_API_KEY` | Your Groq key; server only |
| `GROQ_MODEL` | `openai/gpt-oss-120b` |
| `DAILY_AI_CALL_LIMIT` | `100` or your chosen shared daily limit |
| `CAMPAIGN_DB_PATH` | `/app/data/campaigns.sqlite3` |
| `ALLOWED_ORIGINS` | The final frontend origin, e.g. `https://your-project.vercel.app` |

The volume retains saves and the shared quota across deployments. Per-campaign
locks are process-local, so multiple workers/replicas require a database locking
redesign. The daily cap counts model invocations per UTC day, including failed
requests and format repairs. It is not a dollar spending guarantee; configure
provider spending controls separately. Saved adventures remain readable when the
model quota runs out; new narrative actions require available quota.

Railway references: [Dockerfiles](https://docs.railway.com/builds/dockerfiles),
[persistent volumes](https://docs.railway.com/volumes).

### 2. Frontend on Vercel

1. Import this repository, select `prod` as the production branch, and set **Root
   Directory** to `frontend`. Use the Next.js preset and Node 22.
2. Add the variables below to the Production environment. Use separate values
   for local development; never commit live credentials.
3. Deploy, then use the final frontend origin in Google and Railway configuration.
   Redeploy when changing environment variables.

| Frontend variable | Value |
| --- | --- |
| `BACKEND_URL` | Railway HTTPS origin, without `/game/interact` |
| `NEXTAUTH_URL` | Canonical frontend HTTPS origin |
| `NEXTAUTH_SECRET` | A unique secret from `openssl rand -base64 32` |
| `GOOGLE_CLIENT_ID` | Google web OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google web OAuth client secret |

These variables are server-side and must not use a `NEXT_PUBLIC_` prefix.
`frontend/vercel.json` uses native Next.js routing, including `/game` and
`/api/auth/*`; there is no catch-all homepage rewrite.

References: [Vercel environment variables](https://vercel.com/docs/environment-variables),
[NextAuth production options](https://next-auth.js.org/configuration/options).

### 3. Keep Google login working

In the Google Cloud Console, configure a **Web application** OAuth client:

- Authorized JavaScript origins: `http://localhost:3000` and the final frontend origin.
- Authorized redirect URIs: `http://localhost:3000/api/auth/callback/google` and
  `https://YOUR-FRONTEND-DOMAIN/api/auth/callback/google`.
- Configure the consent screen and any test-user restrictions for the intended audience.

Use a stable production domain for OAuth; arbitrary preview URLs are not registered
callbacks. Login is optional, and existing guest saves remain attached to the browser.

### Release checks

- Backend regression suite: 18 tests passed during local preparation.
- Frontend production build passed, with existing hook dependency warnings.
- Local Google provider discovery and redirect initiation can be checked without
  signing in; completing OAuth requires the configured Google account and callback.
- Docker build/run validation is **pending**: Docker Desktop's daemon was stopped.
- After deployment, verify backend `/`, guest start/resume, one narrative action,
  Google sign-in/sign-out, and save persistence after a backend restart.

## DnD-style direction

This is a base for a dynamic tabletop-style RPG. Character attributes, dice checks,
initiative and party play can be added above the same canonical state and encounter
engine. The current product does not claim to implement DnD's official rules.
