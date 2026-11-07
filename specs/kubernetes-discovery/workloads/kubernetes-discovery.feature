@domain:kubernetes-discovery @area:workloads @from:arch-map/arch-map
Feature: Discovering a live Kubernetes namespace
  Operators see the Deployments and Ingresses running in a namespace, with replica counts and host routing, next to their Terraform resources.

  Background:
    Given the operator generates the diagram for the Kubernetes namespace "production"

  @id:kubernetes-discovery.workloads.001 @rule:kubernetes.workloads.deployment-shown-with-replicas @inferred @source:arch_map.py#_k8s_workloads
  Scenario Outline: Each Deployment is shown as a service labelled with its replica count
    Given the namespace has a Deployment "api" with <replicas setting>
    When the operator generates the diagram
    Then the diagram shows a service box labelled "<label>"

    Examples:
      | replicas setting     | label  |
      | 3 replicas           | api ×3 |
      | no replica count set | api ×1 |

  @id:kubernetes-discovery.workloads.002 @rule:kubernetes.ingress.linked-by-host-to-selected-workload @inferred @source:arch_map.py#_k8s_ingresses
  Scenario Outline: An Ingress is an entry point linked, by host, to the workload its backend Service selects
    Given the namespace has an Ingress "web" routing host "shop.example.com" to Service "api-svc"
    And Service "api-svc" selects pods with <selector label> "api"
    And a Deployment named "api" exists
    When the operator generates the diagram
    Then the diagram shows a load balancer box labelled "Ingress: web"
    And a link labelled "shop.example.com" runs from "Ingress: web" to "api ×1"

    Examples:
      | selector label         |
      | app                    |
      | app.kubernetes.io/name |

  @id:kubernetes-discovery.workloads.003 @rule:kubernetes.ingress.link-target-assumed-to-be-deployment-name @inferred @source:arch_map.py#_k8s_ingresses @questionable
  Scenario: An Ingress link points at the selector value even when no Deployment has that name
    Given Service "api-svc" selects app "storefront"
    And the Deployment serving it is named "storefront-v2"
    And an Ingress routes host "shop.example.com" to "api-svc"
    When the operator generates the diagram
    Then the link from the Ingress points at a bare box "k8s_storefront" outside every group
    And the "storefront-v2 ×1" box has no incoming Ingress link
