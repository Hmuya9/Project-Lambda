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

if st.button("Generate plan", type="primary"):
    if not job_text.strip() or not profile_text.strip():
        st.error(
            "Intake gate: both a job description (or composite) and a profile are "
            "required. Nothing is tailored without them."
        )
        st.stop()
    from lambda_core.pipeline import run_pipeline

    with st.status("Running the Lambda pipeline...", expanded=True) as status:
        try:
            plan = run_pipeline(
                job_text, profile_text, intent=intent, weeks=weeks, update_backlog=update_backlog
            )
        except Exception as exc:  # surface config/API errors readably
            status.update(label="Pipeline failed", state="error")
            st.exception(exc)
            st.stop()
        status.update(label="Plan generated", state="complete")
    st.session_state["plan"] = plan

plan = st.session_state.get("plan")
if plan:
    meta = plan["meta"]
    st.subheader(meta["role_title"] + (f" @ {meta['company']}" if meta.get("company") else ""))
    st.write(plan["role_decode"]["summary"])

    tab_gap, tab_sprints, tab_pos, tab_json = st.tabs(["Gap map", "Sprints", "Positioning", "plan.json"])
    with tab_gap:
        st.dataframe(plan["gap_map"], use_container_width=True)
    with tab_sprints:
        for s in plan["sprints"]:
            with st.expander(f"Week {s['week']} — {s['primary']['question']}"):
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
