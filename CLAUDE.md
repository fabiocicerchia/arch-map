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
make help    # Show this help
make setup   # Install the pre-commit hook
make install # Install the package
```

## Tooling

Shared config — the GitHub workflows, `.pre-commit-config.yaml`,
`.editorconfig`, `.hadolint.yaml`, `SECURITY.md` — comes from
[repo-skeleton](https://github.com/fabiocicerchia/repo-skeleton). Edit it
there, not here; a local edit is drift and the next sync overwrites it.
`check-drift.sh` in that repo reports what has diverged.

- `make setup` installs the pre-commit hook, and that is the whole of it.
  Don't add a `.githooks/` directory: `core.hooksPath` replaces `.git/hooks/`
  wholesale, so setting it silently stops every pre-commit hook from running.
- Hooks are pinned by commit SHA with the tag in a trailing comment. A tag can
  be moved, a SHA cannot.
- CI runs this same `.pre-commit-config.yaml` through `pre-commit/action`, so
  what passes locally is what gates the pull request.

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
