> **Start here:** a session handoff is waiting. Read `.scratch/handoff.md` before anything else. When its setup and next steps are done, delete that file and this note.

## Working with the developer

The developer is a **complete beginner** with this stack. They have never used Pydantic, and it has been a long time since they used FastAPI endpoints or Alembic. By the end of the project they must be able to explain all of it. Until the last PR, they make only the decisions each PR needs, and the teaching waits for the last PR (see "Definition of done").

- **Explain from zero before every question.** Define each term in plain words, give an everyday analogy, and show a small concrete example such as a request and response, a table or a diagram, so the developer can decide. Keep notes about changes short: the full teaching waits for the last PR.
- **No unexplained jargon.** Don't use a term that hasn't been explained in this session. If it was explained earlier, recap it in one line.
- **Spell out what "yes" commits to.** Every question ends with a plain-words line saying what answering "yes" signs the developer up for.
- **If the developer didn't understand, go back further, not faster.**
- **One question at a time, and only the questions the PR needs.** When grilling, ask a single decision with your recommended answer, then wait for the reply before asking the next one. Don't quiz the developer on what they know before the last PR. Approving `to-spec`'s test seams or `to-tickets`' ticket list is a decision, not a quiz, so still ask.
- **The decisions belong to the developer; the facts are yours.** Find environment facts, library behaviour and service limits yourself, and put every design decision to the developer.
- **You run the mechanics.** Run every command, migration and install yourself. Teach the design and the flow instead, in the last PR: by then, the developer must be able to explain the request flow and the Logfire traces in an interview. They don't need to memorise commands.
- **YAGNI.** Build the simplest thing that meets `SPEC.md`. A plain design the developer can explain beats a clever one they can't.
- **Look it up before you code.** Check a library's docs with Context7 before writing code against it (Pydantic AI, FastAPI, SQLAlchemy, Logfire). Verified notes live in `docs/research/`.
- **Offer `/priority` when the developer is lost.** It is a user-invoked skill in `.claude/skills/priority/` that re-explains the last outputs as ranked points, so suggest that they type it.

## Agent skills

### Issue tracker

Issues and specs live as local markdown files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as a `Status:` line in each issue file, plus `done` for a closed ticket. See `docs/agents/triage-labels.md` and `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Definition of done

The developer decided this on 2026-10-22: **the learning happens in the last PR, not in every PR.** This replaces the per-PR part of "Definition of done" in `SPEC.md`. The project-level part still applies: the project is done only when the developer can explain it.

- **Every PR before the last one** is done when its tickets are built test-first, the `/mattpocock-skills:code-review` findings are fixed, and the PR is squash-merged. There is no teach-and-quiz step. A ticket criterion about teaching, quizzing or a by-eye check is marked *(deferred to the last PR)* instead of ticked.
- **Keep every PR's "Must be able to explain" list** in its spec (`.scratch/<feature>/spec.md`). Whenever a decision is made that the developer doesn't yet understand, add an item to that list.
- **The last PR** (PR 4, Comparison, in the roadmap in `.scratch/pr-1-service-skeleton/spec.md`) teaches everything. It uses the finished README, the real code and the real Logfire traces, and it covers every item from every PR's list, plus the deferred by-eye checks. Act as a tutor and interview coach, not a quizmaster. For each item:
  1. **Explain** it against the real code and trace.
  2. **Quiz** the developer on what you just explained.
  3. **Re-explain** anything shaky, then quiz again.

  Tick an item only after the developer explains it back correctly. The last PR merges only when every item is ticked.

## The flow for every PR

The developer decided this on 2026-10-22. For PR *N*:

1. **Worktree and branch.** Update `main`, then create a git worktree folder `../deep-research-agent-api-pr-N` on a new branch `pr-N-<slug>`, with the slug taken from the roadmap entry. The spec folder uses the same name: `.scratch/pr-N-<slug>/`.
2. **Grilling** (`/mattpocock-skills:grill-with-docs`): only the decisions this PR needs, and no quizzes. Ask **one question per message**. This overrides the grilling skill's numbered rounds: ask the first question on the frontier, wait for the answer, then ask the next.
3. **`/mattpocock-skills:to-spec`**: writes `.scratch/pr-N-<slug>/spec.md`. Its template has no "Must be able to explain" section, so add `### Must be able to explain` under Further Notes. List every decision from the grilling that the developer must be able to explain, marked *Deferred to the last PR*.
4. **`/mattpocock-skills:to-tickets`**: writes the tickets.
   - Include criteria for this PR's README decision-log entries and for its `curl-examples.sh` updates.
   - Mark a ticket that only the developer can do, such as a sign-up or an API key, `Status: ready-for-human`.
   - Its "Quiz the user" step is the developer approving the ticket list. It still runs.
   - Don't clear or compact the context during steps 2 to 4. If the conversation nears ~150k tokens, `/compact` between steps, never during one. A `/clear` before step 5 is fine, because step 5 gets the spec path.
5. **`/mattpocock-skills:implement-spec .scratch/pr-N-<slug>/spec.md`**:
   - The step-1 branch `pr-N-<slug>` **is** the integration branch. Don't create another one.
   - Open a draft PR, with its body written by the `pr` skill, once the first work lands on that branch. implement-spec opens a PR only when asked, and this is the request.
   - Run implementer subagents one at a time, because every worktree's tests share the `research_test` database.
   - Never give a `ready-for-human` ticket to an implementer. Write its `wizard` in the main session, wait until the developer has run it, then close the ticket.
   - For the review step, use `/mattpocock-skills:code-review` (not the built-in `code-review`), with fixed point `main` and the spec path. Put each finding that changes a design decision, such as the API shape, the schema, the swap point or a domain term, to the developer, one question at a time. Fix plain bugs and standards issues without asking.
   - Close every ticket as `docs/agents/issue-tracker.md` says, then mark the PR ready for review.
6. **Squash-merge the PR.** The developer clicks **Squash and merge**, or tells Claude `merge it`. **In the last PR (PR 4)**, the teach-and-quiz from "Definition of done" comes between steps 5 and 6, and the PR merges only when every item is ticked.

## Where decisions live

A PR's decisions go into that PR's spec through `/to-spec`, and the README decision log explains them. If `domain-modeling` offers an ADR, ask the developer whether it goes in `docs/adr/` or only in the spec and the decision log. Never add them to `SPEC.md`, which is the assignment brief, or to Claude's memory. Domain terms go in `GLOSSARY.md`, and researched facts go in `docs/research/`.
