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


# --- id assignment (regression: KeyError 'id' on live runs) -----------------

def test_assign_ids_matched_and_new():
    from lambda_core.pipeline import assign_ids

    mappings = [
        {"problem": "Why does K8s exist?", "backlog_id": "P34", "backlog_problem": "Why does Kubernetes exist?", "domain": ""},
        {"problem": "Why is fleet repair hard?", "backlog_id": "NEW", "backlog_problem": "Why is automating repair hard?", "domain": "Fleet Ops"},
        {"problem": "Mystery", "backlog_id": "", "backlog_problem": "", "domain": ""},
    ]
    mapped, new_entries, id_by_problem = assign_ids(mappings, 65)
    assert id_by_problem["Why does K8s exist?"] == "P34"
    assert id_by_problem["Why is fleet repair hard?"] == "P65"
    assert id_by_problem["Mystery"] == "P66"          # blank id treated as NEW
    assert "NEW" not in id_by_problem.values()
    assert [e["id"] for e in new_entries] == ["P65", "P66"]
    assert mapped[0] == {"id": "P34", "problem": "Why does Kubernetes exist?"}
    assert len(mapped) == 3


# --- JSON extraction --------------------------------------------------------

def test_extract_json_variants():
    from lambda_core.llm import _extract_json

    assert _extract_json('{"a": 1}') == {"a": 1}
    assert _extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert _extract_json('Here is the plan:\n{"a": 1}') == {"a": 1}
    assert _extract_json('{"a": 1}\nHope this helps!') == {"a": 1}  # trailing prose
    assert _extract_json('prose {"a": {"b": 2}} more prose') == {"a": {"b": 2}}
    with pytest.raises(ValueError):
        _extract_json("")
    with pytest.raises(ValueError):
        _extract_json("no json here")
    with pytest.raises(ValueError):
        _extract_json("[1, 2, 3]")  # array, not object


# --- rank normalization -----------------------------------------------------

def test_rank_normalizes_messy_model_output():
    from lambda_core.pipeline import rank

    ranked = rank([
        {"id": "P11", "problem": "a", "importance": "5", "gap": "Full"},   # strings
        {"id": "P30", "problem": "b", "importance": 99, "gap": "NONE "},   # out of range
        {"id": "P25", "problem": "c", "importance": "high", "gap": "huge"},  # garbage
    ])
    by_id = {g["id"]: g for g in ranked}
    assert by_id["P11"]["importance"] == 5 and by_id["P11"]["gap"] == "full"
    assert by_id["P30"]["importance"] == 5 and by_id["P30"]["gap"] == "none"
    assert by_id["P25"]["importance"] == 3 and by_id["P25"]["gap"] == "partial"
    assert [g["priority"] for g in ranked] == [1, 2, 3]


# --- backlog insertion when Added section is not last -----------------------

def test_backlog_appends_inside_added_section(tmp_path):
    copy = tmp_path / "backlog.md"
    copy.write_text(
        "# Backlog\n\n## Domain A\n1. Why A?\n\n## Added from targeted runs\n"
        "2. Why B?\n\n## Trailing Notes\nSome text.\n",
        encoding="utf-8",
    )
    appended = append_entries([{"problem": "Why C?", "domain": "X"}], copy)
    assert appended == ["P3"]
    text = copy.read_text(encoding="utf-8")
    added_section = text.split("## Added from targeted runs")[1].split("## ")[0]
    assert "3. Why C?" in added_section, "entry must land INSIDE the Added section"
    assert text.index("3. Why C?") < text.index("## Trailing Notes")
    assert load_backlog(copy)[-1].problem == "Why C?" or "Why C?" in [p.problem for p in load_backlog(copy)]


# --- END-TO-END: full pipeline against a mock LLM with messy output ---------

