# CLAUDE.md

Guidance for Claude Code (and other AI agents) working in this repo.

## Project

arch-map is a single-file Python 3.10+ CLI (`arch_map.py`, entry point
`arch_map:main`) that generates a living C4-style Mermaid diagram from
Terraform state and live Kubernetes resources, written to `ARCHITECTURE.md`
and regenerated in CI. No runtime dependencies; stdlib only.

## Commands

```sh
make dev     # editable install with dev deps (pytest, ruff, build)
make test    # pytest -q
make lint    # ruff check .
make build   # python -m build
```

## Conventions

- Match existing style; don't reformat unrelated code. Ruff, line length 100.
- Keep it stdlib-only — `dependencies = []` is a feature, not an accident.
- Update docs/ and examples/ with behavior changes. Don't hand-edit CHANGELOG.md
  or the pyproject version — release-please generates both from commit messages.
- Use Conventional Commits (`feat:`/`fix:`/…); they drive the release version bump.
- Never commit secrets; CI runs gitleaks/trivy. Keep `.env` out of git.

## Guardrails

- Don't add dependencies without a clear reason; prefer stdlib.
- Don't touch generated files (`*.egg-info/`, caches) by hand.
- Ask before large refactors or destructive operations.
