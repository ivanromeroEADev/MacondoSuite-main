# 🦋 Macondo Suite

<img src="macondo_logo.jpg" width="110" align="right" alt="Yellow butterfly, the Macondo logo">

**Macondo Suite is a small set of QA tools for JaaS (EA's Jira).** It runs on your own computer and has two tools:

- **Macondo Logger**: you describe a bug in your own words, and it drafts a properly structured JaaS ticket for you to review, edit and submit.
- **Macondo WorkLogger**: you log your hours for a whole week (every day, every activity) on one screen, instead of opening ticket after ticket in JaaS.

You can use them separately or together in one app, **Macondo Suite**, with one tab for each.

The name comes from *One Hundred Years of Solitude*, hence the yellow butterfly.

## Contents

1. [Why it exists](#why-it-exists)
2. [Business impact](#business-impact)
3. [What you need](#what-you-need)
4. [Installation, step by step](#installation-step-by-step)
5. [First launch](#first-launch)
6. [How to use Macondo Logger](#how-to-use-macondo-logger)
7. [How to use Macondo WorkLogger](#how-to-use-macondo-worklogger)
8. [How the Logger learns](#how-the-logger-learns)
9. [Troubleshooting](#troubleshooting)
10. [For maintainers](#for-maintainers)

## Why it exists

Two everyday QA tasks in JaaS take more time than they should.

**Logging a bug.** A good bug report needs a clear summary that follows the project's naming convention, a short description, repro steps, player impact and notes, plus every required field the project asks for. The bug itself often fits in one sentence, but writing it up properly can take a long time, and every tester writes it a little differently.

**Logging hours.** Time is logged on "Time Tracking" tickets, one ticket per activity. Logging a week means opening many tickets and entering the time one by one, and it's easy to skip a day or log against an old version's ticket.

## Business impact

**Macondo Logger**
- **Consistency.** Every bug starts from the same QA structure (description, repro steps, player impact, notes), so tickets read the same no matter who wrote them. That means less back-and-forth between QV and developers.
- **Faster onboarding.** A new tester gets the team's format "out of the box" instead of learning it ticket by ticket.
- **No missed required fields.** The app reads each project's create screen from JaaS and shows exactly the fields that project needs.
- **Gets better with use.** It learns from each project's real tickets and from the tester's corrections, so drafts get closer to each team's style over time.
- **Works for any project.** It isn't tied to one game: anyone with JaaS access can pick their own project.
- **The tester stays in control.** Nothing is sent to JaaS until the tester has reviewed and confirmed it.

**Macondo WorkLogger**
- **A whole period in one pass.** Several days × several activities on a single screen, then one button sends everything.
- **Always the current tickets.** Versions and activity tickets are fetched fresh from JaaS every time, so nobody logs against an outdated ticket.
- **Fewer mistakes.** Each day shows how close it is to 8 hours, and you review a summary before sending.

**Measuring it honestly.** The time saved hasn't been formally measured yet. The Logger records its own **accuracy** (the share of tickets sent without rewriting the AI draft) for each project. The fairest way to evaluate the suite is a short pilot: a few testers log the same bugs both ways, the time is recorded, and a lead reviews the tickets against QV standards.

## What you need

- **A Windows 10 or 11 computer.**
- **Access to JaaS** ([jaas.ea.com](https://jaas.ea.com)) with permission to create tickets in your project. If you can open JaaS in your browser from this computer, you're fine.
- **Your own JaaS Personal Access Token (PAT).** Everyone uses their own, so every ticket and worklog is created under their name. How to create one is explained below.
- **A Groq API key** (only for Macondo Logger). Groq is the service that runs the AI that writes the drafts. It's free to create, and the free plan is enough for daily use.
- **About 15 minutes** for the first installation.

> **About data leaving EA:** to write a draft, Macondo Logger sends your bug description and a few recent tickets from your project to Groq, as format examples. Check with your lead that this is allowed for your project before using it on real work. The WorkLogger doesn't use AI and only talks to JaaS.

## Installation, step by step

### Step 1. Install Python

Macondo is written in Python, so your computer needs it.

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest version for Windows.
2. Open the installer.
3. **Important:** on the first screen, check the box **"Add python.exe to PATH"**. If you skip this, Windows won't find Python and nothing else will work.
4. Click **Install Now** and wait until it finishes.

To check it worked, open a terminal (press the **Windows key**, type `cmd`, press **Enter**) and type:

```
python --version
```

If you see something like `Python 3.12.4`, you're ready. If it says the command isn't recognized, uninstall Python and install it again, this time checking the PATH box.

### Step 2. Download Macondo Suite

1. On this repository's page on GitHub, click the green **Code** button.
2. Click **Download ZIP**.
3. Open your **Downloads** folder, right-click the ZIP and choose **Extract All…**.
4. Move the extracted folder somewhere easy to find, for example `Documents\MacondoSuite`.

(If you use git, you can also `git clone` the repository.)

### Step 3. Create your JaaS token (PAT)

1. Open [jaas.ea.com](https://jaas.ea.com) and sign in.
2. Click your profile picture (top right) → **Profile**.
3. Go to **Personal Access Tokens** → **Create token**.
4. Give it a name, like `Macondo`, and create it.
5. **Copy the token right away** and keep it somewhere safe for a minute. JaaS only shows it once.

Treat this token like a password: don't paste it in chats, emails or files you'll share.

### Step 4. Create your Groq API key (Macondo Logger only)

1. Go to [console.groq.com/keys](https://console.groq.com/keys) and sign up or sign in.
2. Click **Create API Key**, give it a name and copy it.

If you'll only use the WorkLogger, you can skip this step.

### Step 5. Open the app

In the Macondo Suite folder, double-click:

| File | Opens |
|---|---|
| **`run_suite.bat`** | Macondo Suite: both tools, in tabs (recommended) |
| `run_macondo.bat` | Macondo Logger only |
| `run_worklogger.bat` | Macondo WorkLogger only (no Groq key needed) |

A black window opens. **The first time, it installs what the app needs, which takes a few minutes.** After that it starts in seconds. When it's ready, the app opens in your browser on its own. If it doesn't, go to [http://localhost:8501](http://localhost:8501).

**Keep the black window open while you use the app.** Closing it closes the app.

If Windows shows *"Windows protected your PC"*, click **More info → Run anyway**. It appears because the file isn't digitally signed.

## First launch

1. **Paste your Groq API key** and click **Save Groq API Key**. It's only asked once per computer.
2. **Paste your JaaS PAT**, leave **Remember on this computer** checked, and click **Connect**.

Both keys are stored **encrypted** in the Windows Credential Manager (under the name `sk8-buglogger`), never in a text file. Next time you open the app, it remembers them. To remove your token, click **Forget token** on the connection screen.

## How to use Macondo Logger

1. **Choose your project.** You'll only see projects where you're allowed to create bugs. The ones you used recently and the ones you lead come first. If yours isn't there, type its key under *Don't see your project?*
2. **Fill in the fields.** The form shows only the fields your project has on its create screen. Required ones are marked with `*`. Fields specific to your project also appear, and the less common optional ones are under *Other fields*.
3. **Fill in "Feature"** (for example, *Challenges*). It goes into the notes of the description.
4. **Describe the bug** the way you'd tell a teammate: what happens, where, and what you expected instead. You can attach logs and videos, or paste a screenshot with **Ctrl+V**.
5. **Click "Generate with AI".** In a few seconds you get a summary and a description with repro steps, player impact and notes.
6. **Review and edit.** Everything is editable. Whatever you change here is what the app learns from.
7. **Click "Confirm and send".** The ticket is created in JaaS, the attachments are uploaded, and you get a link to open it.

If JaaS rejects an optional field, the app removes it, creates the ticket anyway and tells you which field couldn't be applied.

## How to use Macondo WorkLogger

1. Open the **WorkLogger** tab in Macondo Suite.
2. **Time-tracking project:** it comes set to `FCQV` (skate). Other teams type their own project key.
3. Click **Load versions**. The app fetches the current "Time Tracking" tickets from JaaS.
4. **Choose the version** and the **date range** (*From* / *To*). Only business days, Monday to Friday, are included.
5. Click **Prepare days**. You'll see every day, each with every activity.
6. **Type the time** for each activity. Accepted formats: `2h`, `1h 30m`, `45m` or `1.5h`. Leave it empty for activities you didn't do. Nothing reloads while you type.
7. Click **Save and review** to see the summary per day and the grand total.
8. Click **Send worklogs to JaaS**. You'll see which entries were logged and which, if any, failed.

Each worklog starts at 09:00 on its day (JaaS needs a start time), and its comment is the activity name.

## How the Logger learns

Macondo Logger doesn't train its own AI model. Every time it writes a draft, it gives the AI a few real examples of how bugs are written **in your project**, and the AI follows that format. What improves with use are those examples. This is called *few-shot learning*.

The examples come from, in order of priority:

1. **Your corrections in that project.** When you edit a draft before sending it, your corrected version is saved and used for the next drafts. If you send the draft untouched, nothing is saved.
2. **Real recent bugs from the project in JaaS.** Your own first; if you have none, the team's. They're read every time you open the project and aren't stored on disk.
3. **A base skate style**, only if the project has neither of the above yet.

Each project learns separately: corrections in SK8 don't affect another project.

**Where it's stored.** On your computer, in `%APPDATA%\MacondoLogger\` (paste that into the File Explorer address bar to get there):

- `buglogger_examples_<PROJECT>.json`: your corrections for that project.
- `buglogger_stats_<PROJECT>.json`: that project's metrics: drafts generated, tickets sent, how many were corrected and how similar the draft was to what you sent.

The form shows the **accuracy** for each project (the share of tickets sent without rewriting). If it goes up over time, the app is learning the project's style. To start a project from scratch, delete its `buglogger_examples_<PROJECT>.json`.

## Troubleshooting

**"Python not found" or "python is not recognized"**
Python isn't on the PATH. Reinstall it and check **Add python.exe to PATH**.

**"streamlit is not recognized"**
Use `python -m streamlit run macondo_suite_app.py` instead of `streamlit run …`. The `.bat` files already do this.

**"Invalid token"**
Check that you copied the whole PAT and that it hasn't expired. If it still fails, create a new one.

**My project doesn't appear**
Type its key under *Don't see your project?* If the app says it can't read the fields, you probably don't have permission to create tickets there. Ask your lead.

**"This project requires fields the app can't fill in yet"**
Your project has a required field of an unusual type. Create that ticket directly in JaaS and let the maintainer know which field it was.

**The WorkLogger finds no versions**
Check the project key, and that the project uses "Time Tracking" tickets with the naming convention described in [`docs/briefs/FCQV.md`](docs/briefs/FCQV.md).

**Groq error mentioning the model (`model_decommissioned` or `model_not_found`)**
Groq retires models from time to time. A maintainer needs to update `GROQ_MODEL` in `core.py` with a current model from [console.groq.com/docs/models](https://console.groq.com/docs/models).

**Port 8501 is already in use**
Another Macondo window is already open. Use that one, or close it first.

## For maintainers

### Project structure

```
MacondoSuite/
├── README.md                  this guide
├── run_suite.bat              opens Macondo Suite (both tools) without building
├── run_macondo.bat            opens Macondo Logger only, without building
├── run_worklogger.bat         opens the WorkLogger only, without building
├── requirements.txt           Python libraries the app needs
│
├── macondo_suite_app.py       app: both tools in tabs
├── macondo_app.py             app: Macondo Logger only
├── worklogger_app.py          app: WorkLogger only
│
├── core.py                    Logger core: JaaS, Groq, learning, credentials
├── bug_logger_ui.py           Logger screens
├── worklogger_core.py         WorkLogger logic (versions, activities, time parsing)
├── worklogger_ui.py           WorkLogger screens
├── macondo_login.py           shared connection screen
├── macondo_theme.py           colors, fonts and header
├── macondo_logo.jpg
│
├── build_all.bat              builds the three .exe files
├── build_macondo.bat · build_worklogger.bat · build_suite.bat
├── *.spec                     PyInstaller recipes for each .exe
├── launcher_*.py · _launcher_base.py   startup code for the .exe files
│
├── test_suite.py              automated tests (simulated JaaS, no network)
└── docs/
    ├── BUILD_EXE.md           how to build and share the .exe files
    └── briefs/                overview, distribution, and one brief per project
```

### Run from the command line

```
python -m pip install -r requirements.txt
python -m streamlit run macondo_suite_app.py
```

Use `macondo_app.py` or `worklogger_app.py` instead for the standalone tools.

### Run the tests

```
python -m pip install pytest
python -m pytest test_suite.py -q
```

### Build .exe files for people without Python

See [`docs/BUILD_EXE.md`](docs/BUILD_EXE.md). In short: double-click `build_all.bat`, and the three `.exe` files appear in `dist\`.

### More documentation

- [`docs/briefs/00_Overview_and_Distribution.md`](docs/briefs/00_Overview_and_Distribution.md): architecture, security, distribution and maintenance.
- One brief per project: [`SK8`](docs/briefs/SK8.md) · [`PL1`](docs/briefs/PL1.md) · [`FCQV`](docs/briefs/FCQV.md) · [`F1 (future onboarding)`](docs/briefs/F1_future.md).

### Before distributing widely

- **Rotate any JaaS PAT** that was ever exposed in plain text.
- Validate a real ticket in **PL1** (a bug with an attachment) from the built `.exe`.
- **Sign the `.exe` files** with an EA certificate to avoid the SmartScreen warning.

Created by Iván Romero · QV, Skate · Bogotá.