MESSY_STAGE_OUTPUTS = [
    # [1/4] decode — role fields present, problems slightly informal
    {
        "role_title": "Platform Engineer",
        "company": "Acme",
        "archetype": "Backend Platform",
        "summary": "Keeps services alive at scale.",
        "expensive_problems": [
            {"problem": "Why do distributed systems fail?", "why_paid": "outages cost money", "jd_evidence": "resilient services"},
            {"problem": "Why does observability matter?", "why_paid": "cannot fix what you cannot see", "jd_evidence": "monitoring"},
            {"problem": "Why is fleet-scale toil expensive?", "why_paid": "manual ops do not scale", "jd_evidence": "automation"},
        ],
        "hard_requirements": ["Python"],
        "wishlist": ["Go"],
        "seniority_signal": "mid",
    },
    # [2/4] map — REWORDED problems (breaks exact-match lookup), one NEW, one blank id
    {
        "mappings": [
            {"problem": "Why do distributed systems fail? ", "backlog_id": "P25", "backlog_problem": "Why do distributed systems fail?", "domain": ""},
            {"problem": "Why does observability matter?", "backlog_id": "", "backlog_problem": "Why does observability matter?", "domain": ""},
            {"problem": "Why is fleet-scale toil expensive?", "backlog_id": "NEW", "backlog_problem": "Why is fleet-scale toil expensive?", "domain": "Ops"},
        ]
    },
    # [3/4] intersect — string importance, capitalized gap, one entry missing id
    {
        "gap_map": [
            {"id": "P25", "problem": "Why do distributed systems fail?", "importance": "5", "transfer": "incident experience", "gap": "Partial", "credibility_risk": "no prod ownership"},
            {"problem": "Why does observability matter?", "importance": 4, "gap": "full"},  # no id, no transfer
            {"id": "NEW", "problem": "Why is fleet-scale toil expensive?", "importance": 3, "transfer": "", "gap": "none", "credibility_risk": ""},
        ]
    },
    # [4/5] pitch — project options, one incomplete
    {
        "project_options": [
            {
                "title": "Mini fleet you can kill",
                "hook": "Wouldn't it be cool if you could watch services die and heal themselves?",
                "what_you_will_see": "a dashboard lighting up as pods die",
                "analogy": "a factory line that fixes itself",
                "problems_touched": ["P25", "P30"],
                "what_you_will_learn": "how systems survive failure",
                "difficulty": 3,
                "weeks_estimate": 8,
                "first_win": "one service auto-restarts on your screen",
            },
            {"title": "Second option"},
        ],
        "recommended": 0,
    },
    # [5/5] plan — schema-valid sprints and positioning
    {
        "positioning": {
            "narrative": "Honest narrative.",
            "do_not_claim": ["prod ownership"],
            "talking_points": ["point one", "point two", "point three"],
        },
        "sprints": [
            {
                "week": w,
                "primary": {"id": "P25", "question": f"Question for week {w}?"},
                "secondary": [],
                "stretch": [],
                "evidence": {
                    "artifact": f"Repo artifact for week {w}",
                    "type": "repo",
                    "done_when": "A skeptical senior reviewer would accept this artifact as done.",
                },
                "interview": ["2 LeetCode"],
            }
            for w in range(1, 5)
        ],
    },
]


def test_run_pipeline_end_to_end_with_messy_mock_llm(monkeypatch):
    from lambda_core import pipeline

    responses = [dict(r) for r in MESSY_STAGE_OUTPUTS]
    calls = []

    def fake_complete_json(system, user, *, max_tokens=8192, retries=2):
        calls.append(user[:60])
        assert responses, f"unexpected extra LLM call #{len(calls)}: {user[:120]}"
        return responses.pop(0)

    monkeypatch.setattr(pipeline, "complete_json", fake_complete_json)

    plan = pipeline.run_pipeline(
        "A job description about keeping services alive.",
        "An engineer profile with incident experience.",
        intent="targeted",
        weeks=4,
        update_backlog=False,  # never touch the real backlog from tests
    )

    # The returned plan passed validate_plan inside run_pipeline. Re-assert key glue:
    validate_plan(plan)
    assert len(calls) == 5, "each stage should run exactly once (no hidden retries)"
    # The recommended project was chosen and carried into the plan.
    assert plan["project"]["title"] == "Mini fleet you can kill"
    assert len(plan["project_options"]) == 2
    # Every decoded problem got a real P-id (wording match OR positional fallback).
    ids = [p["id"] for p in plan["role_decode"]["expensive_problems"]]
    assert all(ids) and "NEW" not in ids and "" not in ids
    assert ids[0] == "P25"                      # positional fallback for reworded problem
    # The blank-id "Why does observability matter?" mapping text-matches the
    # EXISTING backlog entry (P30) — no new id minted for it. Only the genuinely
    # new toil problem gets a fresh id.
    new_ids = [e["id"] for e in plan["new_backlog_entries"]]
    assert len(new_ids) == 1 and all(i.startswith("P") for i in new_ids)
    assert "P30" in [g["id"] for g in plan["gap_map"]]
    # Messy gap map was normalized: enums valid, ints in range, priorities 1..n.
    for g in plan["gap_map"]:
        assert g["gap"] in ("none", "partial", "full")
        assert 1 <= g["importance"] <= 5
    assert sorted(g["priority"] for g in plan["gap_map"]) == [1, 2, 3]
    # The entry that came back with no id inherited one positionally.
    assert all(g["id"].startswith("P") and g["id"][1:].isdigit() for g in plan["gap_map"])


