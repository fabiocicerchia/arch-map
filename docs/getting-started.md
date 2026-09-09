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

## Exit codes

A CI job that regenerates the diagram has to tell "the state file was unusable"
from "the diagram changed", so each expected failure has its own code from
`sysexits(3)`:

| Code | Meaning                                                                                              |
| ---- | ---------------------------------------------------------------------------------------------------- |
| 0    | the diagram was written                                                                              |
| 2    | argparse rejected the command line                                                                   |
| 65   | the state file is not valid JSON, is nested too deeply, or is valid JSON that is not terraform state |
| 66   | the state file does not exist                                                                        |
| 74   | the state file exists but could not be read                                                          |

A truncated `terraform state pull` is the usual way to see 65. It prints one
line naming the file and what was wrong with it — never a traceback.
