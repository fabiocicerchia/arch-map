# Contributing

Thanks for taking the time to contribute to arch-map!

## Development setup

You need Python 3.10+ and `make`.

```sh
make dev     # editable install with dev dependencies (pytest, ruff, build)
make setup   # git hooks + pre-commit (secret scanning, ruff)
make lint    # ruff check .
make test    # pytest
```

## Making changes

- Keep changes focused; one logical change per PR, keeping the existing style.
- Add or update tests, and update `docs/` and `examples/` when behavior changes.
- Ensure `make lint`, `make test`, and CI (`code-quality` + `security`) pass.

Don't edit `CHANGELOG.md` or the version in `pyproject.toml` by hand — both are
generated from commit messages by release-please (see [Releases](#releases)).

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`,
`fix:`, `docs:`, `chore:`, etc. This keeps history readable and drives the
version bump: `fix:` → patch, `feat:` → minor, `feat!:` or a
`BREAKING CHANGE:` footer → major.

## Pull requests

Fill out the PR template, link related issues, and request review. Be kind.

## Releases

Releases are automated by [release-please](.github/workflows/release.yml); you
don't tag or edit the changelog manually.

1. Merge `feat:`/`fix:` PRs into `main` as normal — **no tag is created**.
1. release-please keeps an open **release PR** ("chore: release X.Y.Z"),
   recalculating the next version + `CHANGELOG.md` on every merge.
1. **Merge the release PR** to ship: that (and only that) creates the `vX.Y.Z`
   tag and GitHub Release, then builds the sdist/wheel and — if
   `PUBLISH_TO_PYPI` is set — publishes to PyPI.

## License

By contributing you agree that your contributions are licensed under the
Apache License 2.0 (see `LICENSE`).
