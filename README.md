# arch-map

[![CI](https://github.com/fabiocicerchia/arch-map/actions/workflows/ci.yml/badge.svg)](https://github.com/fabiocicerchia/arch-map/actions/workflows/ci.yml)
[![Security](https://github.com/fabiocicerchia/arch-map/actions/workflows/security.yml/badge.svg)](https://github.com/fabiocicerchia/arch-map/actions/workflows/security.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/fabiocicerchia/arch-map/badge)](https://securityscorecards.dev/viewer/?uri=github.com/fabiocicerchia/arch-map)
[![CI carbon](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/fabiocicerchia/arch-map/gh-pages/badge.json)](.github/workflows/carbon-badge.yml)
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

## Features

- Built from real infrastructure — Terraform state and live Kubernetes
  resources — rather than a hand-drawn source of truth that drifts.
- Emits GitHub-native **Mermaid** into `ARCHITECTURE.md`, so it renders in the
  repo with no diagramming tool in the loop.
- Groups nodes by kind: workloads with replica counts, ingresses with
  hostnames, databases, queues, buckets and caches.
- Wires ingress→service edges from **selectors**, not from naming conventions.
- Works from either source alone — `--tfstate` on its own needs no cluster
  access.
- Made to be regenerated in CI, which turns the diagram diff into an
  architecture-change review artifact: "this PR adds a queue" becomes visible.

## Install

```sh
pipx install git+https://github.com/fabiocicerchia/arch-map
```

Or with pip:

```sh
pip install --user git+https://github.com/fabiocicerchia/arch-map
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

## Verifying the image

Every published image is signed with [cosign][cosign], keyless: the identity in
the signature is the workflow that published it, not a key anybody holds.

```sh
cosign verify ghcr.io/fabiocicerchia/arch-map:latest \
  --certificate-identity-regexp \
    'https://github.com/fabiocicerchia/arch-map/.github/workflows/.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

`no signatures found` means the tag predates signing, not that verification was
set up wrongly — a wrong identity or issuer says so explicitly. Re-run the
publish workflow for that tag to sign it.

[cosign]: https://docs.sigstore.dev/

## Development

`make dev` then `make test` / `make lint`. Run `make setup` once to install the
git hooks and pre-commit. Full docs live in [`docs/`](docs/); runnable examples
in [`examples/`](examples/).

## Usage

```sh
# From Terraform state + a live namespace:
arch-map --tfstate <(terraform show -json) --k8s production -o ARCHITECTURE.md

# Terraform only:
arch-map --tfstate infra.tfstate -o ARCHITECTURE.md
```

More in [`docs/getting-started.md`](docs/getting-started.md).

## Documentation

Full docs live in [`docs/`](docs/). Runnable examples live in [`examples/`](examples/).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). By participating you agree to the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) — please don't open a
public issue.

## Support

Need help implementing this? [Get in touch](https://fabiocicerchia.it/contact).

## License

Apache 2.0 — see [LICENSE](LICENSE).
