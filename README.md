# Deep Research Agent API

A FastAPI service that takes one research question, researches it on the web in the background, and returns a cited report. The full assignment is in [`SPEC.md`](SPEC.md).

**Status:** PR 1, the service skeleton, is being built. A caller can submit a query and watch its Run move through its statuses; a placeholder stands in for the research until PR 2. The plan and tickets are in [`.scratch/pr-1-service-skeleton/`](.scratch/pr-1-service-skeleton/). Each PR adds to this README; the choices made so far are in the [decision log](#decision-log).

## Run it locally

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running) and [uv](https://docs.astral.sh/uv/).

1. **Settings (first time only):** `cp .env.example .env`. The defaults work with the database below.
2. **Start the database:** `docker compose up -d`. This runs PostgreSQL 18 in a container, and its data lives in the `postgres-data` Docker volume. The first start also creates a second, empty database, `research_test`, for the tests.
3. **Build or update the tables:** `uv run alembic upgrade head`. This runs every migration the database hasn't had yet.
4. **Start the service:** `uv run uvicorn app.main:app --reload --port 8001`. `--reload` restarts it when the code changes. Port 8001 is used because, on the developer's Mac, another project's container holds port 8000.
5. **Try it:** open http://127.0.0.1:8001/docs and use **Try it out** on each endpoint, or run `bash curl-examples.sh` in a second terminal.

To stop: press Ctrl+C for the service, and run `docker compose stop` for the database. `docker compose down -v` also deletes the database's data.

### Environment variables

They are read from the environment or from `.env`, which git ignores. [`.env.example`](.env.example) lists them.

| Variable | Needed | What it is |
|---|---|---|
| `DATABASE_URL` | yes | The PostgreSQL connection. The service refuses to start without it. |
| `LOGFIRE_TOKEN` | no | Lets the service send traces to Logfire. Without it, nothing is sent. To get one, run `bash scripts/setup-logfire.sh` in a normal terminal: it walks you through sign-up and saves the token in `.env`. |
| `PLACEHOLDER_STEP_SECONDS` | no | How long the placeholder waits before each status change. The default is 2, and the tests use 0. |

`OPENROUTER_API_KEY` and `TAVILY_API_KEY` arrive in PR 2.

### View the traces in Logfire

A **trace** is the timeline of one piece of work. Each **span** in it is one timed step, and spans nest inside each other like folders.

1. Get a token once with `bash scripts/setup-logfire.sh`. Then start (or restart) the service, as in step 4 above.
2. Submit a query, from `/docs` or with `bash curl-examples.sh`.
3. Open your Logfire region's site (https://logfire-us.pydantic.dev or https://logfire-eu.pydantic.dev), choose the `deep-research-agent-api` project, and open **Live**.
4. Click the `POST /research/query` row, then expand it. A Run's trace looks like this:

```
POST /research/query              ~5 ms   ← automatic (FastAPI): ends when the 202 is sent
├─ INSERT INTO runs …                     ← automatic (asyncpg): every database query
└─ BackgroundTask start_run       ~6 s    ← automatic (Logfire): the background work
   └─ research run  run_id=…      ~6 s    ← the one manual span, in app/runs.py
      ├─ UPDATE runs SET status=…         (planning)
      ├─ UPDATE runs SET status=…         (running)
      └─ UPDATE runs SET status=…         (done)

GET /research/{run_id}/status     ~4 ms   ← each poll is its own small trace
└─ SELECT … FROM runs …
```

Every `UPDATE` sits between a `BEGIN` and a `COMMIT`: those are the transaction around each change. If a Run fails, its `research run` span is marked as an error, and the `UPDATE` that records `failed` comes right after it. To find one Run, search for its `run_id`.

### Tests and checks

- `uv run pytest`: the tests. The database container must be running. The tests use `research_test`, which they rebuild from the migrations each time.
- `uv run ruff check` and `uv run ruff format`: the style checks.

---

## What you (the human) do

Claude writes the code, runs every command, and keeps the ticket files up to date. You start sessions, answer questions, and merge pull requests. You learn the whole design in the last PR.

"Type in a **normal terminal**" means the Terminal app. "Type **in Claude Code**" means the prompt you get after you run `claude`.

### 1. First time on a new computer

You need Claude Code installed (claude.com/claude-code). If macOS asks to install "developer tools" when you run `git`, click **Install**.

In a **normal terminal**:

```
git clone https://github.com/SiddharthMuramkar/deep-research-agent-api.git
cd deep-research-agent-api
claude
```

Claude Code may ask you to install the **mattpocock-skills** plugin. Say yes, because every `/mattpocock-skills:…` command below comes from it.

Then type this **in Claude Code**:

```
read the handoff and set up this machine
```

Claude reads [`.scratch/handoff.md`](.scratch/handoff.md) and does the setup:
- it installs the tools and `/priority`;
- it adds Context7, which Claude uses to look up library docs;
- it asks you once how PostgreSQL (the database) should run on this machine;
- it sets up git worktrees for you (a separate folder for each PR's branch);
- it sets up the folder and branch for PR 1.

It asks you to step in only for things only you can do, such as a browser login.

### 2. Every PR: six steps

You decided this on 2026-10-22. Every PR follows the same six steps:

```
1 folder ──► 2 grilling ──► 3 to-spec ──► 4 to-tickets ──► 5 implement-spec ──► 6 merge
             └──────── one conversation: no /clear ───────┘
```

1. **A folder for the PR.** In Claude Code, say `set up the folder for PR <number>`. Claude makes a git worktree (a separate folder with the PR's own branch). Then, in a **normal terminal**:
   ```
   cd <the folder Claude told you>
   claude
   ```
   If Claude says you are on `main`, ask it to switch to the PR's branch first. Work never goes straight onto `main`.
2. **Grilling.** Type `/mattpocock-skills:grill-with-docs`. Claude asks only the decisions this PR needs, one at a time, each with a recommendation. Replying `yes` accepts it.
3. **The plan.** When Claude says the interview is done, type `/mattpocock-skills:to-spec`.
4. **The tickets.** Then type `/mattpocock-skills:to-tickets`. It shows you a ticket list and asks if it looks right before it saves anything. **Don't type `/clear` during steps 2 to 4,** because they need the same conversation.
5. **The build.** Type `/mattpocock-skills:implement-spec .scratch/pr-<N>-<slug>/spec.md`, using the spec path that `to-spec` printed. It has the same name as the branch, for example `.scratch/pr-1-service-skeleton/spec.md`. Claude builds every ticket **test-first** (it writes an automatic check before the code), reviews its own work, fixes what the review finds, and opens a **pull request** (PR) on GitHub. If a step needs you, such as a sign-up, Claude gives you a step-by-step guide (a "wizard").
6. **Merge.** Open the PR link, click **Squash and merge** (the only option this repo allows), then **Confirm squash and merge**. Or tell Claude `merge it`. In the last PR, the learning in section 3 comes before this step.

### 3. The last PR: you learn everything

Until the last PR, nobody quizzes you. Each PR's spec still collects a "Must be able to explain" list. In the last PR (PR 4), Claude teaches you every item from every PR's list, plus the by-eye checks that earlier PRs left for later (watching `/docs` and the Logfire traces). It uses the finished README, the real code and the real traces. Then Claude quizzes you, re-explains anything shaky, and quizzes again. The last PR merges only when you can explain each item back.

### Commands you type in Claude Code

| Command | When |
|---|---|
| `/mattpocock-skills:grill-with-docs` | step 2: the planning interview |
| `/mattpocock-skills:to-spec` | step 3: writes the plan |
| `/mattpocock-skills:to-tickets` | step 4: splits the plan into tickets |
| `/mattpocock-skills:implement-spec <spec file>` | step 5: builds every ticket and opens the PR |
| `/mattpocock-skills:ask-matt` | "which of these should I use now?" |
| `/priority` | lost? It re-explains Claude's last answer as ranked points. `/priority 3` covers the last three answers. |
| `/clear` | between PRs (never during steps 2 to 4) |
| `! <command>` | runs a terminal command inside Claude Code when Claude asks you to, for example `! gh auth login` |

### Rules worth knowing

- **Nothing goes straight to `main`,** the official copy of the code. A hook (an automatic check) stops Claude from pushing there, so every change arrives through a PR that you merge. Your own terminal isn't blocked, so don't push to `main` yourself either.
- **Lost or overwhelmed?** Type `/priority`, or tell Claude "explain that from zero".
- **New to this workflow?** Watch Matt Pocock's video "mattpocock/skills: A complete AI Coding workflow, end-to-end" from 6:52: https://www.youtube.com/watch?v=M6mYodf0dJM&t=412s

## Where things live

| Path | What it is |
|---|---|
| `app/` | the service: `main.py` (start-up and endpoints), `runs.py` (a Run's background work), `database.py` (the database connection), `schemas.py` (API request and response shapes), `tables.py` (database tables), `config.py` (settings) |
| `migrations/` | Alembic: `versions/` holds one numbered script per change to the tables |
| `tests/` | the automated tests |
| `compose.yaml`, `docker/` | how Docker runs PostgreSQL |
| `curl-examples.sh` | sample requests for every endpoint |
| `scripts/setup-logfire.sh` | the wizard that creates your Logfire account, project and write token |
| `SPEC.md` | the assignment brief and the project-level Definition of done. Its per-PR part was replaced on 2026-10-22: see "Definition of done" in `CLAUDE.md` |
| `CLAUDE.md` | how Claude works with you (Claude reads it automatically) |
| `GLOSSARY.md` | the project's words: Run, Architecture, Plan, … |
| `.scratch/<pr>/spec.md` | one PR's plan and decisions |
| `.scratch/<pr>/issues/` | that PR's tickets |
| `.scratch/handoff.md` | notes for continuing on a new machine. Deleted once PR 1 is merged and PR 2 is planned. |
| `docs/research/` | verified facts about the libraries |
| `.claude/` | project settings, the push guard hook, and the `/priority` skill |

## Decision log

The choices made so far, newest last, each with its reasoning. The open decisions they settle are listed at the end of [`SPEC.md`](SPEC.md).

### PostgreSQL runs in Docker Desktop (PR 1)

**Decision:** PostgreSQL 18 runs in one Docker container, described in `compose.yaml`.

**Why:**
- The PR 1 spec planned one Podman container, because the original Fedora laptop had Podman installed. The Mac has Docker Desktop installed instead, and it does the same job, so only the tool changed.
- A container keeps the database apart from the rest of the computer, and it can be wiped and recreated with one command.
- Docker Desktop is free for personal and educational use.
- Rejected: installing Podman, which is extra setup for the same result; and installing PostgreSQL directly on the Mac, which is harder to reset to a clean state.

### API shape of the submit and status endpoints (part of open decision #7, PR 1)

| Request | Success | Errors |
|---|---|---|
| `POST /research/query` with `{"query": "..."}` | **202 Accepted** `{"run_id": "<uuid>", "status": "queued"}` | **422** if `query` is missing, blank, or longer than 2000 characters |
| `GET /research/{run_id}/status` | **200 OK** `{"run_id", "status", "error", "created_at", "updated_at"}` | **404** `{"detail": "Run not found"}`; **422** if `run_id` isn't a UUID |

**Why:**
- **202, not 200:** the service has accepted the Run but hasn't done the research yet. The research happens in the background, and the caller polls the status endpoint to follow it.
- **The body is only `query`.** The spec's optional architecture field waits for PR 3, when a second Architecture exists to choose from.
- **The query is trimmed, then must be 1 to 2000 characters.** That stops empty and oversized queries before they reach any code. Pydantic checks this and FastAPI turns a failure into a 422 that names the field.
- **Run IDs are random UUIDs (version 4).** Nobody can find another caller's Run by counting.
- **`error` is `null` unless the Run failed.**

### The `runs` table (part of open decision #8, PR 1)

| Column | Type | Empty allowed? | Holds |
|---|---|---|---|
| `id` | UUID | no | the run ID (primary key) |
| `query` | text | no | the caller's question |
| `status` | text, limited to `queued`, `planning`, `running`, `done` or `failed` | no | where the Run is in its lifecycle |
| `error` | text | **yes** | the error message, only when the Run failed |
| `created_at` | timestamp with time zone | no | set by the database when the row is added |
| `updated_at` | timestamp with time zone | no | set by the database when the row is added; every update the app makes sets it to the database's current time, `now()` |

**Why:**
- **One table for now.** PR 1 only needs to store the Run itself. The tables for Plans, Steps, Sources and Reports come in PR 2, through a new migration.
- **`status` is text with a CHECK constraint**, not a PostgreSQL enum type. The database still rejects any other value. But SQLAlchemy 2.1 no longer drops an enum type along with its table, so a migration would need extra steps to undo cleanly.
- **The table is created only by Alembic migration `0001`.** Any copy of the database reaches the same shape with `alembic upgrade head`, and the tests build their database the same way, so the migration gets tested too.
- **API models and storage models are separate:** Pydantic (`schemas.py`) and SQLAlchemy (`tables.py`). SQLModel, which merges the two, was rejected because it blurs that line and is still at version 0.0.x.

### Background execution and restarts (open decision #2, PR 1)

**Decision:**
- A Run's work runs with FastAPI `BackgroundTasks`, inside the same server process, after the 202 response has gone out.
- It starts through one swap point, `start_run(run_id, query)` in `app/runs.py`. That function runs the Run's work, then records `done`, or `failed` if any error was raised, with the error stored on the Run as `"<ErrorType>: <message>"`.
- **The statuses only move forward** (`queued` → `planning` → `running` → `done`), because `start_run` is the only code that changes them, and it does so in that order. Any unfinished status can become `failed`: through an error, or through the start-up sweep.
- On start-up, the service marks every Run still `queued`, `planning` or `running` as `failed`, with the error "interrupted by restart".

**Why:**
- `BackgroundTasks` is built into FastAPI. It needs no extra program, queue or database, so there are fewer moving parts to run and explain.
- The cost: the work lives inside the server process, so a restart or crash stops it. The start-up sweep makes that visible instead of leaving Runs stuck forever. A caller who sees "interrupted by restart" can submit the query again.
- **One swap point:** the endpoint only hands the Run's ID and query to `start_run`. In PR 1, `start_run` runs a placeholder. It waits about 2 seconds, then reports `planning`; about 2 seconds later `running`; and about 2 seconds later the Run is `done`. PR 2 points `research` (in `app/runs.py`) at a real Architecture, and the endpoints don't change. `PLACEHOLDER_STEP_SECONDS` sets the wait, and the tests set it to 0.
- **Rejected (YAGNI):** a task queue such as Celery or arq with a separate worker process, and resuming Runs after a restart. Both add infrastructure this project doesn't need: one developer, run locally, a handful of Runs. Cancelling Runs was never planned.

### Tracing: one trace per Run, under its submit request (PR 1)

**Decision:**
- Logfire records every request (FastAPI) and every database query (asyncpg) automatically.
- One manual span, `research run`, carries the run ID and wraps the background work.
- Traces are sent only when `LOGFIRE_TOKEN` is set. The tests force it empty, so they never send anything.

**Why:**
- **One trace per Run:** a Run's background work runs inside its `POST` request's handling, so its spans join that request's trace. The whole story of a Run is then in one place, and each status poll stays out of it as its own small trace.
- **Database queries are recorded at the asyncpg level.** Logfire's SQLAlchemy hook comes from OpenTelemetry, and its newest version (0.66b1) only supports SQLAlchemy below 2.1, so it would record nothing here. Recording one layer lower, at asyncpg, catches the same queries. This was checked by capturing a Run's spans locally.
- **Rejected for now:** a separate trace per Run, with its trace ID stored on the Run. That would keep the request's trace and the Run's trace apart, and it would need a new column and manual linking. One trace per Run is simpler and enough for PR 1.

**Checked while building: does the `POST` span last as long as the Run?** No. With Logfire 5.2, the `POST /research/query` span **ends when the 202 response is sent**, after about 5 ms. The background work appears as a child span, `BackgroundTask start_run`, which lasts the whole Run (about 6 seconds). So a child span outlasts its parent. That's allowed: a parent span only says where the work came from, not that it waits for its children. This was measured from a locally captured trace. On 2026-10-22 the first Run's trace arrived in Logfire, and the developer saw a span of 821 µs. The full by-eye check is part of the last PR's learning.
