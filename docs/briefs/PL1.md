# Project brief: PL1 (PlaygroundBugLogger)

## What it is
Your own **test** project (Playground), where you do have permission to create
tickets. It's for **testing the tool without cluttering SK8**.

## Business impact
- It's the **safety net** for distribution: before using the Bug Logger against
  the real project, the whole flow (login → fields → AI → submit →
  attachments) is validated here with no risk.
- It lets you teach the tool to new people and run demos without creating noise in the
  real backlog.

## How it learns (ML)
Like any project: it saves its own examples in
`%APPDATA%\MacondoLogger\buglogger_examples_PL1.json`. Since it's a test project, the style it
learns does **not** affect SK8's (each project learns separately).

## Maintenance
- Keep it alive while the tool keeps evolving: it's where every
  change is tested before releasing it to the team.
- If it fills up with test tickets, they can be closed/deleted with no consequences.
- When you want to validate a new version of the `.exe` "end to end": create a
  bug with an attachment here and confirm it reaches JaaS correctly.

## Recommended use during distribution
First test on every new PC: connect, open PL1, log a test bug with a
screenshot. If that works, SK8 will work too.
