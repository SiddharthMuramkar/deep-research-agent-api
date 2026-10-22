# 01: Set up Logfire

**What to build:** The developer has a Logfire account, a project for this service, and a write token saved as `LOGFIRE_TOKEN` in the git-ignored `.env` file. This lets the service send traces once tracing exists (ticket 04). Claude generates a `wizard` walkthrough and the developer follows it. This is the only human-only step in PR 1.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] A Logfire account and a project for this service exist.
- [x] A write token is saved as `LOGFIRE_TOKEN` in `.env`, and git does not track `.env`.
- [x] The wizard confirmed that the token is in place, and noted Logfire's current free-plan limits.

## Comments

- 2026-10-22: The developer ran `scripts/setup-logfire.sh` and marked this ticket done. Claude checked that `.env` holds a 55-character EU-region token and that git ignores `.env`. The first Run's trace then arrived in Logfire.
