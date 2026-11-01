"""
Bug Logger screens.

render() is used on its own (macondo_app.py) or as a tab (macondo_suite_app.py).
Login happens before, in macondo_login.

Stages, kept in st.session_state["bl_stage"]: project, form, preview, done.
"""

import streamlit as st

import core


# Helpers

def _is_empty(value):
    return value is None or value == "" or value == []


def _project_label(project):
    """Project label in the list, flagging the recent ones and the ones you lead."""
    tags = [tag for tag, on in (("recent", project["recent"]), ("lead", project["is_lead"])) if on]
    return f"{project['key']}: {project['name']}" + (f"   [{', '.join(tags)}]" if tags else "")


def _load_projects():
    """Lists the projects where you can create bugs. If JaaS doesn't allow it, uses the fallback list."""
    try:
        projects, verified = core.list_user_projects(
            st.session_state.jaas_token, st.session_state.reporter
        )
    except Exception:
        projects = [
            {"key": k, "name": n, "can_create": None, "is_lead": False, "recent": False}
            for k, n in core.FALLBACK_PROJECTS.items()
        ]
        verified = False
    st.session_state.bl_projects = projects
    st.session_state.bl_projects_verified = verified


def _open_project(project_key):
    """Reads the project's enabled fields and moves on to the form. True if it could open it."""
    with st.spinner(f"Reading the enabled fields of {project_key}..."):
        meta = core.load_project_meta(
            st.session_state.jaas_token, st.session_state.reporter, project_key
        )
    if meta is None:
        st.error(
            f"Couldn't read the fields of {project_key}. You may not have permission to create bugs there, "
            "it may not have a 'Bug' type, or there may be no ticket to use as a reference."
        )
        return False
    st.session_state.bl_meta = meta
    st.session_state.bl_stage = "form"
    return True


