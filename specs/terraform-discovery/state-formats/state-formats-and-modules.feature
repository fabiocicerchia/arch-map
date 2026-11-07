@domain:terraform-discovery @area:state-formats @from:arch-map/arch-map
Feature: Reading classic and show-json state, including modules
  Operators can point arch-map at either a classic state file or `terraform show -json` output and see resources from child modules placed in their module.

  @id:terraform-discovery.state-formats.001 @rule:terraform.state-formats.both-formats-and-module-paths @verified @source:arch_map.py#nodes_from_tfstate @test:tests/test_arch_map.py#test_tfstate_classic_format_module_grouping @test:tests/test_arch_map.py#test_tfstate_show_json_format_module_grouping @test:tests/test_arch_map.py#test_mermaid_output_groups_by_module
  Scenario Outline: Resources from either state format appear with the module they live in
    Given a <format> state contains an SQS queue "jobs" at the root and an RDS instance "main" inside module "db"
    When the operator generates the diagram from that state
    Then the diagram shows "SQS: jobs" outside any module group
    And the diagram shows "RDS: main" inside the group "module: db"

    Examples:
      | format               |
      | classic flat         |
      | terraform show -json |

  @id:terraform-discovery.state-formats.002 @rule:terraform.state-formats.classic-module-resources-share-identity @inferred @source:arch_map.py#_nodes_from_classic_state @questionable
  Scenario: In classic state, same-named resources in different modules become one diagram identity
    Given a classic state contains an RDS instance "main" in module "billing" and another RDS instance "main" in module "orders"
    When the operator generates the diagram from that state
    Then both resources get the same diagram id "aws_db_instance_main"
    And the diagram does not keep them as two separate boxes with their own links
