# Macondo Suite: Overview, distribution and maintenance

## What it is

Two QA tools that talk to JaaS (EA's Jira), with the same visual identity
(🦋 mustard). They're distributed as three executables, depending on what each person needs:

| Executable | Contains | For whom |
|---|---|---|
| `MacondoLogger.exe` | Bug Logger with AI | Testers who only log bugs |
| `MacondoWorkLogger.exe` | Time logging | People who only log time |
| `MacondoSuite.exe` | Both, in tabs | A skate tester's day-to-day |

Everything runs **locally**: each `.exe` starts a server on `localhost` and opens the
browser. The tool has no backend and no data in the cloud.

## Business impact (summary)

- **Bug Logger:** turns a loose note into a complete, well-structured ticket
  in seconds. Less time per bug, a consistent format across testers, and a shorter
  learning curve for new people. It scales to other franchises without rewriting
  anything: each project learns its own style.
- **WorkLogger:** removes logging time hour by hour, ticket by ticket, by hand in JaaS.
  It logs a whole period (several days, several activities) in a single pass,
  with the ticket IDs fetched fresh from the API.

*(The impact per project is in each brief: SK8, PL1, FCQV, F1.)*

## Architecture (why a single codebase)

```
core.py              ← shared core: JaaS, Groq, ML, credentials (Bug Logger)
worklogger_core.py   ← time-logging logic (uses core for the connection)
macondo_theme.py     ← the mustard palette, in one place
macondo_login.py     ← reusable connection screen
bug_logger_ui.py     ← Bug Logger screen  (render)
worklogger_ui.py     ← WorkLogger screen  (render)
macondo_app.py / worklogger_app.py / macondo_suite_app.py  ← the three apps
```

A fix in the logic (e.g. a change in how JaaS responds) is made **once** in
the core and works for all three executables.

## Authentication today and tomorrow

- **Today:** each person uses their **JaaS PAT Token**, which is stored **encrypted** in
  the Windows Credential Manager (keyring), per Windows user. The
  projects each person sees come from their **real permissions** in JaaS, filtered by
  their account (EA email). Nobody sees or uses anyone else's token.
- **Tomorrow (recommended):** login with the **EA user via SSO/OAuth**. That requires
  JaaS/EA to register the app as an OAuth client. Until that exists, PAT + keyring
  is the viable and secure option. The code already isolates the connection in `core.py` and
  `macondo_login.py`, so moving to OAuth only means changing that layer.

## Security

- Tokens and the Groq key: **encrypted** in keyring, never in plain text on disk.
- **Critical to-do:** the PAT that showed up in plain text in an uploaded file must be
  considered compromised: **rotate it in JaaS**.
- The Groq key only generates text (it doesn't identify anyone), but it's still encrypted and
  shouldn't be pasted in chats.

## Distribution

1. Build on a Windows PC with `build_all.bat` (see [`BUILD_EXE.md`](../BUILD_EXE.md)).
2. Share the `.exe` file(s) through the internal channel (network folder, Teams, etc.).
3. **First launch:** SmartScreen/Defender may warn because the `.exe` isn't
   signed → *More info → Run anyway*.
   - For wide distribution it's worth **signing the `.exe`** with an EA certificate
     (removes the warning). It's the recommended step before going from a pilot to the whole
     team.
4. Each PC sets up its Groq key (Bug Logger) and its JaaS token once.

## Maintenance (general)

| How often | What to check |
|---|---|
| When Groq changes models | `GROQ_MODEL` in `core.py` (currently `openai/gpt-oss-120b`). |
| If JaaS changes a project's fields | Nothing in the code: the app reads the fields from the API. Only check if a new field type shows up that the UI can't draw. |
| For each new skate version | Nothing: the WorkLogger fetches the versions fresh from the API. |
| Token rotation | According to EA policy; the PAT is pasted again once. |
| Dependencies | `requirements.txt` without pinned versions; if something breaks, pin the version that worked. |

The **per-project** maintenance details are in each brief.
