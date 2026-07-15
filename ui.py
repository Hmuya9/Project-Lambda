"""Local Streamlit UI wrapping Project Lambda generation (MVP-001)."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from lambda_core.generator import generate_contract, resolve_config
from lambda_core.outputs import default_output_path, render_markdown, write_markdown

ROOT = Path(__file__).resolve().parent
JOBS_DIR = ROOT / "examples" / "jobs"
PROFILES_DIR = ROOT / "examples" / "profiles"
OUTPUTS_DIR = ROOT / "outputs"

load_dotenv(ROOT / ".env")


def _list_examples(directory: Path) -> list[str]:
    if not directory.is_dir():
        return []
    return sorted(
        p.name for p in directory.iterdir() if p.suffix.lower() in {".md", ".txt"} and p.is_file()
    )


def _load_example(directory: Path, name: str) -> str:
    return (directory / name).read_text(encoding="utf-8")


def main() -> None:
    st.set_page_config(
        page_title="Project Lambda — Role-to-Roadmap Engine",
        layout="wide",
    )
    st.title("Project Lambda — Role-to-Roadmap Engine")

    api_key, model, base_url = resolve_config()
    if not api_key:
        st.error(
            "OPENAI_API_KEY is missing or blank. Set it in `.env` "
            "(see `.env.example`). The API key is never shown in this UI."
        )
    else:
        st.caption(
            f"Model: `{model}`"
            + (f" · Base URL: `{base_url}`" if base_url else " · Default OpenAI API")
        )

    if "job_text" not in st.session_state:
        st.session_state.job_text = ""
    if "profile_text" not in st.session_state:
        st.session_state.profile_text = ""
    if "job_source" not in st.session_state:
        st.session_state.job_source = "pasted"
    if "profile_source" not in st.session_state:
        st.session_state.profile_source = "pasted"

    left, right = st.columns(2)

    with left:
        st.subheader("Inputs")

        job_examples = _list_examples(JOBS_DIR)
        profile_examples = _list_examples(PROFILES_DIR)

        job_pick = st.selectbox(
            "Optional: load example job",
            options=["(none)"] + job_examples,
            key="job_example_pick",
        )
        if st.button("Load job example", disabled=(job_pick == "(none)")):
            st.session_state.job_text = _load_example(JOBS_DIR, job_pick)
            st.session_state.job_source = f"examples/jobs/{job_pick}"
            st.rerun()

        profile_pick = st.selectbox(
            "Optional: load example profile",
            options=["(none)"] + profile_examples,
            key="profile_example_pick",
        )
        if st.button("Load profile example", disabled=(profile_pick == "(none)")):
            st.session_state.profile_text = _load_example(PROFILES_DIR, profile_pick)
            st.session_state.profile_source = f"examples/profiles/{profile_pick}"
            st.rerun()

        job_text = st.text_area(
            "Job description (raw paste — not cleaned or rewritten)",
            key="job_text",
            height=280,
        )
        profile_text = st.text_area(
            "Engineer profile / background (raw paste)",
            key="profile_text",
            height=280,
        )

        generate = st.button("Generate", type="primary", use_container_width=True)

        if generate:
            if not api_key:
                st.error("Cannot generate: OPENAI_API_KEY is missing.")
            elif not job_text:
                st.error("Job description is required.")
            elif not profile_text:
                st.error("Engineer profile is required.")
            else:
                with st.spinner("Generating Role-to-Roadmap..."):
                    try:
                        # Pass raw text through unchanged (no rewrite/summary).
                        contract = generate_contract(job_text, profile_text)
                        markdown = render_markdown(
                            contract,
                            job_source=st.session_state.job_source,
                            profile_source=st.session_state.profile_source,
                        )
                        st.session_state.contract = contract
                        st.session_state.markdown = markdown
                        st.session_state.gen_error = None
                    except Exception as exc:
                        st.session_state.contract = None
                        st.session_state.markdown = None
                        st.session_state.gen_error = str(exc)

    with right:
        st.subheader("Output")

        if st.session_state.get("gen_error"):
            st.error(f"Generation failed: {st.session_state.gen_error}")

        markdown = st.session_state.get("markdown")
        contract = st.session_state.get("contract")

        if not markdown or not contract:
            st.info("Generated Markdown roadmap will appear here after you click Generate.")
            return

        st.markdown(markdown)

        with st.expander("JSON (raw roadmap)"):
            st.json(contract)

        json_text = json.dumps(contract, indent=2)
        stamp_path = default_output_path(OUTPUTS_DIR)
        json_default_name = stamp_path.with_suffix(".json").name
        md_default_name = stamp_path.name

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Save Markdown to outputs/", use_container_width=True):
                path = write_markdown(markdown, default_output_path(OUTPUTS_DIR))
                st.success(f"Saved: `{path}`")
            st.download_button(
                "Download Markdown",
                data=markdown,
                file_name=md_default_name,
                mime="text/markdown",
                use_container_width=True,
            )
        with c2:
            if st.button("Save JSON to outputs/", use_container_width=True):
                path = default_output_path(OUTPUTS_DIR).with_suffix(".json")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json_text, encoding="utf-8")
                st.success(f"Saved: `{path}`")
            st.download_button(
                "Download JSON",
                data=json_text,
                file_name=json_default_name,
                mime="application/json",
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