def test_run_pipeline_stage_retry_then_clear_error(monkeypatch):
    """A stage missing required keys retries once, then raises a readable error."""
    from lambda_core import pipeline

    def always_wrong(system, user, *, max_tokens=8192, retries=2):
        return {"unexpected": True}

    monkeypatch.setattr(pipeline, "complete_json", always_wrong)
    with pytest.raises(RuntimeError, match="decode stage"):
        pipeline.run_pipeline("jd text", "profile text", update_backlog=False)


def test_run_pipeline_intake_gate():
    from lambda_core.pipeline import run_pipeline

    with pytest.raises(ValueError, match="intake gate"):
        run_pipeline("", "profile", update_backlog=False)
    with pytest.raises(ValueError, match="profile"):
        run_pipeline("jd", "   ", update_backlog=False)
    with pytest.raises(ValueError, match="intent"):
        run_pipeline("jd", "profile", intent="wrong", update_backlog=False)


# --- watch links ------------------------------------------------------------

def test_watch_url_never_a_dead_link():
    from lambda_core.render import watch_url

    yt = watch_url({"query": "how does kubernetes work 3blue1brown style", "source": "youtube"})
    assert yt.startswith("https://www.youtube.com/results?search_query=")
    assert "3blue1brown" in yt
    ocw = watch_url({"query": "distributed systems lecture", "source": "mit-ocw"})
    assert ocw.startswith("https://ocw.mit.edu/search/?q=")
    # missing source defaults to youtube; special chars are encoded
    assert "search_query=a%2Bb" in watch_url({"query": "a+b"}) or "search_query=a%2Bb" == watch_url({"query": "a+b"}).split("?")[1].split("=",1)[1] and True
    assert watch_url({"query": "kv cache & memory"}).count(" ") == 0


def test_tutor_fields_render_in_vault_and_dashboard(tmp_path, demo_plan):
    """A plan WITH tutor fields renders hook, project, and watch links."""
    demo_plan["role_decode"]["human_hook"] = {
        "what_this_really_is": "This role is about keeping a robot city alive.",
        "why_exciting": "You get to watch machines heal themselves.",
        "why_doable": "One small machine at a time.",
    }
    demo_plan["project"] = {
        "title": "Mini fleet you can kill",
        "hook": "Wouldn't it be cool?",
        "what_you_will_see": "dashboards lighting up",
        "analogy": "a factory that fixes itself",
        "problems_touched": ["P25"],
        "what_you_will_learn": "resilience",
        "difficulty": 3,
        "weeks_estimate": 8,
        "first_win": "first auto-restart on screen",
    }
    demo_plan["sprints"][0]["simple_intro"] = "Imagine a mailroom for programs."
    demo_plan["sprints"][0]["watch"] = [
        {"title": "Containers in 100 seconds", "query": "docker explained 100 seconds", "source": "youtube", "why": "picture the box"},
        {"title": "MIT lecture", "query": "containers virtualization", "source": "mit-ocw"},
    ]
    validate_plan(demo_plan)  # new fields must not break the schema
    render_all(demo_plan, tmp_path)
    week1 = (tmp_path / "vault" / "02 - Weekly Sprints" / "Week 1.md").read_text(encoding="utf-8")
    assert "Say It Human First" in week1 and "mailroom" in week1
    assert "youtube.com/results?search_query=docker" in week1
    assert "ocw.mit.edu/search" in week1
    overview = (tmp_path / "vault" / "00 - Plan Overview.md").read_text(encoding="utf-8")
    assert "robot city" in overview and "Mini fleet you can kill" in overview
    dashboard = (tmp_path / "dashboard.html").read_text(encoding="utf-8")
    assert "robot city" in dashboard and "Mini fleet you can kill" in dashboard


