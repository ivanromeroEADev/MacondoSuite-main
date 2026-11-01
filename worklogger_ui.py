"""
WorkLogger screens.

render() is used on its own (worklogger_app.py) or as a tab (macondo_suite_app.py).

Stages, kept in st.session_state["wl_stage"]:
  setup: pick the project, load versions, pick a version and dates
  log:   type the hours per day and activity, review, send

All the day inputs live inside one st.form, so typing doesn't rerun the page
and the scroll doesn't jump back to the first day.
"""

from datetime import date

import streamlit as st

import worklogger_core as wl


# State

def _init_state():
    defaults = {
        "wl_stage": "setup",
        "wl_project": wl.DEFAULT_PROJECT,
        "wl_project_resolved": wl.DEFAULT_PROJECT,  # the already normalized (UPPERCASE) project that was queried
        "wl_versions": None,     # list of detected versions, or None if not loaded yet
        "wl_all_issues": None,   # raw JaaS tickets (to slice the activities per version)
        "wl_version_index": 0,
        "wl_activities": {},     # {activity: ticket_key} for the chosen version
        "wl_workdays": [],       # list of dates (business days in the range)
        "wl_results": None,      # results of the last submission, or None
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _input_key(day, activity):
    """Widget key for one activity on one day."""
    return f"wl_in::{day.isoformat()}::{activity}"


# Stage: setup (project, version and dates)

def _load_versions():
    """Fetches the project's tickets from JaaS and detects the available versions."""
    # Normalized in a separate variable: Streamlit doesn't allow changing a widget's value after it's drawn.
    project = (st.session_state.get("wl_project") or wl.DEFAULT_PROJECT).strip().upper() or wl.DEFAULT_PROJECT
    with st.spinner(f"Fetching versions of {project} from JaaS..."):
        all_issues = wl.fetch_all_issues(st.session_state.jaas_token, project)
        versions = wl.find_available_versions(all_issues)
    st.session_state.wl_all_issues = all_issues
    st.session_state.wl_versions = versions
    st.session_state.wl_project_resolved = project  # to show it later without touching the widget


def _stage_setup():
    st.caption(f"connected as {st.session_state.user_display_name}")
    st.subheader("Version and dates")

    # Project
    col_p, col_btn = st.columns([2, 1])
    col_p.text_input(
        "Time-tracking project",
        key="wl_project",
        help="FCQV for skate. Other teams enter their own project here.",
    )
    with col_btn:
        st.markdown("<div style='height:1.8em'></div>", unsafe_allow_html=True)  # lines the button up with the input
        if st.button("Load versions", type="primary", key="wl_btn_load"):
            _load_versions()
            st.rerun()

    versions = st.session_state.wl_versions
    if versions is None:
        st.info("Enter the project and press **Load versions** to fetch the current tickets from JaaS.")
        return

    if not versions:
        st.error(
            f"Couldn't find any 'Time Tracking' versions in {st.session_state.wl_project_resolved}. "
            "Check that the project is right and that you have access to those tickets."
        )
        return

    # Version
    labels = [f"v{v['label']}  ({v['key']})" for v in versions[:10]]  # the 10 most recent
    chosen_label = st.selectbox("Version", labels, key="wl_version_label")
    st.session_state.wl_version_index = labels.index(chosen_label)

    # Date range
    today = date.today()
    col_a, col_b = st.columns(2)
    start = col_a.date_input("From", value=today, key="wl_start")
    end = col_b.date_input("To", value=today, key="wl_end")

    if start > end:
        st.warning("The 'From' date is after the 'To' date.")
        return

    workdays = wl.get_workdays(start, end)
    if not workdays:
        st.warning("There are no business days (Monday to Friday) in that range.")
        return
    st.caption(f"{len(workdays)} business day(s): " + ", ".join(d.strftime("%a %d/%m") for d in workdays))

    if st.button("Prepare days", type="primary", key="wl_btn_prepare"):
        activities = wl.activities_for_version(
            st.session_state.wl_all_issues, versions, st.session_state.wl_version_index
        )
        if not activities:
            st.error("That version has no activities to log.")
            return
        st.session_state.wl_activities = activities
        st.session_state.wl_workdays = workdays
        st.session_state.wl_results = None
        # We clear any hours from a previous period.
        for key in [k for k in st.session_state if str(k).startswith("wl_in::")]:
            del st.session_state[key]
        st.session_state.wl_stage = "log"
        st.rerun()


# Stage: logging hours (every day visible at once)

def _render_day_inputs():
    """Draws, inside the form, each day with its activities and a time input."""
    for day in st.session_state.wl_workdays:
        st.divider()
        # Day total according to what was saved in the last 'Save and review'.
        day_minutes = _day_minutes_from_state(day)
        title = f"**{day.strftime('%A %d/%m/%Y')}**: "
        if day_minutes == wl.WORKDAY_MINUTES:
            title += f"✅ {wl.format_minutes(day_minutes)} / 8h"
        elif day_minutes:
            title += f"{wl.format_minutes(day_minutes)} / 8h"
        else:
            title += "nothing logged"
        st.markdown(title)

        for activity in st.session_state.wl_activities:
            col_name, col_time = st.columns([3, 1])
            col_name.markdown(activity)
            col_time.text_input(
                "time",
                key=_input_key(day, activity),
                label_visibility="collapsed",
                placeholder="2h",
            )


def _day_minutes_from_state(day):
    """Adds up the minutes typed for a day, reading the current value of each input."""
    total = 0
    for activity in st.session_state.wl_activities:
        _, minutes = wl.parse_time(st.session_state.get(_input_key(day, activity), ""))
        total += minutes
    return total


def _collect_entries_from_state():
    """Builds the list of entries with time, reading the current value of each input."""
    entries = []
    for day in st.session_state.wl_workdays:
        for activity, ticket_key in st.session_state.wl_activities.items():
            time_str, minutes = wl.parse_time(st.session_state.get(_input_key(day, activity), ""))
            if minutes > 0:
                entries.append({
                    "day": day, "activity": activity, "ticket": ticket_key,
                    "time": time_str, "minutes": minutes,
                })
    return entries


def _submit_entries(entries):
    """Sends each worklog to JaaS and saves the results to show them."""
    results = []
    progress = st.progress(0.0)
    for i, entry in enumerate(entries, 1):
        ok, error = wl.submit_worklog(
            st.session_state.jaas_token,
            entry["ticket"],
            entry["time"],
            entry["day"],
            entry["activity"],  # the worklog comment is the activity name
        )
        results.append({**entry, "ok": ok, "error": error})
        progress.progress(i / len(entries))
    progress.empty()
    st.session_state.wl_results = results


def _stage_log():
    activities = st.session_state.wl_activities
    workdays = st.session_state.wl_workdays

    # Top bar
    top_a, top_b = st.columns([3, 1.4])
    top_a.caption(f"connected as {st.session_state.user_display_name}")
    if top_b.button("Change version / dates", key="wl_btn_back"):
        st.session_state.wl_stage = "setup"
        st.rerun()

    version = st.session_state.wl_versions[st.session_state.wl_version_index]
    st.markdown(f"### {st.session_state.wl_project_resolved} · v{version['label']}")
    st.caption(
        f"{len(activities)} activity(ies) · {len(workdays)} day(s). "
        "Type the time per activity (2h · 1h 30m · 45m · 1.5h) and press **Save and review**. "
        "While you type inside the form, nothing reloads or jumps."
    )

    # Form: all the days together, no reloads while typing
    with st.form("wl_log_form"):
        _render_day_inputs()
        st.divider()
        st.form_submit_button("Save and review", type="primary")

    # Summary + submission (outside the form)
    entries = _collect_entries_from_state()
    st.subheader("Summary")
    if not entries:
        st.info("Type the hours above and press **Save and review** to see the summary.")
        return

    grand_total = sum(e["minutes"] for e in entries)
    current_day = None
    for entry in entries:
        if entry["day"] != current_day:
            current_day = entry["day"]
            day_total = sum(e["minutes"] for e in entries if e["day"] == current_day)
            st.markdown(f"**{current_day.strftime('%A %d/%m')}**: {wl.format_minutes(day_total)}")
        st.caption(f"　{entry['ticket']} · {entry['activity']} → {entry['time']}")
    st.markdown(f"**Grand total: {wl.format_minutes(grand_total)} in {len(entries)} entry(ies)**")

    if st.button("Send worklogs to JaaS", type="primary", key="wl_btn_submit"):
        _submit_entries(entries)
        st.rerun()


# Submission results

def _show_results():
    results = st.session_state.wl_results
    ok_count = sum(1 for r in results if r["ok"])
    fail_count = len(results) - ok_count

    if fail_count == 0:
        st.success(f"Done: {ok_count} worklog(s) logged successfully.")
    else:
        st.warning(f"{ok_count} logged, {fail_count} failed. Check the failed ones below.")

    for r in results:
        line = f"{r['day'].strftime('%d/%m')} · {r['activity']} → {r['time']}"
        if r["ok"]:
            st.caption(f"✅ {line}")
        else:
            st.caption(f"❌ {line}: {r['error']}")

    col1, col2 = st.columns(2)
    if col1.button("Log another period", key="wl_btn_new_period"):
        st.session_state.wl_results = None
        st.session_state.wl_stage = "setup"
        st.rerun()
    if col2.button("Back to logging", key="wl_btn_back_to_log"):
        st.session_state.wl_results = None
        st.rerun()


# Entry point

def render():
    """Draws the WorkLogger. Assumes there's already a session (see macondo_login)."""
    _init_state()

    # If we just sent, we show the results above everything else.
    if st.session_state.wl_results is not None:
        _show_results()
        return

    if st.session_state.wl_stage == "setup":
        _stage_setup()
    else:
        _stage_log()
