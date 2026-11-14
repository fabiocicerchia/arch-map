# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3](https://github.com/fabiocicerchia/arch-map/compare/v0.2.2...v0.2.3) (2026-11-14)


### Bug Fixes

* **ci:** keep actions: read on the job that uploads sarif ([#106](https://github.com/fabiocicerchia/arch-map/issues/106)) ([e4c7aad](https://github.com/fabiocicerchia/arch-map/commit/e4c7aad3316b9e5a36226c5582e5299ac3faa913))
* **coc:** restore the reporting address and the version deep-link ([#90](https://github.com/fabiocicerchia/arch-map/issues/90)) ([0fdb36e](https://github.com/fabiocicerchia/arch-map/commit/0fdb36e0dafeef5f4129930dedbacf24f43e3bb7))
* **release:** create the release with RELEASE_PLEASE_TOKEN, not GITHUB_TOKEN ([#114](https://github.com/fabiocicerchia/arch-map/issues/114)) ([809bc1f](https://github.com/fabiocicerchia/arch-map/commit/809bc1f1c9e4ec387124f4e1c517ab78806923fc))
* **release:** grant id-token on the job that calls the signing workflow ([#88](https://github.com/fabiocicerchia/arch-map/issues/88)) ([5bf39d0](https://github.com/fabiocicerchia/arch-map/commit/5bf39d0aec0a80c95b20ee8dd8d3266ffdbebdf1))
* **release:** let the release PR carry a token that isn't GITHUB_TOKEN ([#91](https://github.com/fabiocicerchia/arch-map/issues/91)) ([8b2f24e](https://github.com/fabiocicerchia/arch-map/commit/8b2f24e39234017cbde2501d0e0577599670dcee))


### Documentation

* add a Features section to the README ([#92](https://github.com/fabiocicerchia/arch-map/issues/92)) ([b5c99c4](https://github.com/fabiocicerchia/arch-map/commit/b5c99c41aa98804a27833286ea9f258836d8e445))

## [0.2.2](https://github.com/fabiocicerchia/arch-map/compare/v0.2.1...v0.2.2) (2026-09-09)


### Bug Fixes

* **ci:** pin the editorconfig-checker binary version ([#66](https://github.com/fabiocicerchia/arch-map/issues/66)) ([d9e995b](https://github.com/fabiocicerchia/arch-map/commit/d9e995b483efb523e723836b018da798e76781d8))


### Documentation

* drop the curl | sh installer, document the direct install ([#74](https://github.com/fabiocicerchia/arch-map/issues/74)) ([63b66be](https://github.com/fabiocicerchia/arch-map/commit/63b66beb63f7ff0d8983ee653ae608b883cf3314))

## [0.2.1](https://github.com/fabiocicerchia/arch-map/compare/v0.2.0...v0.2.1) (2026-08-29)

### Bug Fixes

- unblock quality and clear the Scorecard pinned-dependencies finding ([#51](https://github.com/fabiocicerchia/arch-map/issues/51)) ([e01e751](https://github.com/fabiocicerchia/arch-map/commit/e01e7510230d698ee395db83f86d56e7e09c2a15))

## [0.2.0](https://github.com/fabiocicerchia/arch-map/compare/v0.1.2...v0.2.0) (2026-08-25)

### Features

- **docs:** build the docs site in Actions and drop Read the Docs ([#42](https://github.com/fabiocicerchia/arch-map/issues/42)) ([e36fb93](https://github.com/fabiocicerchia/arch-map/commit/e36fb934cacaef2d2f5595fcef912d8b417c95ff))

### Bug Fixes

- **ci:** compute the next release PR after the draft is published ([#39](https://github.com/fabiocicerchia/arch-map/issues/39)) ([efdfe3e](https://github.com/fabiocicerchia/arch-map/commit/efdfe3e83d8e9bee578a7cee5900276d02511176))

## [0.1.2](https://github.com/fabiocicerchia/arch-map/compare/v0.1.1...v0.1.2) (2026-08-13)

### Bug Fixes

- security and code-quality findings ([#28](https://github.com/fabiocicerchia/arch-map/issues/28)) ([3e7fbbe](https://github.com/fabiocicerchia/arch-map/commit/3e7fbbe51d1793d5261697c054b1403ed04a41d0))

## [0.1.1](https://github.com/fabiocicerchia/arch-map/compare/v0.1.0...v0.1.1) (2026-08-06)

### Bug Fixes

- **pre-commit:** stop check-yaml failing on Helm templates and multi-doc manifests ([09fb6c0](https://github.com/fabiocicerchia/arch-map/commit/09fb6c08f00c5238fbdb27f66a14fae0758f0740))
- **security:** skip the SARIF upload on private repos ([6c6b7d5](https://github.com/fabiocicerchia/arch-map/commit/6c6b7d551dddafcd54a1299ee466b421925c64da))

## [Unreleased]

## [0.1.0]

### Added

- Terraform state parsing (classic and `terraform show -json` shapes).
- Kubernetes workloads/services/ingress discovery via `kubectl`.
- Mermaid flowchart output to `ARCHITECTURE.md`, grouped by kind with
  ingress→service edges wired from selectors.

[Unreleased]: https://github.com/fabiocicerchia/arch-map/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fabiocicerchia/arch-map/releases/tag/v0.1.0
