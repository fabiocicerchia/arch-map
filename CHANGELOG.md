# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2026-07-29)


### Features

* add --format plantuml/d2 output ([564c22c](https://github.com/fabiocicerchia/arch-map/commit/564c22c0f6c7e9f998d8798bc1ed673e2c5e816f))
* add --level context|container|component C4 levels ([1632d1f](https://github.com/fabiocicerchia/arch-map/commit/1632d1fd3dee0d73ac7fbc2c35cc6aa1f46dea7e))
* add Alibaba Cloud, OCI, and OVH resource types ([f595193](https://github.com/fabiocicerchia/arch-map/commit/f5951932c55a300011bc93e8d8f47cecce198527))
* add diagram legend and broaden k8s-to-datastore edge matching ([3b960e0](https://github.com/fabiocicerchia/arch-map/commit/3b960e04f14ac11b09f2c16e1e5ebc4af0a6e812))
* add DigitalOcean, Linode/Akamai, Cloudflare, Vultr, and IBM Cloud resource types ([338d9e8](https://github.com/fabiocicerchia/arch-map/commit/338d9e8574e4311de50125c1495133b684d50f58))
* add GCP/Azure TF resource mappings and module grouping ([e0c80e3](https://github.com/fabiocicerchia/arch-map/commit/e0c80e38f8a4e58750433a660696a7b2c52455da))
* add Hetzner Cloud and Scaleway resource types ([1957eff](https://github.com/fabiocicerchia/arch-map/commit/1957eff2f83042bdbfce38b6a1fe96ddb24e6af2))
* add install.sh one-liner installer ([4858aa1](https://github.com/fabiocicerchia/arch-map/commit/4858aa1083005760536cbeb41548343ef3eaa264))
* derive edges from terraform state resource dependencies ([5684f17](https://github.com/fabiocicerchia/arch-map/commit/5684f17450110da0e410a568c3618be519852482))
* infer service-&gt;datastore edges from DSN env vars ([6bad40a](https://github.com/fabiocicerchia/arch-map/commit/6bad40a745dacc7df104d4b82738334ff2d8c3f4))


### Bug Fixes

* restore executable bit and apply ruff-format ([#11](https://github.com/fabiocicerchia/arch-map/issues/11)) ([a5cee1b](https://github.com/fabiocicerchia/arch-map/commit/a5cee1b845c3956a91002a396a74d732db1fc76b))
* sanitize() strip any non-alphanumeric char, not a fixed list ([4b83914](https://github.com/fabiocicerchia/arch-map/commit/4b839147986189992e9d87b4fcef7da9c1671f5f))


### Documentation

* add GitHub Pages site, trim completed roadmap items from README ([cef4c0a](https://github.com/fabiocicerchia/arch-map/commit/cef4c0a331116a820902d253d69ced980dd8024a))
* add missing README badges ([849bd78](https://github.com/fabiocicerchia/arch-map/commit/849bd780558a3ab61823b44e85bd77ba8b336842))
* remove the broken FOSSA badge ([ab32afd](https://github.com/fabiocicerchia/arch-map/commit/ab32afd89ec1be6647f8b8404b1e9b54cb33a6ef))

## [Unreleased]

## [0.1.0]

### Added

- Terraform state parsing (classic and `terraform show -json` shapes).
- Kubernetes workloads/services/ingress discovery via `kubectl`.
- Mermaid flowchart output to `ARCHITECTURE.md`, grouped by kind with
  ingress→service edges wired from selectors.

[Unreleased]: https://github.com/fabiocicerchia/arch-map/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fabiocicerchia/arch-map/releases/tag/v0.1.0
