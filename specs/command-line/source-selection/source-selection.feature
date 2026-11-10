@domain:command-line @area:source-selection @from:arch-map/arch-map
Feature: Selecting sources
  Operators choose Terraform state, a Kubernetes namespace or both, and are stopped when they give neither.

  @id:command-line.source-selection.001 @rule:cli.sources.at-least-one-required @inferred @source:arch_map.py#main
  Scenario: Running without any source is refused
    Given neither a Terraform state file nor a Kubernetes namespace is given
    When the operator runs arch-map
    Then arch-map exits with code 2
    And stderr ends with "arch-map: error: need at least one of --tfstate / --k8s"
    And no diagram is written

  @id:command-line.source-selection.002 @rule:cli.sources.combined-in-one-diagram @inferred @source:arch_map.py#_collect
  Scenario: Terraform and Kubernetes sources given together appear in one diagram
    Given a Terraform state file with the database "main"
    And the Kubernetes namespace "production" with the Deployment "api" whose environment names "main"
    When the operator generates the diagram from both sources
    Then the diagram shows both "RDS: main" and "api ×1"
    And a link runs from "api ×1" to "RDS: main"
