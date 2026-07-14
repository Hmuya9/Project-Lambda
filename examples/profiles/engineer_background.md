# Engineer profile

## Background

Systems / infrastructure engineer with ~7 years building and operating
distributed production platforms. Strongest in Kubernetes, Linux networking,
observability, and Python services. Comfortable owning on-call and translating
vague reliability pain into concrete capacity and latency work.

## Recent relevant work

- Owned a Kubernetes platform serving latency-sensitive APIs (~50k RPS peak)
  with p99 budgets, autoscaling, and multi-AZ failover.
- Built an internal job/queue system for batch + online workloads; introduced
  backpressure, DLQs, and queue-depth–driven autoscaling.
- Instrumented production services with OpenTelemetry + Prometheus; reduced
  mean time to diagnose by improving span coverage on the critical path.
- Migrated a Python microservice fleet to greener resource requests; cut idle
  CPU waste ~30% while keeping error budgets green.
- Debugged kernel/network-adjacent issues (conntrack exhaustion, DNS tail
  latency, noisy-neighbor IO) under incident pressure.

## GPU / ML infra exposure (honest)

- Limited direct GPU fleet ownership. Have run CUDA containers on Kubernetes
  for internal experiment workers, but not owned multi-node LLM training.
- Familiar with inference concepts (batching, KV cache pressure, cold starts)
  from reading systems papers and staging a small vLLM demo, not from
  production LLM serving ownership.
- Strong transfer skills from non-ML serving: load shedding, admission control,
  capacity planning, and SLO design.

## Strengths

- Turning ambiguous outages into reproducible failure modes and fixes
- Writing clear runbooks and capacity models others can execute
- Preference for measurable bars (latency, cost, utilization) over vibes

## Gaps I want proof for

- Production LLM serving ownership (autoscaling, KV cache, multi-model routing)
- GPU scheduling / utilization economics at fleet scale
- Partnering with research to ship model changes behind stable serving contracts
