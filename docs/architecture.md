# Architecture

arch-map is a single-file, stdlib-only CLI. It reads two kinds of source,
normalizes them into a flat list of typed nodes and edges, and renders Mermaid
(default), PlantUML or D2.

## Overview

```
Terraform state ─┐
                 ├─▶ nodes + edges ─▶ Mermaid flowchart ─▶ ARCHITECTURE.md
kubectl (K8s) ───┘
```

## Components

- **Terraform reader** — one reader per state shape: `_nodes_from_show_json` /
  `_edges_from_show_json` for `terraform show -json`, `_nodes_from_classic_state`
  / `_edges_from_classic_state` for a classic flat state file. `nodes_from_tfstate`
  and `edges_from_tfstate` pick between them. `TF_KINDS` maps resource types
  (e.g. `aws_db_instance`) to a node kind + label prefix.
- **Kubernetes reader** — one reader per resource kind (`_k8s_workloads`,
  `_k8s_selectors`, `_k8s_ingresses`), each shelling out through `_kubectl_get`;
  captures replica counts, container env values and ingress hostnames.
- **Env-var heuristic** — `edges_from_env_dsns` guesses service→datastore edges
  from a workload's env values in two named passes: `_datastore_in_host` for
  DSN-style values, then `_datastore_in_value` for whole-token name matches.
- **Renderers** — `to_mermaid` (default), `to_plantuml` and `to_d2`, selected
  through `RENDERERS`. All three group nodes with the shared `_by_kind` so the
  formats cannot drift into different orderings; only Mermaid draws Terraform
  module subgraphs. Ingress→service edges are wired from label selectors.

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
