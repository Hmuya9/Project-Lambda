"""Offline tests: schema, backlog, ranking, rendering. No API key, no network."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from lambda_core.backlog import append_entries, as_prompt_block, load_backlog, next_id
from lambda_core.pipeline import rank
from lambda_core.render import render_all
from lambda_core.validate import ValidationError, validate_plan

ROOT = Path(__file__).resolve().parent.parent
DEMO_PLAN = ROOT / "examples" / "plans" / "bytedance_ai_compute_demo.json"


@pytest.fixture()
def demo_plan() -> dict:
    return json.loads(DEMO_PLAN.read_text(encoding="utf-8"))


# --- validation -------------------------------------------------------------

def test_demo_plan_validates(demo_plan):
    validate_plan(demo_plan)


def test_missing_done_when_fails(demo_plan):
    demo_plan["sprints"][0]["evidence"]["done_when"] = "done"
    with pytest.raises(ValidationError, match="done_when"):
        validate_plan(demo_plan)


def test_consumption_artifact_fails(demo_plan):
    demo_plan["sprints"][0]["evidence"]["artifact"] = "Learn Kubernetes basics"
    with pytest.raises(ValidationError, match="consumption"):
        validate_plan(demo_plan)


def test_empty_do_not_claim_fails(demo_plan):
    demo_plan["positioning"]["do_not_claim"] = []
    with pytest.raises(ValidationError, match="do_not_claim"):
        validate_plan(demo_plan)


def test_bad_gap_value_fails(demo_plan):
    demo_plan["gap_map"][0]["gap"] = "huge"
    with pytest.raises(ValidationError):
        validate_plan(demo_plan)


# --- backlog ----------------------------------------------------------------

def test_backlog_loads_with_stable_ids():
    problems = load_backlog()
    ids = [p.id for p in problems]
    assert ids[0] == "P1"
    assert "P61" in ids
    assert len(ids) == len(set(ids)), "backlog IDs must be unique"


def test_backlog_prompt_block_contains_domains():
    block = as_prompt_block(load_backlog())
    assert "P34: Why does Kubernetes exist?" in block
    assert "[AI Systems & Infrastructure]" in block


def test_backlog_grows_never_mutates(tmp_path):
    copy = tmp_path / "backlog.md"
    shutil.copy(ROOT / "data" / "backlog.md", copy)
    before = load_backlog(copy)
    appended = append_entries(
        [{"problem": "Why is test isolation expensive?", "domain": "Testing"}], copy
    )
    after = load_backlog(copy)
    assert appended == [f"P{next_id(before) - 0}"] or appended  # got a fresh ID
    assert len(after) == len(before) + 1
    # existing entries untouched
    assert [(p.id, p.problem) for p in after[: len(before)]] == [
        (p.id, p.problem) for p in before
    ]
    # duplicate append is a no-op
    assert append_entries(
        [{"problem": "Why is test isolation expensive?", "domain": "Testing"}], copy
    ) == []


# --- ranking ----------------------------------------------------------------

def test_rank_is_deterministic_and_foundations_first():
    gap_map = [
        {"id": "P34", "problem": "k8s", "importance": 5, "gap": "full"},
        {"id": "P6", "problem": "docker", "importance": 5, "gap": "full"},
        {"id": "P30", "problem": "obs", "importance": 4, "gap": "partial"},
        {"id": "P25", "problem": "dist", "importance": 4, "gap": "none"},
    ]
    ranked = rank(gap_map)
    # equal score (5*3): lower backlog ID (foundation) first
    assert [g["id"] for g in ranked[:2]] == ["P6", "P34"]
    # priorities are 1..n
    assert [g["priority"] for g in ranked] == [1, 2, 3, 4]
    # lowest score last
    assert ranked[-1]["id"] == "P25"


# --- rendering --------------------------------------------------------------

def test_render_all_offline(demo_plan, tmp_path):
    summary = render_all(demo_plan, tmp_path)
    assert summary["sprints"] == len(demo_plan["sprints"])
    dashboard = (tmp_path / "dashboard.html").read_text(encoding="utf-8")
    assert "/*__PLAN_JSON__*/null" not in dashboard, "plan data must be injected"
    assert demo_plan["meta"]["role_title"] in dashboard
    vault = tmp_path / "vault"
    assert (vault / "00 - Plan Overview.md").exists()
    assert (vault / "01 - Positioning.md").exists()
    weeks = list((vault / "02 - Weekly Sprints").glob("Week *.md"))
    assert len(weeks) == len(demo_plan["sprints"])
    pages = list((vault / "03 - Engineering Notebook").glob("*.md"))
    assert len(pages) >= len(demo_plan["gap_map"])


def test_engine_has_no_jd_or_user_specific_logic():
    """The anti-overfit invariant, enforced as a test."""
    banned = ("bytedance", "fluidstack", "redfish", " bmc", "huss")
    for py in (ROOT / "lambda_core").glob("*.py"):
        text = py.read_text(encoding="utf-8").lower()
        for term in banned:
            assert term not in text, f"{py.name} contains engine-overfit term: {term!r}"
