@domain:terraform-discovery @area:dependency-links @from:arch-map/arch-map
Feature: Linking resources by recorded dependencies
  Operators see the dependencies Terraform recorded as arrows between boxes, without arrows pointing at resources that are not drawn.

  @id:terraform-discovery.dependency-links.001 @rule:terraform.dependencies.links-only-between-drawn-resources @inferred @source:arch_map.py#edges_from_tfstate
  Scenario: Recorded dependencies become links only when both ends are on the diagram
    Given a Lambda function "worker" depends on the SQS queue "jobs" and on the IAM role "worker"
    When the operator generates the diagram from that state
    Then the diagram shows an unlabelled link from "Lambda: worker" to "SQS: jobs"
    And no link to the IAM role appears
