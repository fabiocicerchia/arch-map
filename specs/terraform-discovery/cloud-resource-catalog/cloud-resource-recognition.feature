@domain:terraform-discovery @area:cloud-resource-catalog @from:arch-map/arch-map
Feature: Recognising cloud resources
  Operators see their known cloud resources from thirteen providers as typed, labelled boxes, with IAM, networking and other plumbing left off the diagram.

  @id:terraform-discovery.cloud-resource-catalog.001 @rule:terraform.catalog.known-types-mapped-unknown-ignored @verified @source:arch_map.py#TF_KINDS @test:tests/test_arch_map.py#test_tfstate_classic_format @test:tests/test_arch_map.py#test_tfstate_gcp_and_azure_kinds @test:tests/test_arch_map.py#test_tfstate_show_json_format
  Scenario Outline: Known resource types become labelled boxes of their kind and everything else is left out
    Given the Terraform state contains a resource of type "<type>" named "<name>"
    When the operator generates the diagram from that state
    Then <outcome>

    Examples:
      | type                      | name      | outcome                                          |
      | aws_db_instance           | main      | a database box labelled "RDS: main"              |
      | aws_s3_bucket             | assets    | an object storage box labelled "S3: assets"      |
      | google_pubsub_topic       | events    | a queue box labelled "Pub/Sub: events"           |
      | azurerm_redis_cache       | sessions  | a cache box labelled "Azure Cache: sessions"     |
      | hcloud_load_balancer      | front     | a load balancer box labelled "Hetzner LB: front" |
      | cloudflare_workers_script | edge-auth | a service box labelled "Workers: edge-auth"      |
      | aws_iam_role              | deployer  | no box for this resource                         |
