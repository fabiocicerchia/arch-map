#!/usr/bin/env python3
"""arch-map — a living C4-style container diagram from your real infra.

Sources:
  --tfstate terraform.tfstate      Terraform state (local file or `terraform show -json` output)
  --k8s namespace                  live workloads/services/ingresses via kubectl

Output is Mermaid (renders natively on GitHub) written to ARCHITECTURE.md —
commit it, regenerate in CI, and the diagram never rots.

  arch-map --tfstate infra.tfstate --k8s production -o ARCHITECTURE.md
"""

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict

DEFAULT_TITLE = "Architecture"

# Terraform resource type -> (node kind, label prefix)
TF_KINDS = {
    "aws_db_instance": ("database", "RDS"),
    "aws_rds_cluster": ("database", "RDS"),
    "aws_elasticache_cluster": ("cache", "ElastiCache"),
    "aws_s3_bucket": ("store", "S3"),
    "aws_sqs_queue": ("queue", "SQS"),
    "aws_sns_topic": ("queue", "SNS"),
    "aws_lb": ("edge", "ALB"),
    "aws_cloudfront_distribution": ("edge", "CloudFront"),
    "aws_lambda_function": ("service", "Lambda"),
    # GCP
    "google_sql_database_instance": ("database", "Cloud SQL"),
    "google_spanner_instance": ("database", "Spanner"),
    "google_redis_instance": ("cache", "Memorystore"),
    "google_storage_bucket": ("store", "GCS"),
    "google_pubsub_topic": ("queue", "Pub/Sub"),
    "google_compute_global_forwarding_rule": ("edge", "GCLB"),
    "google_compute_forwarding_rule": ("edge", "LB"),
    "google_cloudfunctions_function": ("service", "Cloud Function"),
    "google_cloudfunctions2_function": ("service", "Cloud Function"),
    "google_cloud_run_service": ("service", "Cloud Run"),
    # Azure
    "azurerm_postgresql_server": ("database", "Azure DB"),
    "azurerm_postgresql_flexible_server": ("database", "Azure DB"),
    "azurerm_mysql_server": ("database", "Azure DB"),
    "azurerm_sql_database": ("database", "Azure SQL"),
    "azurerm_redis_cache": ("cache", "Azure Cache"),
    "azurerm_storage_account": ("store", "Blob Storage"),
    "azurerm_servicebus_queue": ("queue", "Service Bus"),
    "azurerm_servicebus_topic": ("queue", "Service Bus"),
    "azurerm_application_gateway": ("edge", "App Gateway"),
    "azurerm_lb": ("edge", "LB"),
    "azurerm_function_app": ("service", "Function App"),
    # Hetzner Cloud
    "hcloud_server": ("service", "Hetzner Server"),
    "hcloud_load_balancer": ("edge", "Hetzner LB"),
    "hcloud_volume": ("store", "Hetzner Volume"),
    # Scaleway
    "scaleway_instance_server": ("service", "Scaleway Instance"),
    "scaleway_container": ("service", "Scaleway Container"),
    "scaleway_function": ("service", "Scaleway Function"),
    "scaleway_rdb_instance": ("database", "Scaleway DB"),
    "scaleway_redis_cluster": ("cache", "Scaleway Redis"),
    "scaleway_object_bucket": ("store", "Scaleway Bucket"),
    "scaleway_lb": ("edge", "Scaleway LB"),
    "scaleway_mnq_sqs_queue": ("queue", "Scaleway Queue"),
    # Alibaba Cloud
    "alicloud_instance": ("service", "ECS"),
    "alicloud_fc_function": ("service", "Function Compute"),
    "alicloud_db_instance": ("database", "ApsaraDB RDS"),
    "alicloud_kvstore_instance": ("cache", "ApsaraDB Redis"),
    "alicloud_oss_bucket": ("store", "OSS"),
    "alicloud_mns_queue": ("queue", "MNS"),
    "alicloud_slb_load_balancer": ("edge", "SLB"),
    # Oracle Cloud Infrastructure
    "oci_core_instance": ("service", "OCI Instance"),
    "oci_functions_function": ("service", "OCI Function"),
    "oci_database_db_system": ("database", "OCI DB System"),
    "oci_database_autonomous_database": ("database", "Autonomous DB"),
    "oci_objectstorage_bucket": ("store", "OCI Object Storage"),
    "oci_queue_queue": ("queue", "OCI Queue"),
    "oci_load_balancer_load_balancer": ("edge", "OCI LB"),
    # OVH
    "ovh_dedicated_server": ("service", "OVH Server"),
    "ovh_vps": ("service", "OVH VPS"),
    "ovh_cloud_project_database": ("database", "OVH DB"),
    # DigitalOcean
    "digitalocean_droplet": ("service", "Droplet"),
    "digitalocean_app": ("service", "DO App"),
    "digitalocean_database_cluster": ("database", "DO Database"),
    "digitalocean_loadbalancer": ("edge", "DO LB"),
    "digitalocean_spaces_bucket": ("store", "Spaces"),
    # Linode / Akamai
    "linode_instance": ("service", "Linode"),
    "linode_database_mysql": ("database", "Linode DB"),
    "linode_database_postgresql": ("database", "Linode DB"),
    "linode_nodebalancer": ("edge", "NodeBalancer"),
    "linode_object_storage_bucket": ("store", "Linode Object Storage"),
    # Cloudflare
    "cloudflare_workers_script": ("service", "Workers"),
    "cloudflare_r2_bucket": ("store", "R2"),
    "cloudflare_load_balancer": ("edge", "CF LB"),
    "cloudflare_queue": ("queue", "CF Queue"),
    # Vultr
    "vultr_instance": ("service", "Vultr Instance"),
    "vultr_database": ("database", "Vultr DB"),
    "vultr_load_balancer": ("edge", "Vultr LB"),
    "vultr_object_storage": ("store", "Vultr Object Storage"),
    # IBM Cloud
    "ibm_is_instance": ("service", "IBM VSI"),
    "ibm_database": ("database", "IBM Cloud Databases"),
    "ibm_is_lb": ("edge", "IBM LB"),
    "ibm_cos_bucket": ("store", "COS"),
}


