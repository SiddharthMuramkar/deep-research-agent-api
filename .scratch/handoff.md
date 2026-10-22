# Handoff: continue on a new machine

Session 1 wrote this note on 2026-10-22, on the original Fedora laptop. The work continues on a MacBook, under a different Claude account. There is no Claude memory carried over: everything the next session needs is in this repo.

**Next session:** read this file. Then run the setup below, and work through the next steps in order. When everything is done, delete this file and the "Start here" note at the top of `CLAUDE.md`.

## Where things stand

- *Updated on 2026-10-22, on the MacBook:* **PR 1 (service skeleton) is built**, and its draft PR is open on GitHub. The setup below is done. PostgreSQL runs in Docker Desktop.
  - Spec: `.scratch/pr-1-service-skeleton/spec.md`. It holds every decision, the 4-PR roadmap (under Further Notes), and the "Must be able to explain" list, which is deferred to the last PR.
  - Tickets: `.scratch/pr-1-service-skeleton/issues/01…04`, all built. Their teach-and-quiz and by-eye criteria are deferred to the last PR.
- **The assignment brief** is `SPEC.md`, with the project-level Definition of done at the end.
- **How to work with the developer** is in `CLAUDE.md`: a complete beginner; only the decisions each PR needs, one question at a time; no quizzes until the last PR (PR 4), which teaches everything; YAGNI; Context7. **The six steps for every PR** are in "The flow for every PR" in `CLAUDE.md`.
- **Domain words** are in `GLOSSARY.md`. **Research for PR 2** is in `docs/research/pydantic-ai.md`.
- **Push guard:** `.claude/hooks/block-push-to-main.sh` blocks Claude from pushing to `main`. It does not stop the developer's own terminal, because the developer chose a hook only, with no GitHub ruleset. Its tests are `.claude/hooks/test-block-push-to-main.sh`.
- **The `/priority` skill** is in `.claude/skills/priority/`. It works in this repo as-is.

## Decided in session 1, outside PR 1's spec

- **Pydantic AI** is the agent framework from PR 2 onward. The developer chose it and has no prior knowledge of it, so explain from zero whatever a grilling decision about it needs. The full teaching of Pydantic AI happens in the last PR.
- The project builds **two Architectures**. Which two is still open, and gets decided when PR 2 is grilled.

## Setup on this machine (once)

Claude runs these commands, following the "You run the mechanics" rule. The developer does only the interactive logins, by typing `! <command>` in Claude Code.

1. **Check that Matt's plugin is installed.** The project settings enable `mattpocock-skills@claude-plugins-official`, so Claude Code should offer to install it. If `/mattpocock-skills:implement-spec` is still unknown, the developer types `/plugin install mattpocock-skills@claude-plugins-official` and restarts Claude Code.
2. **Install `/priority` for every project**, not only this repo:
   `mkdir -p ~/.claude/skills && cp -R .claude/skills/priority ~/.claude/skills/`
3. **Add Context7**, which is needed for library docs:
   `claude mcp add --transport http --scope user context7 https://mcp.context7.com/mcp`
   An API key from context7.com raises the rate limits. If the developer has one, add it as a header. Then check the server with `/mcp`.
4. **Install the tools:** `git`, `gh`, `uv` and `python3`. `jq` is optional, because the hook falls back to `python3`. With Homebrew: `brew install gh uv jq`. The developer then runs `! gh auth login`.
5. **Re-decide how PostgreSQL 18 runs.** The spec says "Podman, already installed", which was true on Fedora but not on macOS. Grill this one decision with the developer before ticket 02, then record it in the README decision log. The options are:
   - Podman: `brew install podman`, then `podman machine init` and `podman machine start`;
   - Docker Desktop or OrbStack;
   - Postgres.app, or `brew install postgresql@18`.
6. **Check the push guard:** `bash .claude/hooks/test-block-push-to-main.sh` should end with "All hook tests passed".

## Next steps, in order

1-4. **Done on 2026-10-22.** The worktree and branch `pr-1-service-skeleton` exist, ticket 01's wizard was run, tickets 02 to 04 are built, and the code-review fixes are committed.
5. **Close PR 1.** Open it with the `pr` skill, and the developer squash-merges it. *(Changed on 2026-10-22: the teach-and-quiz moved to the last PR. See "Definition of done" in `CLAUDE.md`.)*
6. **Start PR 2**, the first Architecture, with "The flow for every PR" in `CLAUDE.md`. The open decisions are under Out of Scope in the PR 1 spec, and the facts are in `docs/research/pydantic-ai.md`.

## Suggested skills

- `/mattpocock-skills:grill-with-docs`, which runs `grilling` and `domain-modeling`: step 2 of the flow for PR 2.
- `wizard`: for any step only the developer can do, such as an API key.
- `tdd` and `mattpocock-skills:code-review`: they run inside `/mattpocock-skills:implement-spec`, step 5 of the flow.
- `pr`: when opening a PR.
- `research`: for any new facts. Save the results under `docs/research/`.
- **Only the developer can type these:**
  - `/mattpocock-skills:grill-with-docs`
  - `/mattpocock-skills:to-spec`
  - `/mattpocock-skills:to-tickets`
  - `/mattpocock-skills:implement-spec <spec file>`
  - `/mattpocock-skills:ask-matt`, which tells you which skill fits
  - `/priority`

## Gotchas

- **`/priority` depends on the transcript format.** It reads Claude Code's session transcript, whose format is internal and can change between versions. If `/priority` reports "format not recognised", it still works from context. Fix `scripts/collect_outputs.py` when that happens.
- **Old Matt Pocock material uses old names.** Older videos and articles say `/grill-me`, `/to-prd` and `/to-issues`, where the current names are `/grill-with-docs`, `/to-spec` and `/to-tickets`. The recommended video is "mattpocock/skills: A complete AI Coding workflow, end-to-end", https://www.youtube.com/watch?v=M6mYodf0dJM. Start at 6:52.
- **Check model limits before choosing models in PR 2.** Free OpenRouter models allow only 50 requests a day without $10 of credit (see the research notes).
- **The developer can't approve their own PR.** GitHub does not let a PR's author approve it, so merging is enough.
