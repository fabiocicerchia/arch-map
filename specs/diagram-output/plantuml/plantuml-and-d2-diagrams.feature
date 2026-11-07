@domain:diagram-output @area:plantuml @from:arch-map/arch-map
Feature: PlantUML and D2 diagrams
  Operators who use PlantUML or D2 tooling can get the same diagram in that syntax.

  Background:
    Given the discovered architecture has the service "api ×3" linked to the database "RDS: main" with label "sql"

  @id:diagram-output.plantuml.001 @rule:output.alt-formats.same-diagram-in-chosen-syntax @verified @source:arch_map.py#RENDERERS @test:tests/test_arch_map.py#test_plantuml_output_shapes_and_edges @test:tests/test_arch_map.py#test_d2_output_shapes_and_edges
  Scenario Outline: The same diagram can be rendered as PlantUML or D2
    When the operator generates the diagram in <format> format
    Then the diagram is a fenced "<format>" block
    And it contains '<service line>' and '<database line>'
    And it contains '<link line>'

    Examples:
      | format   | service line                         | database line                                       | link line                              |
      | plantuml | component "api ×3" as k8s_api        | database "RDS: main" as aws_db_instance_main        | k8s_api --> aws_db_instance_main : sql |
      | d2       | k8s_api: "api ×3" {shape: rectangle} | aws_db_instance_main: "RDS: main" {shape: cylinder} | k8s_api -> aws_db_instance_main: "sql" |

  @id:diagram-output.plantuml.002 @rule:output.alt-formats.no-module-grouping @inferred @source:arch_map.py#to_plantuml
  Scenario Outline: PlantUML and D2 diagrams do not group resources by Terraform module
    Given the RDS instance "main" lives in Terraform module "db"
    When the operator generates the diagram in <format> format
    Then "RDS: main" appears only inside the "databases" group
    And no "module: db" group appears

    Examples:
      | format   |
      | plantuml |
      | d2       |
