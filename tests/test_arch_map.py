from arch_map import (
    collapse_to_context,
    edges_from_env_dsns,
    nodes_from_tfstate,
    sanitize,
    to_d2,
    to_mermaid,
    to_plantuml,
)


def test_tfstate_classic_format():
    state = {
        "resources": [
            {"type": "aws_db_instance", "name": "main"},
            {"type": "aws_sqs_queue", "name": "jobs"},
            {"type": "aws_iam_role", "name": "ignored"},
        ]
    }
    nodes = nodes_from_tfstate(state)
    assert {n["kind"] for n in nodes} == {"database", "queue"}


def test_tfstate_gcp_and_azure_kinds():
    state = {
        "resources": [
            {"type": "google_sql_database_instance", "name": "primary"},
            {"type": "google_pubsub_topic", "name": "events"},
            {"type": "azurerm_redis_cache", "name": "sessions"},
            {"type": "azurerm_storage_account", "name": "assets"},
        ]
    }
    nodes = nodes_from_tfstate(state)
    assert {n["kind"] for n in nodes} == {"database", "queue", "cache", "store"}


def test_tfstate_classic_format_module_grouping():
    state = {
        "resources": [
            {"type": "aws_db_instance", "name": "main", "module": "module.db"},
            {"type": "aws_sqs_queue", "name": "jobs"},
        ]
    }
    nodes = nodes_from_tfstate(state)
    modules = {n["id"]: n["module"] for n in nodes}
    assert modules == {"aws_db_instance.main": "db", "aws_sqs_queue.jobs": ""}


def test_tfstate_show_json_format_module_grouping():
    state = {
        "values": {
            "root_module": {
                "resources": [
                    {"address": "aws_sqs_queue.jobs", "type": "aws_sqs_queue", "name": "jobs"},
                ],
                "child_modules": [
                    {
                        "address": "module.db",
                        "resources": [
                            {
                                "address": "module.db.aws_db_instance.main",
                                "type": "aws_db_instance",
                                "name": "main",
                            }
                        ],
                    }
                ],
            }
        }
    }
    nodes = nodes_from_tfstate(state)
    modules = {n["id"]: n["module"] for n in nodes}
    assert modules == {"aws_sqs_queue.jobs": "", "module.db.aws_db_instance.main": "db"}


def test_tfstate_show_json_format():
    state = {
        "values": {
            "root_module": {
                "resources": [
                    {"address": "aws_s3_bucket.assets", "type": "aws_s3_bucket", "name": "assets"},
                ]
            }
        }
    }
    nodes = nodes_from_tfstate(state)
    assert nodes[0]["label"] == "S3: assets"


def test_mermaid_output_shapes_and_edges():
    nodes = [
        {"id": "k8s.api", "kind": "service", "label": "api ×3"},
        {"id": "aws_db_instance.main", "kind": "database", "label": "RDS: main"},
    ]
    edges = [("k8s.api", "aws_db_instance.main", "sql")]
    out = to_mermaid(nodes, edges)
    assert 'k8s_api["api ×3"]' in out
    assert 'aws_db_instance_main[("RDS: main")]' in out
    assert "k8s_api -->|sql| aws_db_instance_main" in out


def test_sanitize_makes_valid_mermaid_ids():
    assert sanitize("aws_db_instance.my-db") == "aws_db_instance_my_db"


def test_mermaid_output_groups_by_module():
    nodes = [
        {"id": "aws_db_instance.main", "kind": "database", "label": "RDS: main", "module": "db"},
        {"id": "aws_sqs_queue.jobs", "kind": "queue", "label": "SQS: jobs", "module": ""},
    ]
    out = to_mermaid(nodes, [])
    assert 'subgraph db ["module: db"]' in out
    assert "aws_db_instance_main" in out
    assert out.index("subgraph db") < out.index("aws_db_instance_main")


def test_edges_from_env_dsns_matches_datastore_by_name():
    nodes = [
        {"id": "k8s.api", "kind": "service", "label": "api ×3"},
        {"id": "aws_db_instance.main", "kind": "database", "label": "RDS: main"},
    ]
    env_by_workload = {
        "k8s.api": ["postgres://user:pw@main.abc123.us-east-1.rds.amazonaws.com:5432/prod"]
    }
    edges = edges_from_env_dsns(nodes, env_by_workload)
    assert edges == [("k8s.api", "aws_db_instance.main", "postgres")]


