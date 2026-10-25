# MANDATORY AI AGENT ENTRY POINT

**PRIORITY: READ THIS BEFORE DOING ANY WORK IN THIS REPOSITORY.**

This root `AGENTS.md` is the repository's agent-instruction entry point for coding agents that support `AGENTS.md` discovery, including Codex.

## Required reading order

Before planning or executing a task, changing files, running commands that modify state, or reporting a result:

1. Read this entire `AGENTS.md`.
2. Read the root `agent.md` for the project's mandatory workflow and branch rules.
3. Read the root `goal.md` for the project's goals, feature status, current limitations, and handoff notes.
4. Inspect the relevant source, tests, docs, and CI configuration before changing implementation.

Do not skip these files just because the user gives a short request or the task looks familiar. If one is missing or unreadable, say so and inspect the available project documentation before proceeding.

## Hard rules

- **NEVER create a branch unless the user explicitly asks you to create one.** A feature request is not permission to create a branch.
- Work on the branch the user selected or the current branch. Do not switch branches, merge, open a PR, delete branches, or push unrelated changes unless explicitly requested.
- **Keep `goal.md` updated in the same task whenever features, implementation status, tests, builds, known limitations, or blockers change.**
- Record implemented, partial, not implemented, blocked, or needs-verification status based on evidence. Code presence and README claims alone do not prove runtime success.
- Leave actionable handoff notes: what changed, relevant files, exact validation commands and outcomes, failures/blockers, and the next concrete steps.
- Inspect actual build/test/CI logs before diagnosing failures. Never claim a build, test, or device run passed unless it actually did.
- Follow the architecture the user explicitly requested. Do not reintroduce a second/legacy backend or fallback when the request specifies a full replacement.
- Preserve unrelated user changes and avoid unrelated rewrites.

## Before handing off

Summarize the files changed, feature statuses updated in `goal.md`, exact tests/builds performed and outcomes, unresolved blockers, and next steps. Make the repository's `goal.md` accurate for the next agent.

The detailed project instructions live in `agent.md`; the current feature inventory and continuation notes live in `goal.md`. Read both before implementation.
