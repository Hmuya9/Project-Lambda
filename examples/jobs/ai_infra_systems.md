# AI Infrastructure / Systems Engineer

## About the role

We are hiring a Senior AI Infrastructure Engineer to own the systems that train,
serve, and observe large language model workloads in production. You will work
across GPU clusters, model serving, data pipelines, and reliability — with a
bias toward measurable latency, cost, and uptime outcomes.

## What you'll do

- Design and operate GPU training and inference infrastructure on Kubernetes
- Build and harden model serving paths (vLLM / Triton / custom runtimes)
- Own end-to-end latency budgets from API gateway → scheduler → GPU → response
- Improve utilization and $/token economics across multi-tenant workloads
- Build observability for queue depth, token throughput, cold starts, and
  GPU memory pressure
- Partner with research and product to ship new models without breaking SLOs
- Lead incident response for inference outages and capacity cliffs

## Requirements

- 5+ years systems / infrastructure / distributed systems experience
- Deep experience with Kubernetes, Linux, networking, and containers
- Hands-on with CUDA-aware workloads, GPU scheduling, or ML serving
- Strong Python and comfort reading / writing Go or Rust for systems glue
- Proven ownership of production SLOs (availability, latency, error budgets)
- Experience with Prometheus/Grafana/OpenTelemetry or equivalent stacks
- Ability to debug messy production failures under time pressure

## Nice to have

- Experience running multi-node LLM training (FSDP / DeepSpeed / Megatron)
- Prior work on autoscaling for bursty inference traffic
- Familiarity with cost attribution for shared GPU fleets
- Contributions to open-source inference or orchestration tooling

## Success in the first 6 months

- Reduce p95 inference latency by a measurable margin on our flagship endpoint
- Raise GPU utilization without violating latency SLOs
- Ship a serving platform change that research engineers can adopt safely
- Document runbooks and capacity plans that on-call can execute without you
