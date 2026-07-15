from arch_map import (
    collapse_to_context,
    edges_from_env_dsns,
    nodes_from_tfstate,
    sanitize,
    to_mermaid,
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
