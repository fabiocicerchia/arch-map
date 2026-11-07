@domain:diagram-output @area:grouping-and-legend @from:arch-map/arch-map
Feature: Grouping, shapes and legend
  Readers of the diagram can tell kinds apart at a glance, and the diagram stays valid whatever the resource names are.

  @id:diagram-output.grouping-and-legend.001 @rule:output.legend.present-kinds-only @verified @source:arch_map.py#_present_kinds @test:tests/test_arch_map.py#test_mermaid_output_includes_legend_for_present_kinds_only @test:tests/test_arch_map.py#test_plantuml_output_includes_legend @test:tests/test_arch_map.py#test_d2_output_includes_legend
  Scenario Outline: The legend explains only the kinds that appear in the diagram
    Given the discovered architecture has only the database "RDS: main"
    When the operator generates the diagram in <format> format
    Then the legend contains '<legend entry>'
    And the legend has no entry for services, caches, storage, queues or load balancers

    Examples:
      | format   | legend entry                           |
      | mermaid  | legend_database[("Database")]          |
      | plantuml | database = Database                    |
      | d2       | database: "Database" {shape: cylinder} |

  @id:diagram-output.grouping-and-legend.002 @rule:output.ids.safe-for-diagram-syntax @verified @source:arch_map.py#sanitize @test:tests/test_arch_map.py#test_sanitize_makes_valid_mermaid_ids
  Scenario: Resource identifiers are made safe for diagram syntax
    Given the state has an RDS instance named "my-db"
    When the operator generates the diagram
    Then the box is identified as "aws_db_instance_my_db"
    And its label still reads "RDS: my-db"
