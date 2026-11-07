@domain:architecture-views @area:context-view @from:arch-map/arch-map
Feature: Choosing the C4 level
  Operators pick between a one-box-per-kind context overview and the full container view of every discovered resource.

  Background:
    Given the discovered architecture has services "api" and "worker" both linked to the database "main"

  @id:architecture-views.context-view.001 @rule:views.context.one-box-per-kind @verified @source:arch_map.py#collapse_to_context @test:tests/test_arch_map.py#test_collapse_to_context_groups_by_kind
  Scenario: The context view shows one box per kind with counts and one link per kind pair
    When the operator generates the diagram at the context level
    Then the diagram shows a box "service (2)" and a box "database (1)"
    And exactly one unlabelled link runs from "service (2)" to "database (1)"

  @id:architecture-views.context-view.002 @rule:views.container.default-shows-everything @inferred @source:arch_map.py#_build_parser
  Scenario Outline: The container view is the default, and the component view shows the same detail
    When the operator generates the diagram at <level>
    Then the diagram shows separate boxes for "api", "worker" and "main"
    And each discovered link is drawn with its own label

    Examples:
      | level               |
      | no level given      |
      | the container level |
      | the component level |
