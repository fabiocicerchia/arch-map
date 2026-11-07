@domain:kubernetes-discovery @area:cluster-access @from:arch-map/arch-map
Feature: Reaching the cluster through kubectl
  Operators need to know when the Kubernetes source cannot be read because kubectl is missing or the query fails.

  @id:kubernetes-discovery.cluster-access.001 @rule:kubernetes.cluster-access.kubectl-failure-reported @inferred @source:arch_map.py#_kubectl_get @questionable
  Scenario Outline: A missing or failing kubectl ends the run with a traceback instead of a one-line error
    Given <situation>
    When the operator generates the diagram for the Kubernetes namespace "production"
    Then arch-map stops with a Python traceback whose last line starts with "<error>"
    And no diagram is written

    Examples:
      | situation                            | error                                |
      | kubectl is not installed on the PATH | RuntimeError: kubectl is not on PATH |
      | kubectl cannot reach the cluster     | subprocess.CalledProcessError        |
