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

## Context-exhaustion checkpoint (mandatory)

When you judge that the available context is running low, you may soon lose important task details, you need to stop before the work is complete, or you cannot reliably continue without a fresh session, **do not end the session without creating a durable handoff in the root `goal.md`**.

Update `goal.md` before stopping. Add or refresh a clearly timestamped section such as **“Session checkpoint / handoff”** that records:

- **Current task and scope:** the user's exact requested outcome, what is in scope, what is explicitly out of scope, target repo/branch, and relevant constraints.
- **Progress and changed files:** what has been done, where it was done, and what remains in progress.
- **Feature inventory:** separate **Implemented**, **Partial**, **Unimplemented**, **Blocked**, and **Needs verification** items. Never mark something implemented just because code was written.
- **Bugs and errors:** observed bugs, exact failing commands/CI jobs and relevant error messages, suspected causes clearly labeled as hypotheses, and fixes attempted.
- **Validation:** commands/builds/tests/device checks actually run, their results, and checks not yet run. Never invent success or validation.
- **Next steps:** concise, ordered, actionable instructions for the next agent, including relevant paths, branch, dependencies, and known pitfalls.
- **Important notes and decisions:** architecture choices, user constraints, unresolved questions, and context that would otherwise be lost.

Keep the existing project goal and feature inventory intact; append or update the checkpoint rather than replacing useful project documentation with a session diary. Preserve earlier unresolved blockers until they are actually resolved.

After saving the checkpoint, **tell the user plainly that the current session is approaching context exhaustion and that it is time to start a new session**. Include the target repository/branch, point them to the root `goal.md`, and state the next concrete step. Do not claim that a new session has started. Do not wait until context is so low that the handoff can no longer be written.

## Before handing off

Whether stopping because of context exhaustion or finishing the requested task, summarize the files changed, feature statuses updated in `goal.md`, exact tests/builds performed and outcomes, unresolved blockers, and next steps. Make the repository's `goal.md` accurate for the next agent.

The detailed project instructions live in `agent.md`; the current feature inventory and continuation notes live in `goal.md`. Both files live in the repository root and must be read before implementation.
