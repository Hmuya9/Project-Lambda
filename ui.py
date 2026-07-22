"""Project Lambda — local Streamlit UI wrapping the same pipeline.

    streamlit run ui.py
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

st.set_page_config(page_title="Project Lambda", layout="wide")
st.title("Project Lambda")
st.caption(
    "The market pays for proximity to expensive problems — not for knowing technologies. "
    "Profile + market intent in, evidence-driven plan out."
)

with st.sidebar:
    st.header("Intake")
    intent = st.selectbox(
        "Market intent",
        ("targeted", "directional", "exploratory"),
        help=(
            "targeted: one specific job description · "
            "directional: a domain (paste several postings or a domain brief) · "
            "exploratory: cross-domain, narrowing is part of the work"
        ),
    )
    weeks = st.slider("Sprint count", 4, 12, 8)
    update_backlog = st.checkbox("Grow data/backlog.md with new problems", value=True)

    st.divider()
    example_jobs = sorted((ROOT / "examples" / "jobs").glob("*.md"))
    example_profiles = sorted((ROOT / "examples" / "profiles").glob("*.md"))
    job_example = st.selectbox("Load example JD", ["(none)"] + [p.name for p in example_jobs])
    profile_example = st.selectbox("Load example profile", ["(none)"] + [p.name for p in example_profiles])

col1, col2 = st.columns(2)
with col1:
    job_default = ""
    if job_example != "(none)":
        job_default = (ROOT / "examples" / "jobs" / job_example).read_text(encoding="utf-8")
    job_text = st.text_area("Job description / market composite", value=job_default, height=320)
with col2:
    profile_default = ""
    if profile_example != "(none)":
        profile_default = (ROOT / "examples" / "profiles" / profile_example).read_text(encoding="utf-8")
    profile_text = st.text_area("Engineer profile", value=profile_default, height=320)

# ---------- Step 1: Discover ------------------------------------------------
if st.button("Decode this role", type="primary"):
    if not job_text.strip() or not profile_text.strip():
        st.error(
            "Intake gate: both a job description (or composite) and a profile are "
            "required. Nothing is tailored without them."
        )
        st.stop()
    import traceback

    from lambda_core.pipeline import run_discovery

    st.session_state.pop("error", None)
    st.session_state.pop("plan", None)
    with st.status("Decoding the role and pitching your projects...", expanded=True) as status:
        try:
            st.session_state["discovery"] = run_discovery(
                job_text, profile_text, intent=intent, update_backlog=update_backlog
            )
            st.session_state["profile_text"] = profile_text
            status.update(label="Role decoded — pick your project below", state="complete")
        except Exception as exc:  # surface config/API errors readably
            status.update(label="Pipeline failed", state="error")
            st.session_state["error"] = (str(exc), traceback.format_exc())

# Errors render OUTSIDE the collapsible status box so they are always visible.
if err := st.session_state.get("error"):
    st.error(err[0])
    with st.expander("Full traceback"):
        st.code(err[1])

# ---------- Step 2: The hook + project pick ---------------------------------
discovery = st.session_state.get("discovery")
if discovery and not st.session_state.get("plan"):
    decode = discovery["decode"]
    st.header(str(decode.get("role_title", "")) + (f" @ {decode['company']}" if decode.get("company") else ""))

    hook = decode.get("human_hook") or {}
    if hook.get("what_this_really_is"):
        st.markdown(f"### {hook['what_this_really_is']}")
        if hook.get("why_exciting"):
            st.markdown(f"**Why it's exciting —** {hook['why_exciting']}")
        if hook.get("why_doable"):
            st.markdown(f"**Why it's doable —** {hook['why_doable']}")
    else:
        st.write(decode.get("summary", ""))

    with st.expander("The expensive problems behind this role (ranked)", expanded=False):
        for g in discovery["gap_map"]:
            human = next(
                (p.get("human", "") for p in discovery["expensive_problems"] if p.get("id") == g["id"]),
                "",
            )
            st.markdown(
                f"**{g['priority']}. {g['problem']}** ({g['id']}, importance {g['importance']}/5, gap: {g['gap']})"
                + (f"  \n{human}" if human else "")
            )

    options = discovery.get("project_options", [])
    if options:
        st.subheader("Pick your project")
        st.caption(
            "The goal: sit you as close to those expensive problems as we can — by building "
            "something you can SEE working (and breaking). Same physics as the industrial "
            "version, smaller machine. Pick the one that pokes your inner engineer."
        )
        labels = [f"{p.get('title', f'Project {i+1}')}" for i, p in enumerate(options)]
        choice = st.radio("Projects", labels, label_visibility="collapsed")
        idx = labels.index(choice)
        p = options[idx]
        st.markdown(f"#### {p.get('title', '')}")
        st.markdown(p.get("hook", ""))
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**What you'll see:** {p.get('what_you_will_see', '')}")
            st.markdown(f"**Think of it as:** {p.get('analogy', '')}")
            st.markdown(f"**First win (one sitting):** {p.get('first_win', '')}")
        with col_b:
            st.markdown(f"**You'll learn:** {p.get('what_you_will_learn', '')}")
            st.markdown(
                f"**Difficulty:** {p.get('difficulty', '?')}/5 · **~{p.get('weeks_estimate', '?')} weeks** · "
                f"touches {', '.join(p.get('problems_touched', []))}"
            )
    else:
        idx = None

    if st.button("Build my plan around this project", type="primary"):
        import traceback

        from lambda_core.pipeline import run_plan

        st.session_state.pop("error", None)
        chosen = options[idx] if options else None
        with st.status("Building your sprint plan...", expanded=True) as status:
            try:
                st.session_state["plan"] = run_plan(
                    discovery,
                    st.session_state.get("profile_text", profile_text),
                    project=chosen,
                    weeks=weeks,
                )
                status.update(label="Plan ready", state="complete")
                st.rerun()
            except Exception as exc:
                status.update(label="Pipeline failed", state="error")
                st.session_state["error"] = (str(exc), traceback.format_exc())

# ---------- Step 3: The plan ------------------------------------------------
plan = st.session_state.get("plan")
if plan:
    meta = plan["meta"]
    st.subheader(meta["role_title"] + (f" @ {meta['company']}" if meta.get("company") else ""))
    hook = plan["role_decode"].get("human_hook") or {}
    if hook.get("what_this_really_is"):
        st.markdown(hook["what_this_really_is"])
    else:
        st.write(plan["role_decode"]["summary"])
    proj = plan.get("project") or {}
    if proj.get("title"):
        st.success(f"**Your project: {proj['title']}** — {proj.get('hook', '')}")
    if st.button("↩ Pick a different project"):
        st.session_state.pop("plan", None)
        st.rerun()

    tab_gap, tab_sprints, tab_pos, tab_json = st.tabs(["Gap map", "Sprints", "Positioning", "plan.json"])
    with tab_gap:
        st.dataframe(plan["gap_map"], use_container_width=True)
    with tab_sprints:
        from lambda_core.render import watch_url

        for s in plan["sprints"]:
            with st.expander(f"Week {s['week']} — {s['primary']['question']}"):
                if s.get("simple_intro"):
                    st.markdown(s["simple_intro"])
                if s.get("why_this_matters"):
                    st.caption(f"Why this matters: {s['why_this_matters']}")
                watch = [w for w in (s.get("watch") or []) if isinstance(w, dict) and w.get("query")]
                if watch:
                    st.markdown(
                        "**Watch first (gentle → deeper):** "
                        + "  \n".join(
                            f"▶ [{w.get('title', 'video')}]({watch_url(w)})"
                            + (f" — {w['why']}" if w.get("why") else "")
                            for w in watch
                        )
                    )
                ev = s["evidence"]
                st.markdown(f"**Evidence ({ev['type']}):** {ev['artifact']}")
                st.markdown(f"**Done when:** {ev['done_when']}")
                if s.get("secondary"):
                    st.markdown("**Secondary:** " + " · ".join(s["secondary"]))
                if s.get("interview"):
                    st.markdown("**Interview:** " + " · ".join(s["interview"]))
    with tab_pos:
        st.write(plan["positioning"]["narrative"])
        st.markdown("**Talking points**")
        for t in plan["positioning"]["talking_points"]:
            st.markdown(f"- {t}")
        st.markdown("**Do not claim**")
        for t in plan["positioning"]["do_not_claim"]:
            st.markdown(f"- ❌ {t}")
    with tab_json:
        st.json(plan)

    # Render to a scratch dir and offer a zip download (dashboard + vault + plan).
    from lambda_core.render import render_all

    out_dir = ROOT / "outputs" / "_ui_last"
    render_all(plan, out_dir)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in out_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(out_dir))
        zf.writestr("plan.json", json.dumps(plan, indent=2, ensure_ascii=False))
    st.download_button(
        "Download plan bundle (dashboard + Obsidian vault + plan.json)",
        data=buf.getvalue(),
        file_name="lambda_plan.zip",
        mime="application/zip",
    )
