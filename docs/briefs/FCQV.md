# Project brief: FCQV (time logging)

## What it is
The JaaS project where the skate team **logs its time**. The tool that
applies here is the **WorkLogger** (not the Bug Logger). Logging is organized in
"Time Tracking" tickets.

## How it's organized in JaaS
- One **"parent" ticket per version**, with a summary like `Time Tracking 0.31.5`
  (no brackets).
- Under it, one **"child" ticket per activity**, with the summary in brackets, like
  `[QA][Time Tracking] Regression - San Van`.
- The WorkLogger reads all of this **from the API**, detects the versions and pulls the activities
  of the version you choose. It always fetches what's current: there are no fixed lists in the code.

## Business impact
- Removes the manual work of opening each ticket and logging hour by hour. A
  **whole period** (several days × several activities) is logged on a single screen.
- Fewer logging mistakes and skipped days; it flags when a day reaches 8h.
- Much faster week/period close.

## Maintenance
- **Naming convention:** the WorkLogger relies on parents saying
  `Time Tracking <version>` without brackets and children having brackets. If the team
  changes that convention, the pattern in `worklogger_core.py` has to be adjusted
  (`find_available_versions` / `_clean_activity_label`).
- **Other teams:** the project can be configured in the app itself (the "Time-tracking
  project" field, FCQV by default). A new team with the same convention only
  changes the project key; no code is touched.
- The start time of each worklog is set to 09:00 on that day (JaaS requires one). If
  another one were needed, it's in `submit_worklog`.

## Risks / notes
- The token needs permission to log time in FCQV.
- Each worklog's comment is the **activity name** (it matches the
  ticket), so it stays traceable.
