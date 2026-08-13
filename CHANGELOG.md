# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2](https://github.com/fabiocicerchia/arch-map/compare/v0.1.1...v0.1.2) (2026-08-13)


### Bug Fixes

* security and code-quality findings ([#28](https://github.com/fabiocicerchia/arch-map/issues/28)) ([3e7fbbe](https://github.com/fabiocicerchia/arch-map/commit/3e7fbbe51d1793d5261697c054b1403ed04a41d0))

## [0.1.1](https://github.com/fabiocicerchia/arch-map/compare/v0.1.0...v0.1.1) (2026-08-06)


### Bug Fixes

* **pre-commit:** stop check-yaml failing on Helm templates and multi-doc manifests ([09fb6c0](https://github.com/fabiocicerchia/arch-map/commit/09fb6c08f00c5238fbdb27f66a14fae0758f0740))
* **security:** skip the SARIF upload on private repos ([6c6b7d5](https://github.com/fabiocicerchia/arch-map/commit/6c6b7d551dddafcd54a1299ee466b421925c64da))

## [Unreleased]

## [0.1.0]

### Added

- Terraform state parsing (classic and `terraform show -json` shapes).
- Kubernetes workloads/services/ingress discovery via `kubectl`.
- Mermaid flowchart output to `ARCHITECTURE.md`, grouped by kind with
  ingress→service edges wired from selectors.

[Unreleased]: https://github.com/fabiocicerchia/arch-map/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fabiocicerchia/arch-map/releases/tag/v0.1.0
