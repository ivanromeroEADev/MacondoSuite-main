# Project brief: F1 (Formula 1, future onboarding)

> Sample brief for when **another franchise** adopts Macondo. F1 is just the illustrative
> case; it applies the same way to any new team.

## What changes when a new franchise joins
**Almost nothing**, and that's the point. The tool is multi-project by design:

1. The F1 tester opens the same `MacondoLogger.exe` (or the Suite).
2. They connect with **their** JaaS token.
3. **F1** shows up in the project list because the app reads their **real permissions**;
   they choose F1 and that's it.
4. F1's fields are read from the API (F1's, not skate's).

There's no need to build an "F1 version" or touch any code.

## Business impact
- Shows the investment scales: the same executable serves several franchises,
  with a marginal cost close to zero per new team.
- A **shared bug-quality standard across teams**, while keeping each game's own
  style.

## How it learns (ML) from scratch
- F1 starts **without examples of its own**: meanwhile, the app uses a neutral base style.
- As the F1 tester corrects summaries/descriptions, F1 builds up **its own**
  examples file (`buglogger_examples_F1.json`), separate from skate's.
- Within a few weeks, the AI writes in F1's style.

## Maintenance
- Nothing code-specific. Just make sure the F1 team has **Create Issue**
  permissions in their project.
- If F1 uses time logging with the same `Time Tracking` convention, the WorkLogger
  works for them by only changing the project key on the screen.

## Checklist for onboarding a new franchise
- [ ] The team has a project in JaaS and create permissions.
- [ ] Share the `.exe` (or point to the network folder where it lives).
- [ ] Each PC: Groq key once + JaaS token.
- [ ] A first test bug in their project (or in PL1) to validate the flow.
- [ ] (Optional) Adjust the time-logging project key if they use the WorkLogger.
