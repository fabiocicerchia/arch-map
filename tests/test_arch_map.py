from arch_map import nodes_from_tfstate, sanitize, to_mermaid


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
