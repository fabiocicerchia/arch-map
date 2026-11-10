@domain:connection-inference @area:connection-string-links @from:arch-map/arch-map
Feature: Inferring workload-to-datastore connections
  Operators see which workloads talk to which Terraform datastores, inferred from the literal environment values of their Deployments.

  Background:
    Given the operator generates the diagram from Terraform state and the Kubernetes namespace "production"
    And the Deployment "api" is on the diagram

  @id:connection-inference.connection-string-links.001 @rule:connections.dsn.linked-by-host-with-protocol @verified @source:arch_map.py#edges_from_env_dsns @test:tests/test_arch_map.py#test_edges_from_env_dsns_matches_datastore_by_name @test:tests/test_arch_map.py#test_edges_from_env_dsns_no_match
  Scenario Outline: A connection URL naming a datastore's host links the workload to it, labelled with the protocol
    Given the state has a <kind> named "<name>"
    And "api" has an environment value "<value>"
    When the operator generates the diagram
    Then a link labelled "<label>" runs from "api" to the <kind> "<name>"

    Examples:
      | kind     | name     | value                                                                 | label       |
      | database | main     | postgres://app:secret@main.abc123.eu-west-1.rds.example.com:5432/prod | postgres    |
      | database | orders   | mysql://orders.db.example.com/shop                                    | mysql       |
      | cache    | sessions | rediss://sessions.cache.example.com:6380                              | rediss      |
      | queue    | jobs     | amqp://jobs.mq.example.com                                            | amqp        |
      | database | catalog  | mongodb+srv://catalog.mongo.example.com/app                           | mongodb+srv |

  @id:connection-inference.connection-string-links.002 @rule:connections.dsn.host-match-is-substring @inferred @source:arch_map.py#_datastore_in_host @questionable
  Scenario: A connection URL links to a datastore whose name merely appears inside the host
    Given the state has a database named "db" and a cache named "cache"
    And "api" has an environment value "postgres://app@reporting-dbx.example.com/stats"
    When the operator generates the diagram
    Then a link labelled "postgres" runs from "api" to the database "db"

  @id:connection-inference.connection-string-links.003 @rule:connections.name-reference.whole-token-min-length @verified @source:arch_map.py#_datastore_in_value @test:tests/test_arch_map.py#test_edges_from_env_dsns_matches_non_dsn_by_token @test:tests/test_arch_map.py#test_edges_from_env_dsns_token_match_requires_word_boundary
  Scenario Outline: A non-URL value naming a datastore as a whole word links to it, but short names and word fragments do not
    Given the state has an object storage bucket named "<name>"
    And "api" has an environment value "<value>"
    When the operator generates the diagram
    Then <outcome>

    Examples:
      | name    | value                       | outcome                                                    |
      | uploads | BUCKET_NAME=my-app-uploads  | an unlabelled link runs from "api" to the bucket "uploads" |
      | data    | METADATABASE_URL=irrelevant | no link is drawn                                           |
      | img     | assets-img                  | no link is drawn                                           |
