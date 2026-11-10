# Specifications of arch-map

What this code does, one atomic Gherkin scenario per behaviour, read from the code by code-atlas.
Tags: `@verified` a test asserts it · `@inferred` read from the code only · `@gap` an entry point no test covers · `@human` written or amended by a person, never rewritten.

## Architecture views
Choosing how much detail the C4-style diagram shows.

- **System context view**: [Choosing the C4 level](architecture-views/context-view/c4-levels.feature) (2)

## Command line
How someone runs arch-map and gets the generated document back.

- **Generated document**: [Writing the generated document](command-line/generated-document/generated-document.feature) (2)
- **Source selection**: [Selecting sources](command-line/source-selection/source-selection.feature) (2)

## Connection inference
Working out which workloads talk to which datastores when nothing records it explicitly.

- **Connection-string links**: [Inferring workload-to-datastore connections](connection-inference/connection-string-links/connection-inference.feature) (3)

## Developer tooling
Building, checking, packaging and shipping arch-map.

- **Container image**: [Running arch-map from its container image](developer-tooling/container-image/container-image.feature) (3)

## Diagram output
Turning the inventory into a diagram in a chosen syntax.

- **Grouping, shapes and legend**: [Grouping, shapes and legend](diagram-output/grouping-and-legend/grouping-and-legend.feature) (2)
- **Mermaid diagrams**: [Mermaid diagrams](diagram-output/mermaid/mermaid-diagrams.feature) (1)
- **PlantUML diagrams**: [PlantUML and D2 diagrams](diagram-output/plantuml/plantuml-and-d2-diagrams.feature) (2)

## Kubernetes discovery
Building the architecture inventory from a live Kubernetes namespace.

- **Cluster access**: [Reaching the cluster through kubectl](kubernetes-discovery/cluster-access/cluster-access.feature) (1)
- **Workloads**: [Discovering a live Kubernetes namespace](kubernetes-discovery/workloads/kubernetes-discovery.feature) (3)

## Terraform discovery
Building the architecture inventory from Terraform state files.

- **Cloud resource recognition**: [Recognising cloud resources](terraform-discovery/cloud-resource-catalog/cloud-resource-recognition.feature) (1)
- **Resource dependencies**: [Linking resources by recorded dependencies](terraform-discovery/dependency-links/resource-dependencies.feature) (1)
- **State formats and modules**: [Reading classic and show-json state, including modules](terraform-discovery/state-formats/state-formats-and-modules.feature) (2)
- **State file loading**: [Rejecting unusable Terraform state](terraform-discovery/state-loading/state-file-loading.feature) (1)