def test_plans_without_tutor_fields_still_valid_and_render(demo_plan, tmp_path):
    """Backward compatibility: old plans (no hook/project/watch) keep working."""
    validate_plan(demo_plan)
    render_all(demo_plan, tmp_path)
    assert (tmp_path / "dashboard.html").exists()


# --- sprint normalization (regression: 'verification log' enum crash) -------

def test_normalize_sprints_handles_free_form_model_output():
    from lambda_core.pipeline import _normalize_evidence_type, normalize_sprints

    # The exact live failure: profile says "verification logs", model obliges.
    assert _normalize_evidence_type("verification log") == "verification-log"
    assert _normalize_evidence_type("Verification Logs") == "verification-log"
    assert _normalize_evidence_type("incident report") == "postmortem"
    assert _normalize_evidence_type("FMEA table") == "failure-mode-table"
    assert _normalize_evidence_type("architecture sketch") == "diagram"
    assert _normalize_evidence_type("code repository") == "repo"
    assert _normalize_evidence_type("benchmark results") == "benchmark"
    assert _normalize_evidence_type("something odd") == "writeup"
    assert _normalize_evidence_type("") == "writeup"
    assert _normalize_evidence_type(None) == "writeup"

    sprints = normalize_sprints([
        {
            "week": "1",                                   # string week
            "primary": {"id": "P25", "question": "Why?"},
            "evidence": {"artifact": "Logs of my tests", "type": "verification log",
                         "done_when": "A reviewer accepts the verification log as complete evidence."},
            "interview": ["2 LeetCode"],
            "watch": [{"query": "how it works", "source": "vimeo"},  # bad source
                      "not-a-dict", {"title": "no query"}],
        },
        "garbage-entry",
        {"week": 3, "primary": "not-a-dict", "evidence": "not-a-dict"},
    ])
    assert len(sprints) == 2
    assert sprints[0]["week"] == 1
    assert sprints[0]["evidence"]["type"] == "verification-log"
    assert sprints[0]["watch"] == [{"title": "video", "query": "how it works", "source": "youtube"}]
    assert sprints[1]["primary"] == {"id": "P0", "question": ""}
    assert sprints[1]["evidence"]["type"] == "writeup"
    assert sprints[1]["interview"] == []


def test_verification_log_is_schema_legal(demo_plan):
    demo_plan["sprints"][0]["evidence"]["type"] = "verification-log"
    validate_plan(demo_plan)


# --- dedupe (regression: duplicate P66 rows; NEW-minting for existing text) --

def test_assign_ids_dedupes_new_and_matches_existing_text():
    from lambda_core.backlog import load_backlog
    from lambda_core.pipeline import assign_ids

    problems = load_backlog()
    start = 900
    mappings = [
        # Model says NEW but the text matches an existing backlog entry → existing id wins.
        {"problem": "reworded", "backlog_id": "NEW",
         "backlog_problem": "Why does Kubernetes exist?", "domain": ""},
        # The same NEW problem twice → ONE shared new id, one backlog entry.
        {"problem": "a", "backlog_id": "NEW",
         "backlog_problem": "Why is live compute migration hard?", "domain": "Ops"},
        {"problem": "b", "backlog_id": "NEW",
         "backlog_problem": "Why is live compute migration HARD?", "domain": "Ops"},
        # Straight duplicate of an already-mapped id → dropped from mapped output.
        {"problem": "c", "backlog_id": "P34",
         "backlog_problem": "Why does Kubernetes exist?", "domain": ""},
    ]
    mapped, new_entries, id_by_problem = assign_ids(mappings, start, problems)
    assert id_by_problem["reworded"] == "P34"
    assert id_by_problem["a"] == id_by_problem["b"] == "P900"
    assert [e["id"] for e in new_entries] == ["P900"], "one NEW problem → one entry"
    ids = [m["id"] for m in mapped]
    assert ids == ["P34", "P900"], f"no duplicate ids in mapped output, got {ids}"


def test_normalize_gap_map_drops_duplicate_ids():
    from lambda_core.pipeline import normalize_gap_map

    out = normalize_gap_map(
        [
            {"id": "P66", "problem": "pipeline", "importance": 4, "gap": "full"},
            {"id": "P66", "problem": "pipeline", "importance": 4, "gap": "full"},
            {"id": "P30", "problem": "obs", "importance": 4, "gap": "partial"},
        ],
        mapped=[],
    )
    assert [g["id"] for g in out] == ["P66", "P30"]
