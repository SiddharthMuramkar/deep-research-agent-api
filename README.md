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

`OPENROUTER_API_KEY` and `TAVILY_API_KEY` arrive in PR 2.

### Tests and checks

- `uv run pytest`: the tests. The database container must be running. The tests use `research_test`, which they rebuild from the migrations each time.
- `uv run ruff check` and `uv run ruff format`: the style checks.

---

## What you (the human) do

Claude writes the code, runs every command, and keeps the ticket files up to date. You start sessions, answer questions, learn the design, and merge pull requests.

"Type in a **normal terminal**" means the Terminal app. "Type **in Claude Code**" means the prompt you get after you run `claude`.

### 1. First time on a new computer

You need Claude Code installed (claude.com/claude-code). If macOS asks to install "developer tools" when you run `git`, click **Install**.

In a **normal terminal**:

```
git clone https://github.com/siddharth-0044/deep-research-agent-api.git
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
- it teaches you git worktrees (a separate folder for each PR's branch);
- it sets up the folder and branch for PR 1.

It asks you to step in only for things only you can do, such as a browser login.

### 2. Every work session: one ticket

A **ticket** is one small job. Each one gets its own Claude session.

0. In a **normal terminal**, go to the folder Claude set up for this PR and start Claude:
   ```
   cd <the folder Claude told you>
   claude
   ```
   If Claude says you are on `main`, ask it to switch to the PR's branch first. Work never goes straight onto `main`.
1. **Ticket 01 comes first, and you do it yourself.** Type: `help me do ticket 01`. Claude gives you a step-by-step guide (a "wizard") for creating your Logfire account, and you follow it.
2. **Tickets 02, 03 and 04 are built by Claude.** For each one, type the command that starts it. Ticket 02's is:
   ```
   /mattpocock-skills:implement .scratch/pr-1-service-skeleton/issues/02-submit-and-look-up-a-run.md
   ```
   At the end of each ticket, Claude tells you the exact command for the next one.
3. Answer Claude's questions. Each one comes with a recommendation, and replying `yes` accepts it.
4. Claude builds the ticket **test-first** (it writes an automatic check before the code) and explains what it did as it goes. Then tell Claude: `mark this ticket done`.
5. Type `/clear`. It wipes Claude's short-term memory, so the next ticket starts fresh.

```
claude ──► start the ticket ──► Claude builds + explains ──► "mark this ticket done" ──► /clear
   ▲                                                                                       │
   └───────────────────────────────── next ticket ◄────────────────────────────────────────┘
```

### 3. When all of a PR's tickets are done

1. **The learning check.** Claude teaches, then quizzes you on every item in the PR spec's "Must be able to explain" list, and keeps going until you can explain each one back. This is the "Definition of done" in `SPEC.md`: a PR isn't done until you understand it.
2. Claude opens a **pull request** (PR) on GitHub and gives you the link.
3. Open the link and read the summary. Click **Squash and merge**, which is the only option this repo allows, then **Confirm squash and merge**. Or just tell Claude `merge it`, and it does the same.

### 4. Planning the next PR

1. Tell Claude: `let's plan PR 2`. Claude interviews you one question at a time (this is called "grilling").
2. When Claude says the interview is done, type `/mattpocock-skills:to-spec`. It writes the plan.
3. When that finishes, type `/mattpocock-skills:to-tickets`. It shows you a ticket list and asks if it looks right before it saves anything.
4. **Don't type `/clear` during steps 1 to 3.** The three steps need the same conversation. After them, go back to section 2.

### Commands you type in Claude Code

| Command | When |
|---|---|
| `/mattpocock-skills:implement <ticket file>` | building one ticket |
| `/mattpocock-skills:to-spec` | after the planning interview: writes the plan |
| `/mattpocock-skills:to-tickets` | right after `to-spec`: splits the plan into tickets |
| `/mattpocock-skills:ask-matt` | "which of these should I use now?" |
| `/priority` | lost? It re-explains Claude's last answer as ranked points. `/priority 3` covers the last three answers. |
| `/clear` | between tickets (never during planning) |
| `! <command>` | runs a terminal command inside Claude Code when Claude asks you to, for example `! gh auth login` |

### Rules worth knowing

- **Nothing goes straight to `main`,** the official copy of the code. A hook (an automatic check) stops Claude from pushing there, so every change arrives through a PR that you merge. Your own terminal isn't blocked, so don't push to `main` yourself either.
- **Lost or overwhelmed?** Type `/priority`, or tell Claude "explain that from zero".
- **New to this workflow?** Watch Matt Pocock's video "mattpocock/skills: A complete AI Coding workflow, end-to-end" from 6:52: https://www.youtube.com/watch?v=M6mYodf0dJM&t=412s

## Where things live

| Path | What it is |
|---|---|
| `app/` | the service: `main.py` (start-up and endpoints), `runs.py` (a Run's background work), `schemas.py` (API request and response shapes), `tables.py` (database tables), `config.py` (settings) |
| `migrations/` | Alembic: `versions/` holds one numbered script per change to the tables |
| `tests/` | the automated tests |
| `compose.yaml`, `docker/` | how Docker runs PostgreSQL |
| `curl-examples.sh` | sample requests for every endpoint |
| `scripts/setup-logfire.sh` | the wizard that creates your Logfire account, project and write token |
| `SPEC.md` | the assignment brief and the project's Definition of done |
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
| `updated_at` | timestamp with time zone | no | set by the database, and changed on every update |

**Why:**
- **One table for now.** PR 1 only needs to store the Run itself. The tables for Plans, Steps, Sources and Reports come in PR 2, through a new migration.
- **`status` is text with a CHECK constraint**, not a PostgreSQL enum type. The database still rejects any other value. But SQLAlchemy 2.1 no longer drops an enum type along with its table, so a migration would need extra steps to undo cleanly.
- **The table is created only by Alembic migration `0001`.** Any copy of the database reaches the same shape with `alembic upgrade head`, and the tests build their database the same way, so the migration gets tested too.
- **API models and storage models are separate:** Pydantic (`schemas.py`) and SQLAlchemy (`tables.py`). SQLModel, which merges the two, was rejected because it blurs that line and is still at version 0.0.x.

### Background execution and restarts (open decision #2, PR 1)

**Decision:**
- A Run's work runs with FastAPI `BackgroundTasks`, inside the same server process, after the 202 response has gone out.
- It starts through one swap point, `start_run(run_id)` in `app/runs.py`, and finishes `done` or `failed`. Any error is caught and stored on the Run as `"<ErrorType>: <message>"`.
- On start-up, the service marks every Run still `queued`, `planning` or `running` as `failed`, with the error "interrupted by restart".

**Why:**
- `BackgroundTasks` is built into FastAPI. It needs no extra program, queue or database, so there are fewer moving parts to run and explain.
- The cost: the work lives inside the server process, so a restart or crash stops it. The start-up sweep makes that visible instead of leaving Runs stuck forever. A caller who sees "interrupted by restart" can submit the query again.
- **One swap point:** PR 1 puts a placeholder behind `start_run`. It waits about 2 seconds, then reports `planning`; about 2 seconds later `running`; and about 2 seconds later the Run is `done`. PR 2 swaps in a real Architecture at the same place, and the endpoints don't change. `PLACEHOLDER_STEP_SECONDS` sets the wait, and the tests set it to 0.
- **Rejected (YAGNI):** a task queue such as Celery or arq with a separate worker process, and resuming Runs after a restart. Both add infrastructure this project doesn't need: one developer, run locally, a handful of Runs. Cancelling Runs was never planned.
