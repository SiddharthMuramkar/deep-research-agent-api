# 03: Watch a Run move through its statuses

**What to build:** After submitting, the Run moves on its own through `planning`, `running` and `done`, about 2 seconds apart, so a caller who polls the status sees it progress.
- A Run that hits an error ends `failed`, with its message.
- When the service starts, any Run cut off by a restart is marked `failed` ("interrupted by restart").
- The placeholder sits behind the single swap point that PR 2 uses for the real Architecture.

**Blocked by:** 02

**Status:** done

- [x] A submitted Run reaches `done` through `planning` and `running`, with no further requests. The wait is configurable, and it is zero in the tests.
- [x] The background work starts through `start_run(run_id)` with FastAPI `BackgroundTasks`.
- [x] If the work raises an error, the Run ends `failed` with the error message. A test swaps in work that raises, to check this.
- [x] On startup, Runs left `queued`, `planning` or `running` become `failed` with "interrupted by restart". A test seeds an unfinished Run, to check this.
- [ ] *(deferred to the last PR)* Polling in `/docs` shows the status change in real time.
- [x] The README decision log records open decision #2 (background execution and restart behaviour).
- [x] The Postman collection or curl script has a sample end-to-end Run: submit, then poll until `done`.
- [ ] *(deferred to the last PR)* The developer was taught, then quizzed, and explained back the Run lifecycle, end to end. It is ticked in the spec.

## Comments

- 2026-10-22: Built test-first, with 5 new tests: one through the second seam (work that raises) and four for the start-up sweep. On the real server, a Run went queued, planning, running, done in about 6 seconds. A Run killed mid-way showed "interrupted by restart" after the restart. The status polling was checked with `curl-examples.sh`, which calls the same endpoint as `/docs`; the developer can watch it in `/docs` during the learning check. The teach-and-quiz is still open.
- 2026-10-22 (code review): the `/docs` criterion is un-ticked. It was checked with curl against the same endpoints, but not in the `/docs` page itself. The developer checks it by eye in `/docs` during the learning check.
- 2026-10-22: The teach-and-quiz and the by-eye `/docs` check moved to the last PR (see "Definition of done" in `CLAUDE.md`).
- 2026-10-22: Closed, following the new flow (step 5 in "The flow for every PR" in `CLAUDE.md`). The criteria marked *(deferred to the last PR)* stay open until PR 4.