def _init_state():
    """Default values for the Bug Logger session. Loads the projects the first time."""
    defaults = {
        "bl_stage": "project",
        "bl_meta": None,
        "bl_ticket": None,
        "bl_was_corrected": False,
        "bl_projects": None,
        "bl_projects_verified": True,
        "bl_pending_files": [],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    if st.session_state.bl_projects is None:
        with st.spinner("Looking for your projects..."):
            _load_projects()


# Stage: choose a project

def _stage_project():
    st.subheader("Choose the project")

    if not st.session_state.bl_projects_verified:
        st.warning(
            "I couldn't verify which projects you're allowed to create bugs in, so you'll see every project "
            "JaaS lets me see (or the fallback list). If you pick one where you can't create, I'll let you know when you open it."
        )

    text_filter = st.text_input("Filter by key or name", key="bl_project_filter").strip().lower()
    visible = [
        p for p in st.session_state.bl_projects
        if text_filter in f"{p['key']} {p['name']}".lower()
    ]
    st.caption(
        f"{len(visible)} of {len(st.session_state.bl_projects)} projects · "
        "recent ones and the ones you lead come first"
    )

    if visible:
        keys_by_label = {_project_label(p): p["key"] for p in visible}
        choice = keys_by_label[st.selectbox("Project", list(keys_by_label), key="bl_project_choice")]
    else:
        choice = None
        st.info("No project matches the filter.")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Use this project", type="primary", disabled=not choice, key="bl_btn_use_project"):
            if _open_project(choice):
                st.rerun()
    with col_b:
        if st.button("Refresh list", key="bl_btn_reload_projects"):
            with st.spinner("Looking for your projects..."):
                _load_projects()
            st.rerun()

    with st.expander("Don't see your project? Type the key"):
        manual = st.text_input("Project key (e.g. SK8, ABC, XYZ)", key="bl_manual_project").strip().upper()
        if st.button("Open by key", disabled=not manual, key="bl_btn_manual_project"):
            if _open_project(manual):
                st.rerun()


# Stage: form (the project's enabled fields)

def _stage_form():
    meta = st.session_state.bl_meta
    project = meta["project"]
    catalogs = meta["catalogs"]
    field_ids = meta["field_ids"]
    required = meta["required_ids"]
    enabled = meta["enabled_ids"]

    def on_screen(field_id):
        """True if the field is on the create screen (or we don't know, so we let it through)."""
        return bool(field_id) and (enabled is None or field_id in enabled)

    def star(field_id):
        """Marks required fields with ' *'."""
        return " *" if field_id in required else ""

    # Top bar: project and refresh
    top_a, top_b, top_c = st.columns([3, 1.4, 1.6])
    top_a.caption(f"connected as {st.session_state.user_display_name}")
    if top_b.button("Change project", key="bl_btn_change_project"):
        st.session_state.bl_stage = "project"
        st.rerun()
    if top_c.button("🔄 Refresh fields", key="bl_btn_refresh"):
        with st.spinner("Updating..."):
            fresh = core.load_project_meta(st.session_state.jaas_token, st.session_state.reporter, project)
        if fresh:
            st.session_state.bl_meta = fresh
            st.rerun()
        st.error("Couldn't update the fields.")

    st.markdown(f"### {project}")
    if meta["source"] == "createmeta":
        st.caption(
            f"Fields read from the project's create screen (type {meta['issuetype_name']}). "
            "The ones marked with * are required."
        )
        if not meta.get("issuetype_is_bug", True):
            st.warning(f"This project doesn't have a 'Bug' type. Using '{meta['issuetype_name']}'.")
    else:
        st.warning(
            f"Couldn't read the create screen of {project}; used ticket {meta['ref_ticket']} as a reference. "
            "Fields the project doesn't allow on create may show up: if JaaS rejects them, they're skipped and I'll let you know."
        )

    # Where it's learning the style from in this project
    learning = core.learning_status(project, meta.get("style"))
    if learning["corrections"] or learning["real_tickets"]:
        parts = []
        if learning["corrections"]:
            parts.append(f"{learning['corrections']} correction(s) of yours")
        if learning["real_tickets"]:
            parts.append(f"{learning['real_tickets']} real bug(s) {learning['real_source']}")
        st.caption("🦋 Learning the style of " + project + " from: " + " + ".join(parts))
    else:
        st.caption(
            "🦋 There are no reference bugs in " + project +
            " yet: a base style is used until you correct the first ones."
        )

    # Real ML accuracy in this project, measured through use.
    acc = core.accuracy_report(project)
    if acc["sent"]:
        st.caption(
            f"📊 Accuracy in {project}: {acc['accuracy_pct']:.0f}% "
            f"({acc['unedited']} of {acc['sent']} sent without rewriting) · "
            f"average similarity to the draft: {acc['avg_similarity_pct']:.0f}%"
        )

    blocking = [f["name"] for f in meta["unsupported_fields"] if f["required"]]
    if blocking:
        st.error(
            "This project requires fields the app can't fill in yet: " + ", ".join(blocking) +
            ". JaaS will probably reject the ticket."
        )

    def known_select(box, logical, label):
        """Draws a selectbox for one of the known fields, if the project has it."""
        field_id = field_ids.get(logical)
        options = sorted(catalogs[logical])
        if not field_id or not options:
            return None
        return box.selectbox(label + star(field_id), options, key=f"bl_{project}_{logical}")

    # Build info
    st.subheader("Build info")
    col1, col2 = st.columns(2)
    cl = col1.text_input("CL number" + star(field_ids.get("changelist")), key=f"bl_{project}_cl")
    branch = col1.selectbox("Branch", core.BRANCHES, key=f"bl_{project}_branch") if field_ids.get("branch") else None
    if on_screen("versions") and catalogs["version"]:
        version = col2.selectbox("Version" + star("versions"), sorted(catalogs["version"]), key=f"bl_{project}_version")
    else:
        version = None
    bug_type = col2.selectbox("Bug type", core.BUG_TYPES, key=f"bl_{project}_bug_type") if field_ids.get("bug_type") else None

    # Known fields
    st.subheader("Fields")
    col1, col2 = st.columns(2)
    pillar = known_select(col1, "pillar", "Pillar team")
    feature = col1.text_input("Feature", key=f"bl_{project}_feature", placeholder="e.g. Challenges, News System")
    game_spine = known_select(col1, "game_spine", "Game spine")
    platform = known_select(col1, "platform", "Platform")
    repro_rate = known_select(col2, "repro_rate", "Repro rate")
    player_impact = known_select(col2, "player_impact", "Player impact")
    severity = known_select(col2, "severity", "Severity")
    player_path = known_select(col2, "player_path", "Player path")

    col1, col2 = st.columns(2)
    activity = known_select(col1, "activity", "Activity")
    if on_screen("priority") and catalogs["priority"]:
        priority = col2.selectbox(
            "Priority (optional)", ["(not specified)"] + sorted(catalogs["priority"]), key=f"bl_{project}_priority"
        )
        priority = None if priority == "(not specified)" else priority
    else:
        priority = None

    # Extra fields the project has and the app knows how to draw
    def render_extra(extra, box):
        label = extra["name"] + (" *" if extra["required"] else "")
        key = f"bl_{project}_x_{extra['id']}"
        kind = extra["kind"]
        if kind == "text":
            return box.text_input(label, key=key)
        if kind == "number":
            return box.number_input(label, value=None, key=key)
        if kind == "date":
            picked = box.date_input(label, value=None, key=key)
            return picked.isoformat() if picked else None
        if kind == "select":
            picked = box.selectbox(label, [""] + sorted(extra["options"]), key=key)
            return picked or None
        if kind == "multiselect":
            return box.multiselect(label, sorted(extra["options"]), key=key)
        if kind == "labels":
            return box.text_input(label, key=key, help="Comma-separated")
        return None

    extras_values = {}
    required_extras = [e for e in meta["extra_fields"] if e["required"]]
    optional_extras = [e for e in meta["extra_fields"] if not e["required"]]
    if required_extras:
        st.subheader(f"Required fields in {project}")
        for extra in required_extras:
            extras_values[extra["id"]] = render_extra(extra, st)
    if optional_extras:
        with st.expander(f"Other fields enabled in {project} ({len(optional_extras)})"):
            for extra in optional_extras:
                extras_values[extra["id"]] = render_extra(extra, st)

    missing = [e["name"] for e in required_extras if _is_empty(extras_values.get(e["id"]))]
    if field_ids.get("changelist") in required and not cl.strip():
        missing.append("CL number")

    # Free-text bug description + attachments
    st.subheader("Describe the bug")
    raw_bug = st.text_area(
        "Bug", height=120, key="bl_raw_bug",
        placeholder="What's happening, where, and what you expected instead",
    )

    st.markdown("**Attachments** (optional: logs, videos, images)")
    uploaded = st.file_uploader(
        "Drag files here or click to choose",
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="bl_file_uploader",
    )
    pasted = st.file_uploader(
        "Or paste a screenshot (Ctrl+V). Click here first, then paste",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"],
        key="bl_paste_uploader",
    )
    st.caption("To paste a screenshot: copy it (PrtScn or the snipping tool), click the box above, and press Ctrl+V.")

    all_files = list(uploaded or []) + list(pasted or [])
    if all_files:
        st.caption(f"{len(all_files)} file(s) ready to attach to the ticket: " + ", ".join(f.name for f in all_files))

    if missing:
        st.caption("Required fields missing: " + ", ".join(missing))

    # Generate with AI
    can_generate = bool(raw_bug and feature and not missing)
    if st.button("Generate with AI", type="primary", disabled=not can_generate, key="bl_btn_generate"):
        with st.spinner("Writing the summary and description..."):
            style = meta.get("style")
            summary = core.generate_summary(
                st.session_state.groq_client, pillar, game_spine, raw_bug, project, style
            )
            description = core.generate_description(
                st.session_state.groq_client, project, raw_bug, cl, branch,
                pillar, feature, repro_rate, player_impact, severity, style,
            )

        core.record_generation(project)  # metrics: one draft generated

        st.session_state.bl_pending_files = [(f.name, f.getvalue(), f.type) for f in all_files]
        st.session_state.bl_ticket = {
            "cl": cl, "branch": branch, "version": version, "bug_type": bug_type,
            "pillar": pillar, "feature": feature, "game_spine": game_spine,
            "platform": platform, "repro_rate": repro_rate, "player_impact": player_impact,
            "severity": severity, "player_path": player_path, "activity": activity,
            "priority": priority, "raw_bug": raw_bug,
            "extras": {fid: v for fid, v in extras_values.items() if not _is_empty(v)},
            "summary": summary, "description": description,
            # We keep the original draft to compare it with what's sent (accuracy):
            "generated_summary": summary, "generated_description": description,
        }
        st.session_state.bl_was_corrected = False
        st.session_state.bl_stage = "preview"
        st.rerun()


# Stage: editable preview

def _stage_preview():
    ticket = st.session_state.bl_ticket
    meta = st.session_state.bl_meta
    project = meta["project"]

    if project == "SK8":
        st.warning("Sending to **SK8** (real project). Check carefully before confirming.")
    else:
        st.info(f"Sending to **{project}**")

    st.subheader("Preview")
    edited_summary = st.text_input("Summary", value=ticket["summary"], key="bl_edit_summary")
    edited_description = st.text_area("Description", value=ticket["description"], height=350, key="bl_edit_description")

    # If you touched the text, we save it as an example when sending (that's how it learns your style).
    if edited_summary != ticket["summary"] or edited_description != ticket["description"]:
        st.session_state.bl_was_corrected = True

    with st.expander("Fields"):
        cols = st.columns(2)
        shown = [
            ("Pillar", ticket["pillar"]), ("Feature", ticket["feature"]),
            ("Game spine", ticket["game_spine"]), ("Platform", ticket["platform"]),
            ("Repro rate", ticket["repro_rate"]), ("Player impact", ticket["player_impact"]),
            ("Severity", ticket["severity"]), ("Player path", ticket["player_path"]),
            ("Activity", ticket["activity"]), ("Priority", ticket["priority"]),
            ("Version", ticket["version"]), ("CL", ticket["cl"]),
            ("Branch", ticket["branch"]), ("Bug type", ticket["bug_type"]),
        ]
        shown += [(meta["field_names"].get(fid, fid), value) for fid, value in ticket["extras"].items()]
        for i, (label, value) in enumerate(item for item in shown if item[1]):
            cols[i % 2].markdown(f"**{label}:** {value}")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("↩️ Start over", key="bl_btn_restart"):
            st.session_state.bl_stage = "form"
            st.session_state.bl_ticket = None
            st.rerun()

    with col2:
        if st.button("✅ Confirm and send", type="primary", key="bl_btn_submit"):
            ticket["summary"] = edited_summary
            ticket["description"] = edited_description

            with st.spinner("Sending to JaaS..."):
                res, warnings = core.submit_ticket(st.session_state.jaas_token, ticket, meta)

            if res.status_code == 201:
                key = res.json().get("key")
                st.session_state.bl_last_key = key
                st.session_state.bl_last_warnings = warnings

                pending_files = st.session_state.get("bl_pending_files", [])
                st.session_state.bl_attach_results = (
                    core.attach_files(st.session_state.jaas_token, key, pending_files) if pending_files else []
                )

                # We only save it as an example when you corrected something: that's what teaches it.
                if st.session_state.bl_was_corrected:
                    core.save_example(
                        project, ticket["raw_bug"], ticket["pillar"], ticket["feature"], edited_description,
                        summary=edited_summary,
                    )

                # Metrics: we record the submission and how much it changed from the draft.
                core.record_submission(
                    project, st.session_state.bl_was_corrected,
                    ticket.get("generated_description", ""), edited_description,
                )

                st.session_state.bl_stage = "done"
                st.rerun()
            else:
                st.error("Sending failed:")
                st.code(core.explain_error(res, meta))

    with col3:
        st.caption("Changes to the Summary/Description are saved as examples to improve future drafts.")


# Stage: done

def _stage_done():
    key = st.session_state.bl_last_key
    st.success(f"**{key}** created")
    st.markdown(f"[Open in JaaS](https://jaas.ea.com/browse/{key})")

    warnings = st.session_state.get("bl_last_warnings", [])
    if warnings:
        with st.expander(f"⚠️ {len(warnings)} field(s) couldn't be applied", expanded=True):
            st.caption("The ticket was created anyway, without these fields:")
            for warning in warnings:
                st.text(warning)

    attach_results = st.session_state.get("bl_attach_results", [])
    if attach_results:
        ok_count = sum(1 for _, ok, _ in attach_results if ok)
        fail_count = len(attach_results) - ok_count
        if fail_count == 0:
            st.caption(f"📎 {ok_count} attachment(s) uploaded successfully.")
        else:
            with st.expander(f"📎 {ok_count} attachment(s) OK, {fail_count} failed", expanded=True):
                for filename, ok, error in attach_results:
                    st.caption(f"✅ {filename}" if ok else f"❌ {filename}: {error}")

    col1, col2 = st.columns(2)
    if col1.button("Log another bug", key="bl_btn_another"):
        st.session_state.bl_stage = "form"
        st.session_state.bl_ticket = None
        st.session_state.bl_pending_files = []
        st.rerun()
    if col2.button("Change project", key="bl_btn_done_change_project"):
        st.session_state.bl_stage = "project"
        st.session_state.bl_ticket = None
        st.session_state.bl_pending_files = []
        st.rerun()


# Entry point: draws the current stage

def render():
    """Draws the Bug Logger. Assumes there's already a session (see macondo_login)."""
    _init_state()
    stage = st.session_state.bl_stage
    if stage == "project":
        _stage_project()
    elif stage == "form":
        _stage_form()
    elif stage == "preview":
        _stage_preview()
    elif stage == "done":
        _stage_done()
