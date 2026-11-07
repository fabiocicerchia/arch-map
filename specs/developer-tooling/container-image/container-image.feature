@domain:developer-tooling @area:container-image @from:arch-map/dockerfile
Feature: Running arch-map from its container image
  Lets an operator or CI job run arch-map from a Docker image without installing Python tooling, with the tool as the command and no root privileges.

  Background:
    Given the operator has built the arch-map container image

  @id:developer-tooling.container-image.001 @rule:tooling.container-image.runs-arch-map-as-entrypoint @inferred @source:Dockerfile#ENTRYPOINT
  Scenario: Arguments given to the container go straight to arch-map
    Given a Terraform state file mounted into the container at /work/terraform.tfstate
    When the operator runs the image with arguments "--tf /work/terraform.tfstate"
    Then arch-map runs with those arguments
    And the generated architecture document is written to stdout

  @id:developer-tooling.container-image.002 @rule:tooling.container-image.runs-as-non-root @inferred @source:Dockerfile#USER
  Scenario: The container runs arch-map as an unprivileged user
    When the operator runs the image
    Then arch-map runs as user "app" with uid 10001
    And it is not running as root

  @id:developer-tooling.container-image.003 @rule:tooling.container-image.no-kubectl-bundled @inferred @source:Dockerfile#FROM @questionable
  Scenario: The image does not include kubectl, so live clusters need it supplied
    Given no kubectl or kubeconfig has been provided to the container
    When the operator runs the image with arguments "--k8s shop"
    Then arch-map cannot read the namespace and reports that kubectl is not available
