# arch-map

[![CI](https://github.com/fabiocicerchia/arch-map/actions/workflows/ci.yml/badge.svg)](https://github.com/fabiocicerchia/arch-map/actions/workflows/ci.yml)
[![Security](https://github.com/fabiocicerchia/arch-map/actions/workflows/security.yml/badge.svg)](https://github.com/fabiocicerchia/arch-map/actions/workflows/security.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/fabiocicerchia/arch-map/badge)](https://securityscorecards.dev/viewer/?uri=github.com/fabiocicerchia/arch-map)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Ffabiocicerchia%2Farch-map.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Ffabiocicerchia%2Farch-map?ref=badge_shield)
[![Release](https://img.shields.io/github/v/release/fabiocicerchia/arch-map)](https://github.com/fabiocicerchia/arch-map/releases)

A **living C4-style container diagram generated from your real
infrastructure** — Terraform state + live Kubernetes resources — as Mermaid
in `ARCHITECTURE.md`, committed to the repo and regenerated in CI. Diagrams
that can't rot, because they're built from what's actually running.

```sh
arch-map --tfstate <(terraform show -json) --k8s production -o ARCHITECTURE.md
```

Produces a GitHub-native Mermaid flowchart: workloads (with replica counts),
ingresses with hostnames, databases, queues, buckets, caches and edges —
grouped by kind, ingress→service edges wired from selectors.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/fabiocicerchia/arch-map/main/install.sh | bash
```

Or with pipx directly:

```sh
pipx install git+https://github.com/fabiocicerchia/arch-map
```

## CI recipe

```yaml
- run: terraform show -json > state.json
- run: arch-map --tfstate state.json --k8s production -o ARCHITECTURE.md
- run: |
    git diff --quiet ARCHITECTURE.md || {
      git add ARCHITECTURE.md
      git commit -m "docs: refresh architecture diagram"
      git push
    }
```

Bonus: the diff itself is an architecture-change review artifact — "this PR
adds a queue" is visible in the diagram diff.

## Status & roadmap

- [x] Terraform state (both classic and `show -json` shapes), K8s
      workloads/ingress, Mermaid out
- [x] Service→datastore edges from env-var heuristics (DSN parsing)
- [x] C4 levels: `--level context|container|component`
- [x] More TF providers (GCP/Azure mappings), module grouping
- [x] PlantUML/D2 output

## Development

`make dev` then `make test` / `make lint`. Run `make setup` once to install the
git hooks and pre-commit. Full docs live in [`docs/`](docs/); runnable examples
in [`examples/`](examples/).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). By participating you agree to the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) — please don't open a
public issue.

## License

Apache 2.0 — see [LICENSE](LICENSE).
