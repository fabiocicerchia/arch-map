# Getting Started

## Prerequisites

- Python 3.10+
- `kubectl` configured against your cluster (only for the `--k8s` source)
- A Terraform state file, or `terraform show -json` output (only for `--tfstate`)

## Install

```sh
pip install arch-map
```

## Run

```sh
# From Terraform state + a live namespace:
arch-map --tfstate <(terraform show -json) --k8s production -o ARCHITECTURE.md

# Terraform only:
arch-map --tfstate infra.tfstate -o ARCHITECTURE.md
```

The output is a GitHub-native Mermaid flowchart. Commit `ARCHITECTURE.md` and
regenerate it in CI so the diagram tracks what's actually deployed.