def _walk_show_json_modules(module, path=""):
    """Yield (resource, module_path) for a `terraform show -json` module tree."""
    for resource in module.get("resources", []):
        yield resource, path
    for child in module.get("child_modules", []):
        # child module address looks like "module.db" or "module.db.module.sub"
        name = child["address"].rsplit(".", 1)[-1] if "address" in child else "?"
        child_path = f"{path}/{name}" if path else name
        yield from _walk_show_json_modules(child, child_path)


def nodes_from_tfstate(state):
    """Extract interesting nodes from a terraform state dict."""
    nodes = []
    resources = state.get("resources", [])
    # `terraform show -json` nests under values.root_module
    if not resources and "values" in state:
        root = state["values"].get("root_module", {})
        for resource, module in _walk_show_json_modules(root):
            mapped = TF_KINDS.get(resource.get("type"))
            if mapped:
                node_kind, label_prefix = mapped
                nodes.append(
                    {
                        "id": resource["address"],
                        "kind": node_kind,
                        "label": f"{label_prefix}: {resource.get('name', resource['address'])}",
                        "module": module,
                    }
                )
        return nodes
    for resource in resources:
        mapped = TF_KINDS.get(resource.get("type"))
        if mapped:
            node_kind, label_prefix = mapped
            # classic state: "module" is e.g. "module.db" or "module.db.module.sub"
            module = "/".join(resource["module"].split(".")[1::2]) if resource.get("module") else ""
            nodes.append(
                {
                    "id": f"{resource['type']}.{resource['name']}",
                    "kind": node_kind,
                    "label": f"{label_prefix}: {resource['name']}",
                    "module": module,
                }
            )
    return nodes


def edges_from_tfstate(state, known_ids):
    """Resource dependency edges recorded in tfstate, filtered to already-discovered nodes."""
    edges = []
    resources = state.get("resources", [])
    if not resources and "values" in state:
        root = state["values"].get("root_module", {})
        for resource, _module in _walk_show_json_modules(root):
            src = resource.get("address")
            if src not in known_ids:
                continue
            for dst in resource.get("depends_on") or []:
                if dst in known_ids:
                    edges.append((src, dst, ""))
        return edges
    for resource in resources:
        src = f"{resource['type']}.{resource['name']}"
        if src not in known_ids:
            continue
        for instance in resource.get("instances", []):
            for dst in instance.get("dependencies") or []:
                if dst in known_ids:
                    edges.append((src, dst, ""))
    return edges


