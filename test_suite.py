"""
Tests with simulated JaaS data, no network.

Covers the WorkLogger logic, that the three apps reach the login screen,
and the WorkLogger logging screen.

Run:  python -m pytest test_suite.py -q
"""

from datetime import date

import worklogger_core as wl


# 1. WorkLogger logic

def _fake_issues():
    """Mimics the list JaaS returns: children on top (newest), parents in between."""
    def issue(key, summary):
        return {"key": key, "fields": {"summary": summary}}
    return [
        issue("FCQV-11", "[QA][Time Tracking] Regression - San Van"),  # 0  child v0.31.5
        issue("FCQV-12", "[QA][Time Tracking] Smoke - Boot"),          # 1  child v0.31.5
        issue("FCQV-10", "Time Tracking 0.31.5"),                       # 2  PARENT v0.31.5
        issue("FCQV-08", "[QA][Time Tracking] Old task"),               # 3  child v0.31.4
        issue("FCQV-07", "Time Tracking 0.31.4"),                       # 4  PARENT v0.31.4
    ]


def test_find_versions():
    versions = wl.find_available_versions(_fake_issues())
    assert [v["label"] for v in versions] == ["0.31.5", "0.31.4"]
    assert versions[0]["index"] == 2 and versions[1]["index"] == 4


def test_activities_latest_version():
    issues = _fake_issues()
    versions = wl.find_available_versions(issues)
    acts = wl.activities_for_version(issues, versions, 0)  # the newest
    assert acts == {
        "Regression - San Van": "FCQV-11",
        "Smoke - Boot": "FCQV-12",
    }


def test_activities_older_version():
    issues = _fake_issues()
    versions = wl.find_available_versions(issues)
    acts = wl.activities_for_version(issues, versions, 1)  # the previous one
    assert acts == {"Old task": "FCQV-08"}


def test_parse_time():
    assert wl.parse_time("2h") == ("2h", 120)
    assert wl.parse_time("1h 30m") == ("1h 30m", 90)
    assert wl.parse_time("45m") == ("45m", 45)
    assert wl.parse_time("1.5h") == ("1h 30m", 90)
    assert wl.parse_time("") == (None, 0)
    assert wl.parse_time("0") == (None, 0)


def test_format_minutes():
    assert wl.format_minutes(90) == "1h 30m"
    assert wl.format_minutes(120) == "2h"
    assert wl.format_minutes(45) == "45m"


def test_workdays_skips_weekend():
    # Monday 2026-10-05 to Sunday 2026-10-11 -> 5 business days.
    days = wl.get_workdays(date(2026, 10, 5), date(2026, 10, 11))
    assert len(days) == 5
    assert all(d.weekday() < 5 for d in days)


# 2 and 3. the apps start up (using Streamlit's AppTest)

def test_apps_reach_login():
    from streamlit.testing.v1 import AppTest
    for app_file in ("macondo_app.py", "worklogger_app.py", "macondo_suite_app.py"):
        at = AppTest.from_file(app_file, default_timeout=30).run()
        assert not at.exception, f"{app_file} raised an exception on startup"
        # Before connecting, the Connect button always shows up.
        labels = [b.label for b in at.button]
        assert "Connect" in labels, f"{app_file} didn't show the Connect button"


def test_worklogger_load_versions_button():
    """Regression: pressing 'Load versions' must not clash with the wl_project widget."""
    from streamlit.testing.v1 import AppTest
    import worklogger_core

    issues = _fake_issues()
    # We avoid the network: fetch_all_issues returns simulated data.
    worklogger_core.fetch_all_issues = lambda token, project=worklogger_core.DEFAULT_PROJECT: issues

    at = AppTest.from_file("worklogger_app.py", default_timeout=30)
    at.session_state["connected"] = True
    at.session_state["jaas_token"] = "fake"
    at.session_state["reporter"] = "ivanromero"
    at.session_state["user_display_name"] = "Ivan Romero"
    at.run()
    assert not at.exception

    # Click on "Load versions" -> it used to crash when reassigning wl_project.
    button = next(b for b in at.button if b.label == "Load versions")
    button.click().run()
    assert not at.exception, "Load versions raised an exception"
    assert at.session_state["wl_project_resolved"] == "FCQV"


def _log_stage_app():
    """Sets up a WorkLogger AppTest already in the logging stage, with simulated data."""
    from streamlit.testing.v1 import AppTest
    import worklogger_core

    issues = _fake_issues()
    versions = worklogger_core.find_available_versions(issues)
    activities = worklogger_core.activities_for_version(issues, versions, 0)

    at = AppTest.from_file("worklogger_app.py", default_timeout=30)
    at.session_state["connected"] = True
    at.session_state["jaas_token"] = "fake"
    at.session_state["reporter"] = "ivanromero"
    at.session_state["user_display_name"] = "Ivan Romero"
    at.session_state["wl_stage"] = "log"
    at.session_state["wl_project"] = "FCQV"
    at.session_state["wl_project_resolved"] = "FCQV"
    at.session_state["wl_all_issues"] = issues
    at.session_state["wl_versions"] = versions
    at.session_state["wl_version_index"] = 0
    at.session_state["wl_activities"] = activities
    at.session_state["wl_workdays"] = [date(2026, 10, 5), date(2026, 10, 6)]
    at.session_state["wl_time"] = {}
    at.session_state["wl_results"] = None
    return at


def test_worklogger_log_screen_with_fake_data():
    """The logging screen draws every day inside a form."""
    at = _log_stage_app().run()
    assert not at.exception, "the logging screen raised an exception"
    assert "Change version / dates" in [b.label for b in at.button]
    # No day selector (it used to jump). Every input visible: 2 activities x 2 days = 4.
    assert len(at.selectbox) == 0
    assert len(at.text_input) == 4


def test_worklogger_time_persists_and_counts():
    """Regression: a typed hour is kept (every input is always drawn)
    and the right day counts it, without jumping to another date."""
    import worklogger_ui

    at = _log_stage_app()
    # We simulate that 2h had already been typed in an activity on the SECOND day.
    key = worklogger_ui._input_key(date(2026, 10, 6), "Regression - San Van")
    at.session_state[key] = "2h"
    at.run()
    assert not at.exception
    # The input keeps the hour.
    assert "2h" in [ti.value for ti in at.text_input]
    # And it shows up under 06/10 in the summary (the right day, not another one).
    md = " ".join(m.value or "" for m in at.markdown)
    assert "2h" in md and "06/10" in md


if __name__ == "__main__":
    import sys
    import traceback

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for test in tests:
        try:
            test()
            print(f"  OK  {test.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL  {test.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} tests OK")
    sys.exit(0 if passed == len(tests) else 1)
