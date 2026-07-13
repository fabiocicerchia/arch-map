# Architecture

arch-map is a single-file, stdlib-only CLI. It reads two kinds of source,
normalizes them into a flat list of typed nodes and edges, and renders Mermaid.

## Overview

```
Terraform state ─┐
                 ├─▶ nodes + edges ─▶ Mermaid flowchart ─▶ ARCHITECTURE.md
kubectl (K8s) ───┘
```

## Components

- **Terraform reader** — parses both classic state and `terraform show -json`
  shapes. `TF_KINDS` maps resource types (e.g. `aws_db_instance`) to a node
  kind + label prefix.
- **Kubernetes reader** — shells out to `kubectl` for workloads, services and
  ingresses in a namespace; captures replica counts and ingress hostnames.
- **Renderer** — groups nodes by kind and emits a Mermaid `flowchart`, wiring
  ingress→service edges from label selectors.

## Data flow

1. Collect resources from each requested source.
2. Map each to a node (kind, id, label) and derive edges.
3. Group by kind and serialize to Mermaid, written to the `-o` target.

## Decisions

- **Stdlib only** (`dependencies = []`) — keeps install trivial and the tool
  safe to drop into any CI job.
- **Mermaid output** — renders natively on GitHub, so the diagram lives in the
  repo and its diffs double as architecture-change review.

Record further significant choices here (or in a `docs/adr/` folder if they
pile up).
