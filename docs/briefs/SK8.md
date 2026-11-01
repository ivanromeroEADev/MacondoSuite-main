# Project brief: SK8 (skate.)

## What it is
The skate team's **real** project in JaaS. It's the project where the game's real
bugs are logged. The tool that applies here is the **Bug Logger**.

## Business impact
- It's Macondo's **main use case**. Every well-written, consistent bug
  saves back-and-forth between QA and development.
- The AI component learns **SK8's own style** (summaries, repro steps
  structure, Note sections) from the project's real tickets and from
  your corrections, so quality goes up with use.
- It lowers the entry curve for new testers on the team: the right format comes
  "out of the box".

## How it learns (ML)
1. **Your corrections** in SK8 (the most faithful): every time you edit the summary or the
   description in the preview and send it, it's saved as an example for SK8.
2. **Recent real tickets** from SK8 in JaaS (the franchise's structure).
3. If there's none of the above, a skate **base style** as a starting point.

The learned examples are saved in `%APPDATA%\MacondoLogger\buglogger_examples_SK8.json`
(they survive `.exe` updates and can be backed up).

## Fields
They're read **from the API** from SK8's create screen (Pillar, Game Spine, Platform,
Repro Rate, Player Impact, Severity, Player Path, Activity, Changelist, Branch, Bug Type,
and any other field the project has enabled). Nothing is "hardcoded" per version.

## Maintenance
- **Careful when sending:** it's the real project. The app shows a warning in the preview before
  confirming in SK8.
- If the team adds a new required field, the app detects it and asks for it on its own;
  code would only need to change if it were a field type the UI can't draw yet.
- Check now and then that the examples file doesn't grow with bad corrections
  (if someone "taught" a wrong format, that JSON can be deleted and it learns
  again).

## Risks / notes
- The tester needs **Create Issue** permission in SK8 (normal on the team).
- Attachments (logs, video, screenshots) are uploaded to the already created ticket.
