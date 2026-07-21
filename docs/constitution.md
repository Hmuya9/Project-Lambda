# Project Lambda — Constitution (Framework, v1.0)

Project Lambda is a framework for structuring study around what the market actually pays for. It is profile-agnostic and goal-agnostic: **nothing is tailored until a user has entered their profile and their market intent.** Lambda is not "come become a better software engineer" — though it can be, if that is the user's stated intent.

## The Thesis (invariant)

**Jobs pay for proximity to an expensive problem — not for knowing Python or Rust** (though tools matter as means). An employable person is one who can stand close to a problem that costs a company real money, understand it, act on it, and prove it. Everything in Lambda exists to move the user closer to expensive problems and to produce evidence of that proximity.

## What a Lambda instance is

```
Lambda instance = Constitution (this doc, fixed)
                + Profile      (who the user is: background, strengths, real experience, gaps, constraints)
                + Intent       (what they want from the market)
                + Backlog      (the expensive problems relevant to that intent)
                + Plan         (sprints + evidence, generated from the four above)
```

The Constitution never changes per user. The Profile and Intent are the user's inputs. The Backlog is derived from the market for that intent. The Plan is derived from all of it. Tailoring before Profile + Intent are captured is a framework violation.

## Intent (captured before anything else)

1. **Targeted** — "I want this job" (a specific job description). The JD is decoded into expensive problems.
2. **Directional** — "I want to be highly employable in domain X." A market composite of that domain's postings replaces the single JD.
3. **Exploratory** — "I want to become a more valuable engineer overall and understand where the money is going." The composite spans the user's plausible domains, and part of the early work is narrowing intent.

Intent can change; when it does, the mapping is regenerated — the framework is not.

## Scope

Initial scope is engineers (start small). The framework itself carries no engineering-specific assumptions beyond "expensive problems exist and evidence can be produced" — it may expand to other fields later.

## The Learning Pipeline

```
Expensive Problem → Question → Mental Model → Principles → Technologies → Implementation → Evidence
```

Nothing is learned in isolation. Every completed question becomes a node in a growing knowledge graph. Technologies enter only when a problem requires them.

## The Process (per question)

1. **Ask** — one primary question per sprint. If the question is unclear, the work is unclear.
2. **Build the Mental Model** — picture the system before studying its implementation.
3. **Understand** — study only what is necessary to answer the question.
4. **Observe** — reverse engineer an existing implementation: why this design, what constraints, what tradeoffs, what alternatives.
5. **Build** — smallest implementation that proves understanding; prefer run → modify → improve over from-scratch.
6. **Improve** — one meaningful improvement, for an engineering reason.
7. **Explain** — teachable or it isn't done.

## Sprint Operating System

Weekly sprints: Primary Objective (must answer), Secondary (if early), Stretch (if time remains). Some questions take two days, some two weeks; the schedule adapts, the mission does not. Continuous interview practice scaled to the intent. Every week produces evidence.

## Completion Criteria

A question is complete only when: the problem is understood; why the solution exists is understood; a real implementation was explored; something was built or modified; tradeoffs can be explained; evidence exists. Knowledge without evidence is incomplete.

## Retention

One page per completed question: what problem existed, why this solution was created, how it solves the problem, what tradeoffs it introduces, where the user has applied or observed it, and whether they can explain it in under two minutes.

## The Rules

1. Build before consuming more content.
2. Understand before optimizing.
3. Ship before polishing.
4. Evidence beats certificates.
5. One finished project beats five unfinished ideas.
6. Never study a technology in isolation.
7. Every week must produce evidence.
8. Every new topic must connect to something already understood.
9. Begin with the expensive problem; work backward to the technologies.
10. The market pays for proximity to expensive problems — not for the longest list of technologies.

## Honesty Constraint

Plans and positioning may only claim what the profile states. Gaps are framed as gaps being closed with evidence, never hidden and never invented over.

## Change Control

The framework is under change control: capture improvement ideas, but do not redesign mid-flight. Modify only at sprint-4 boundaries unless execution reveals a major flaw. The system exists to produce a more valuable person, not a more elaborate system.

## Final Principle

The goal each week is not to study more. The goal is to become more valuable — measured by proximity to expensive problems and the evidence that proves it.
