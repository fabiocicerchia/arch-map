@domain:diagram-output @area:mermaid @from:arch-map/arch-map
Feature: Mermaid diagrams
  Operators get, by default, a Mermaid diagram that GitHub renders natively from ARCHITECTURE.md.

  @id:diagram-output.mermaid.001 @rule:output.mermaid.default-with-labelled-links @verified @source:arch_map.py#to_mermaid @test:tests/test_arch_map.py#test_mermaid_output_shapes_and_edges
  Scenario: By default the diagram is a Mermaid flowchart with shaped boxes and labelled links
    Given the discovered architecture has the service "api ×3" linked to the database "RDS: main" with label "postgres"
    When the operator generates the diagram without choosing a format
    Then the diagram is a fenced "mermaid" block starting with "flowchart TB"
    And it contains 'k8s_api["api ×3"]' and 'aws_db_instance_main[("RDS: main")]'
    And it contains "k8s_api -->|postgres| aws_db_instance_main"