def test_edges_from_env_dsns_no_match():
    nodes = [{"id": "aws_db_instance.main", "kind": "database", "label": "RDS: main"}]
    env_by_workload = {"k8s.api": ["not a dsn", "SOME_FLAG=true"]}
    assert edges_from_env_dsns(nodes, env_by_workload) == []


def test_edges_from_env_dsns_matches_non_dsn_by_token():
    nodes = [
        {"id": "k8s.api", "kind": "service", "label": "api ×3"},
        {"id": "scaleway_object_bucket.uploads", "kind": "store", "label": "Scaleway Bucket: uploads"},
    ]
    env_by_workload = {"k8s.api": ["BUCKET_NAME=my-app-uploads"]}
    edges = edges_from_env_dsns(nodes, env_by_workload)
    assert edges == [("k8s.api", "scaleway_object_bucket.uploads", "")]


def test_edges_from_env_dsns_token_match_requires_word_boundary():
    nodes = [{"id": "scaleway_object_bucket.data", "kind": "store", "label": "Scaleway Bucket: data"}]
    env_by_workload = {"k8s.api": ["METADATABASE_URL=irrelevant"]}
    assert edges_from_env_dsns(nodes, env_by_workload) == []


def test_plantuml_output_shapes_and_edges():
    nodes = [
        {"id": "k8s.api", "kind": "service", "label": "api ×3"},
        {"id": "aws_db_instance.main", "kind": "database", "label": "RDS: main"},
    ]
    edges = [("k8s.api", "aws_db_instance.main", "sql")]
    out = to_plantuml(nodes, edges)
    assert out.startswith("```plantuml\n@startuml")
    assert out.endswith("@enduml\n```")
    assert 'component "api ×3" as k8s_api' in out
    assert 'database "RDS: main" as aws_db_instance_main' in out
    assert "k8s_api --> aws_db_instance_main : sql" in out


def test_d2_output_shapes_and_edges():
    nodes = [
        {"id": "k8s.api", "kind": "service", "label": "api ×3"},
        {"id": "aws_db_instance.main", "kind": "database", "label": "RDS: main"},
    ]
    edges = [("k8s.api", "aws_db_instance.main", "sql")]
    out = to_d2(nodes, edges)
    assert out.startswith("```d2\n")
    assert out.endswith("```")
    assert 'k8s_api: "api ×3" {shape: rectangle}' in out
    assert 'aws_db_instance_main: "RDS: main" {shape: cylinder}' in out
    assert 'k8s_api -> aws_db_instance_main: "sql"' in out


def test_mermaid_output_includes_legend_for_present_kinds_only():
    nodes = [{"id": "k8s.api", "kind": "service", "label": "api ×3"}]
    out = to_mermaid(nodes, [])
    assert "subgraph Legend" in out
    assert 'legend_service["Service / compute"]' in out
    assert "legend_database" not in out


def test_plantuml_output_includes_legend():
    nodes = [{"id": "aws_db_instance.main", "kind": "database", "label": "RDS: main"}]
    out = to_plantuml(nodes, [])
    assert "legend\n  database = Database\nendlegend" in out


def test_d2_output_includes_legend():
    nodes = [{"id": "aws_db_instance.main", "kind": "database", "label": "RDS: main"}]
    out = to_d2(nodes, [])
    assert 'database: "Database" {shape: cylinder}' in out


def test_collapse_to_context_groups_by_kind():
    nodes = [
        {"id": "k8s.api", "kind": "service", "label": "api"},
        {"id": "k8s.worker", "kind": "service", "label": "worker"},
        {"id": "aws_db_instance.main", "kind": "database", "label": "RDS: main"},
    ]
    edges = [
        ("k8s.api", "aws_db_instance.main", "sql"),
        ("k8s.worker", "aws_db_instance.main", "sql"),
    ]
    cnodes, cedges = collapse_to_context(nodes, edges)
    assert {n["id"]: n["label"] for n in cnodes} == {
        "group_service": "service (2)",
        "group_database": "database (1)",
    }
    assert cedges == [("group_service", "group_database", "")]