def nodes_edges_from_k8s(namespace):
    """Workloads + services + ingress from a live cluster."""

    def get(kind):
        # nosec B603 B607: fixed argv (no shell); kind is an internal literal and
        # namespace is passed as a single argv element, so neither can inject.
        out = subprocess.run(  # nosec B603 B607
            ["kubectl", "get", kind, "-n", namespace, "-o", "json"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        return json.loads(out)["items"]

    nodes, edges, env_by_workload = [], [], {}
    for deployment in get("deployments"):
        name = deployment["metadata"]["name"]
        replicas = deployment["spec"].get("replicas", 1)
        workload_id = f"k8s.{name}"
        nodes.append({"id": workload_id, "kind": "service", "label": f"{name} ×{replicas}"})
        env_values = []
        for container in deployment["spec"]["template"]["spec"].get("containers", []):
            for env_var in container.get("env", []):
                # env entries without "value" are valueFrom refs: nothing to read here
                if "value" in env_var:
                    env_values.append(env_var["value"])
        if env_values:
            env_by_workload[workload_id] = env_values
    selectors = {}
    for service in get("services"):
        selector = service["spec"].get("selector") or {}
        app = selector.get("app") or selector.get("app.kubernetes.io/name")
        selectors[service["metadata"]["name"]] = app
    for ingress in get("ingresses"):
        name = ingress["metadata"]["name"]
        ingress_id = f"k8s.ing.{name}"
        nodes.append({"id": ingress_id, "kind": "edge", "label": f"Ingress: {name}"})
        for rule in ingress["spec"].get("rules", []):
            for path in rule.get("http", {}).get("paths", []):
                service_name = path.get("backend", {}).get("service", {}).get("name")
                app = selectors.get(service_name)
                if app:
                    edges.append((ingress_id, f"k8s.{app}", rule.get("host", "")))
    return nodes, edges, env_by_workload


# scheme://[user[:pass]@]host[:port][/db] — enough to pull a host out of a DSN env var
DSN_RE = re.compile(
    r"(?P<scheme>postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis(?:s)?|amqp(?:s)?)"
    r"://(?:[^@/\s]+@)?(?P<host>[^:/\s]+)",
    re.IGNORECASE,
)

DATASTORE_KINDS = {"database", "cache", "store", "queue"}

# ponytail: naive token match, no real reference tracking — a resource whose
# terraform name is a short/generic word (e.g. "data") can false-positive.
# Upgrade path: match against actual bucket/queue names from tfstate `values`
# instead of the terraform resource name, if this gets noisy in practice.
MIN_TOKEN_LEN = 4


def edges_from_env_dsns(nodes, env_by_workload):
    """Heuristic service->datastore edges from env var values.

    Two passes, most confident first:
      1. DSN-style values (scheme://host) matched by hostname.
      2. Any other env value containing a datastore's resource name as a
         distinct token — covers bucket names, queue URLs, function names,
         etc. that aren't connection strings.
    """
    edges = []
    datastores = [node for node in nodes if node["kind"] in DATASTORE_KINDS]
    for workload_id, env_values in env_by_workload.items():
        matched = set()
        for value in env_values:
            dsn = DSN_RE.search(value)
            if dsn:
                host = dsn.group("host").lower()
                for node in datastores:
                    if node["id"] in matched:
                        continue
                    resource_name = node["id"].rsplit(".", 1)[-1].lower()
                    if resource_name and resource_name in host:
                        edges.append((workload_id, node["id"], dsn.group("scheme").lower()))
                        matched.add(node["id"])
                        break
                continue
            normalised = value.lower().replace("-", "_")
            for node in datastores:
                if node["id"] in matched:
                    continue
                resource_name = node["id"].rsplit(".", 1)[-1].lower()
                if len(resource_name) < MIN_TOKEN_LEN:
                    continue
                token = rf"(?<![a-z0-9]){re.escape(resource_name)}(?![a-z0-9])"
                if re.search(token, normalised):
                    edges.append((workload_id, node["id"], ""))
                    matched.add(node["id"])
                    break
    return edges


SHAPES = {  # mermaid node shapes per kind
    "service": ("[", "]"),
    "database": ("[(", ")]"),
    "cache": ("[(", ")]"),
    "store": ("[/", "/]"),
    "queue": ("{{", "}}"),
    "edge": ("([", "])"),
}
DEFAULT_SHAPE = ("[", "]")  # unknown kind: a plain mermaid box

KIND_DESCRIPTIONS = {  # shown in the generated legend
    "service": "Service / compute",
    "database": "Database",
    "cache": "Cache",
    "store": "Object storage",
    "queue": "Queue / topic",
    "edge": "Load balancer / ingress",
}


def _present_kinds(nodes):
    return sorted({node["kind"] for node in nodes})


def sanitize(node_id):
    return re.sub(r"[^A-Za-z0-9_]", "_", node_id)


def collapse_to_context(nodes, edges):
    """C4 context level: one box per kind, edges collapsed to kind->kind."""
    kind_counts = Counter(node["kind"] for node in nodes)
    context_nodes = [
        {"id": f"group_{kind}", "kind": kind, "label": f"{kind} ({count})"}
        for kind, count in sorted(kind_counts.items())
    ]
    kind_by_id = {node["id"]: node["kind"] for node in nodes}
    seen, context_edges = set(), []
    for src, dst, _label in edges:
        src_kind, dst_kind = kind_by_id.get(src), kind_by_id.get(dst)
        if not src_kind or not dst_kind or src_kind == dst_kind or (src_kind, dst_kind) in seen:
            continue
        seen.add((src_kind, dst_kind))
        context_edges.append((f"group_{src_kind}", f"group_{dst_kind}", ""))
    return context_nodes, context_edges


def _by_kind(nodes):
    """Nodes bucketed by kind, in kind order — the grouping every renderer uses.

    Shared so the three formats can never drift into different orderings.
    """
    grouped = defaultdict(list)
    for node in nodes:
        grouped[node["kind"]].append(node)
    return sorted(grouped.items())


def _kind_subgraph_lines(group, indent):
    lines = []
    for kind, kgroup in _by_kind(group):
        lines.append(f"{indent}subgraph {kind}s")
        for node in kgroup:
            left, right = SHAPES.get(kind, DEFAULT_SHAPE)
            lines.append(f'{indent}  {sanitize(node["id"])}{left}"{node["label"]}"{right}')
        lines.append(f"{indent}end")
    return lines


def to_mermaid(nodes, edges, title=DEFAULT_TITLE):
    lines = [
        "```mermaid",
        "flowchart TB",
        f"  %% {title} — generated by arch-map, do not edit by hand",
    ]
    by_module = {}
    for node in nodes:
        by_module.setdefault(node.get("module", ""), []).append(node)
    root = by_module.pop("", [])
    for module, group in sorted(by_module.items()):
        lines.append(f'  subgraph {sanitize(module)} ["module: {module}"]')
        lines += _kind_subgraph_lines(group, "    ")
        lines.append("  end")
    lines += _kind_subgraph_lines(root, "  ")
    for src, dst, label in edges:
        arrow = f"-->|{label}|" if label else "-->"
        lines.append(f"  {sanitize(src)} {arrow} {sanitize(dst)}")
    kinds = _present_kinds(nodes)
    if kinds:
        lines.append("  subgraph Legend")
        for kind in kinds:
            left, right = SHAPES.get(kind, DEFAULT_SHAPE)
            lines.append(f'    legend_{kind}{left}"{KIND_DESCRIPTIONS.get(kind, kind)}"{right}')
        lines.append("  end")
    lines.append("```")
    return "\n".join(lines)


PLANTUML_SHAPES = {  # kind -> PlantUML component-diagram stereotype
    "service": "component",
    "database": "database",
    "cache": "database",
    "store": "folder",
    "queue": "queue",
    "edge": "boundary",
}
DEFAULT_PLANTUML_SHAPE = "component"


def to_plantuml(nodes, edges, title=DEFAULT_TITLE):
    lines = ["```plantuml", "@startuml", f"title {title}", "left to right direction"]
    for kind, group in _by_kind(nodes):
        lines.append(f'package "{kind}s" {{')
        for node in group:
            shape = PLANTUML_SHAPES.get(kind, DEFAULT_PLANTUML_SHAPE)
            lines.append(f'  {shape} "{node["label"]}" as {sanitize(node["id"])}')
        lines.append("}")
    for src, dst, label in edges:
        arrow = f"{sanitize(src)} --> {sanitize(dst)}"
        lines.append(f"{arrow} : {label}" if label else arrow)
    kinds = _present_kinds(nodes)
    if kinds:
        lines.append("legend")
        for kind in kinds:
            shape = PLANTUML_SHAPES.get(kind, DEFAULT_PLANTUML_SHAPE)
            lines.append(f"  {shape} = {KIND_DESCRIPTIONS.get(kind, kind)}")
        lines.append("endlegend")
    lines.append("@enduml")
    lines.append("```")
    return "\n".join(lines)


D2_SHAPES = {  # kind -> D2 shape
    "service": "rectangle",
    "database": "cylinder",
    "cache": "cylinder",
    "store": "page",
    "queue": "queue",
    "edge": "hexagon",
}
DEFAULT_D2_SHAPE = "rectangle"


def to_d2(nodes, edges, title=DEFAULT_TITLE):
    lines = ["```d2", f"# {title} — generated by arch-map, do not edit by hand"]
    for kind, group in _by_kind(nodes):
        lines.append(f"{kind}s: {{")
        for node in group:
            shape = D2_SHAPES.get(kind, DEFAULT_D2_SHAPE)
            lines.append(f'  {sanitize(node["id"])}: "{node["label"]}" {{shape: {shape}}}')
        lines.append("}")
    for src, dst, label in edges:
        arrow = f"{sanitize(src)} -> {sanitize(dst)}"
        lines.append(f'{arrow}: "{label}"' if label else arrow)
    kinds = _present_kinds(nodes)
    if kinds:
        lines.append("legend: {")
        for kind in kinds:
            shape = D2_SHAPES.get(kind, DEFAULT_D2_SHAPE)
            lines.append(f'  {kind}: "{KIND_DESCRIPTIONS.get(kind, kind)}" {{shape: {shape}}}')
        lines.append("}")
    lines.append("```")
    return "\n".join(lines)


RENDERERS = {"mermaid": to_mermaid, "plantuml": to_plantuml, "d2": to_d2}


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="arch-map", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--tfstate", help="terraform state JSON file")
    parser.add_argument("--k8s", metavar="NAMESPACE", help="live cluster namespace")
    parser.add_argument("-o", "--output", default="-", help="output file (default stdout)")
    parser.add_argument("--title", default=DEFAULT_TITLE)
    parser.add_argument(
        "--level",
        choices=["context", "container", "component"],
        default="container",
        help=(
            "C4 level: context collapses to one box per kind; container (default) "
            "and component show every discovered node — this tool doesn't yet "
            "collect sub-component detail, so component == container"
        ),
    )
    parser.add_argument(
        "--format",
        choices=sorted(RENDERERS),
        default="mermaid",
        help="diagram syntax (default: mermaid, renders natively on GitHub)",
    )
    args = parser.parse_args(argv)

    if not args.tfstate and not args.k8s:
        parser.error("need at least one of --tfstate / --k8s")

    nodes, edges = [], []
    if args.tfstate:
        with open(args.tfstate) as fh:
            tf_state = json.load(fh)
        tf_nodes = nodes_from_tfstate(tf_state)
        nodes.extend(tf_nodes)
        edges.extend(edges_from_tfstate(tf_state, {node["id"] for node in tf_nodes}))
    if args.k8s:
        knodes, kedges, env_by_workload = nodes_edges_from_k8s(args.k8s)
        nodes.extend(knodes)
        edges.extend(kedges)
        edges.extend(edges_from_env_dsns(nodes, env_by_workload))

    if args.level == "context":
        nodes, edges = collapse_to_context(nodes, edges)

    doc = (
        f"# {args.title}\n\n_Generated by arch-map — regenerate, don't edit._\n\n"
        + RENDERERS[args.format](nodes, edges, args.title)
        + "\n"
    )
    if args.output == "-":
        print(doc)
    else:
        with open(args.output, "w") as fh:
            fh.write(doc)
        print(f"arch-map: wrote {args.output} ({len(nodes)} nodes, {len(edges)} edges)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
