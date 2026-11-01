"""
WorkLogger logic: no Streamlit here.

Fetches the "Time Tracking" tickets, finds the versions and their activities,
parses times like "1h 30m" and sends the worklogs. Login is reused from core.py.
"""

import re
import requests
from datetime import datetime, timedelta

import core  # shared core: token, connection and JaaS base URL

JAAS_URL = core.JAAS_URL

# Skate logs time in FCQV, on tickets with "Time Tracking" in the summary.
# Other teams change the project from the app.
DEFAULT_PROJECT = "FCQV"
DEFAULT_SUMMARY_MATCH = "Time Tracking"

# 8h, only used to show how full each day is.
WORKDAY_MINUTES = 480


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


# Fetch the project's tickets (always fresh from JaaS)

def fetch_all_issues(token, project=DEFAULT_PROJECT, summary_match=DEFAULT_SUMMARY_MATCH):
    """Every time-tracking ticket in the project, newest first. [] if JaaS fails."""
    jql = f'project={project} AND summary ~ "{summary_match}" ORDER BY created DESC'
    all_issues = []
    start_at = 0
    page_size = 100

    while True:
        params = {
            "jql": jql,
            "maxResults": page_size,
            "startAt": start_at,
            "fields": "summary,key,created",
        }
        try:
            res = requests.get(
                f"{JAAS_URL}/rest/api/2/search",
                headers=_headers(token),
                params=params,
                timeout=30,
            )
        except requests.RequestException:
            return []
        if res.status_code != 200:
            return []

        data = res.json()
        issues = data.get("issues", [])
        all_issues.extend(issues)

        # We stop once we have them all or the page came back incomplete.
        if len(all_issues) >= data.get("total", 0) or len(issues) < page_size:
            break
        start_at += page_size

    return all_issues


# versions and activities
#
# In FCQV, time logging is organized like this:
#   - One "parent" ticket per version, with a summary like "Time Tracking 0.31.5"
#     (no brackets).
#   - Under it, the "child" tickets for each activity, with the summary in brackets,
#     like "[QA][Time Tracking] Regression - San Van".
# Since the list comes ordered from newest to oldest, a version's activities
# are the ones between its parent ticket and the previous parent.

def find_available_versions(all_issues):
    """Parent ticket of each version, newest first: [{"label", "key", "index"}]."""
    versions = []
    for i, issue in enumerate(all_issues):
        summary = issue["fields"]["summary"]
        # A parent has no brackets and mentions "Time Tracking <number>".
        if "[" not in summary and re.search(r"Time Tracking [\d\.]+", summary):
            number = re.search(r"[\d]+\.[\d\.]+", summary)
            label = number.group(0) if number else summary
            versions.append({"label": label, "key": issue["key"], "index": i})
    return versions


def _clean_activity_label(summary):
    """Removes the '[...][Time Tracking] ' prefix and leaves only the activity name."""
    label = summary
    if "][Time Tracking] " in label:
        label = label.split("][Time Tracking] ")[-1]
    elif "[Time Tracking] " in label:
        label = label.replace("[Time Tracking] ", "")
    return label.strip()


def _extract_activities(issues):
    """Turns a batch of child tickets into {activity_name: ticket_key}, without duplicates."""
    activities = {}
    seen = set()
    for issue in issues:
        summary = issue["fields"]["summary"]
        if "[" not in summary:  # skip any parent that slipped in
            continue
        label = _clean_activity_label(summary)
        if label and label not in seen:
            activities[label] = issue["key"]
            seen.add(label)
    return dict(sorted(activities.items()))


def activities_for_version(all_issues, versions, version_index):
    """{activity: ticket_key} for the chosen version (0 = newest)."""
    selected = versions[version_index]
    if version_index == 0:
        # Newest version: its activities go from the start of the list
        # (the most recent) up to just before its parent ticket.
        start_idx, end_idx = 0, selected["index"]
    else:
        # Older version: between the previous parent (exclusive) and this parent.
        prev_parent = versions[version_index - 1]
        start_idx, end_idx = prev_parent["index"] + 1, selected["index"]
    return _extract_activities(all_issues[start_idx:end_idx])


# Dates and times

def get_workdays(start_date, end_date):
    """List of business days (Monday to Friday) between two dates, inclusive."""
    days = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # 0=Monday ... 4=Friday
            days.append(current)
        current += timedelta(days=1)
    return days


def parse_date(text):
    """Parses a date in several common formats. Returns a date or None."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    return None


def parse_time(text):
    """"2h", "1h 30m", "45m" or "1.5h" -> (normalized text, minutes). Empty or zero -> (None, 0)."""
    text = (text or "").strip().lower()
    if not text or text in ("0", "skip", "s", "-"):
        return None, 0

    total_minutes = 0
    try:
        if "h" in text and "m" in text:
            hours_part = text.split("h")[0].strip()
            minutes_part = text.split("h")[1].replace("m", "").strip()
            total_minutes = int(hours_part) * 60 + int(minutes_part)
        elif "h" in text:
            total_minutes = int(float(text.replace("h", "").strip()) * 60)
        elif "m" in text:
            total_minutes = int(text.replace("m", "").strip())
        else:
            # A bare number is read as hours: "1.5" -> 90 min.
            total_minutes = int(float(text) * 60)
    except ValueError:
        return None, 0

    if total_minutes <= 0:
        return None, 0
    return format_minutes(total_minutes), total_minutes


def format_minutes(total_minutes):
    """Turns minutes into readable text: 90 -> '1h 30m', 120 -> '2h', 45 -> '45m'."""
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    if hours > 0:
        return f"{hours}h"
    return f"{minutes}m"


# Send the time log to JaaS

def submit_worklog(token, ticket_key, time_spent, log_date, comment):
    """Logs time on a ticket, starting at 09:00 that day. Returns (ok, error)."""
    headers = {**_headers(token), "Content-Type": "application/json"}
    started = f"{log_date.strftime('%Y-%m-%d')}T09:00:00.000+0000"
    payload = {"timeSpent": time_spent, "started": started, "comment": comment}
    try:
        res = requests.post(
            f"{JAAS_URL}/rest/api/2/issue/{ticket_key}/worklog",
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.RequestException as error:
        return False, str(error)

    if res.status_code in (200, 201):
        return True, None
    return False, res.text
