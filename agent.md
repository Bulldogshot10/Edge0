# Agent Instructions

Read this file before doing any work in this repository. Then read `goal.md`, the relevant README/docs, and the actual source and tests for the task.

## Branch discipline
- **Never create a new branch unless the user explicitly asks for one.**
- Work in the branch the user selected or the current working branch. Do not move work to another branch, rename branches, merge branches, open pull requests, or delete branches unless explicitly requested.
- A feature request does not imply permission to create a branch. Make the change directly on the requested/current branch.
- Do not use `main` for work when the user explicitly names another branch.

## Feature inventory and handoff
- Keep `goal.md` as the living project status and handoff document.
- Track the features and requirements that matter to the project, with explicit statuses: **Implemented**, **Partial**, **Not implemented**, **Blocked**, or **Needs verification**.
- Base status on source code, tests, build output, CI, and device testing where applicable. A README or a planned API alone is not proof that a feature works.
- When a task changes functionality, update `goal.md` in the same set of changes. Record what changed, what remains, the relevant files, validation performed, failures, and clear next steps for the next agent.
- Never mark a feature complete just because code was added. Distinguish compiling, automated-test coverage, and successful runtime/device validation.
- If source, tests, README, CI, and `goal.md` disagree, inspect and reconcile the discrepancy rather than silently picking whichever claim looks most complete.

## Implementation workflow
- Inspect the current branch, worktree context, repository structure, related implementation, and existing tests before editing.
- Preserve unrelated user changes. Avoid broad rewrites and unrelated cleanup.
- Follow the architecture the user actually requested. Do not add a second/legacy backend or fallback architecture when the request calls for a full replacement.
- Use the repository's real build and test commands. Investigate failures from their actual logs; do not guess or report a failed build as successful.
- Before handing off, summarize the changed files, feature-status updates, tests/builds run and their exact outcomes, remaining blockers, and the next concrete action.
