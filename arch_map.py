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
    for r in module.get("resources", []):
        yield r, path
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
        for r, module in _walk_show_json_modules(root):
            kind = TF_KINDS.get(r.get("type"))
            if kind:
                nodes.append(
                    {
                        "id": r["address"],
                        "kind": kind[0],
                        "label": f"{kind[1]}: {r.get('name', r['address'])}",
                        "module": module,
                    }
                )
        return nodes
    for r in resources:
        kind = TF_KINDS.get(r.get("type"))
        if kind:
            # classic state: "module" is e.g. "module.db" or "module.db.module.sub"
            module = "/".join(r["module"].split(".")[1::2]) if r.get("module") else ""
            nodes.append(
                {
                    "id": f"{r['type']}.{r['name']}",
                    "kind": kind[0],
                    "label": f"{kind[1]}: {r['name']}",
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
        for r, _module in _walk_show_json_modules(root):
            src = r.get("address")
            if src not in known_ids:
                continue
            for dst in r.get("depends_on") or []:
                if dst in known_ids:
                    edges.append((src, dst, ""))
        return edges
    for r in resources:
        src = f"{r['type']}.{r['name']}"
        if src not in known_ids:
            continue
        for inst in r.get("instances", []):
            for dst in inst.get("dependencies") or []:
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
    for d in get("deployments"):
        name = d["metadata"]["name"]
        replicas = d["spec"].get("replicas", 1)
        wid = f"k8s.{name}"
        nodes.append({"id": wid, "kind": "service", "label": f"{name} ×{replicas}"})
        values = []
        for c in d["spec"]["template"]["spec"].get("containers", []):
            for e in c.get("env", []):
                if "value" in e:
                    values.append(e["value"])
        if values:
            env_by_workload[wid] = values
    selectors = {}
    for s in get("services"):
        sel = s["spec"].get("selector") or {}
        selectors[s["metadata"]["name"]] = sel.get("app") or sel.get("app.kubernetes.io/name")
    for i in get("ingresses"):
        ing_name = i["metadata"]["name"]
        nodes.append({"id": f"k8s.ing.{ing_name}", "kind": "edge", "label": f"Ingress: {ing_name}"})
        for rule in i["spec"].get("rules", []):
            for path in rule.get("http", {}).get("paths", []):
                svc = path.get("backend", {}).get("service", {}).get("name")
                app = selectors.get(svc)
                if app:
                    edges.append((f"k8s.ing.{ing_name}", f"k8s.{app}", rule.get("host", "")))
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
    datastores = [n for n in nodes if n["kind"] in DATASTORE_KINDS]
    for wid, values in env_by_workload.items():
        matched = set()
        for value in values:
            m = DSN_RE.search(value)
            if m:
                host = m.group("host").lower()
                for n in datastores:
                    if n["id"] in matched:
                        continue
                    name_part = n["id"].rsplit(".", 1)[-1].lower()
                    if name_part and name_part in host:
                        edges.append((wid, n["id"], m.group("scheme").lower()))
                        matched.add(n["id"])
                        break
                continue
            norm_value = value.lower().replace("-", "_")
            for n in datastores:
                if n["id"] in matched:
                    continue
                name_part = n["id"].rsplit(".", 1)[-1].lower()
                if len(name_part) < MIN_TOKEN_LEN:
                    continue
                if re.search(rf"(?<![a-z0-9]){re.escape(name_part)}(?![a-z0-9])", norm_value):
                    edges.append((wid, n["id"], ""))
                    matched.add(n["id"])
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

KIND_DESCRIPTIONS = {  # shown in the generated legend
    "service": "Service / compute",
    "database": "Database",
    "cache": "Cache",
    "store": "Object storage",
    "queue": "Queue / topic",
    "edge": "Load balancer / ingress",
}


def _present_kinds(nodes):
    return sorted({n["kind"] for n in nodes})


def sanitize(node_id):
    return re.sub(r"[^A-Za-z0-9_]", "_", node_id)


def collapse_to_context(nodes, edges):
    """C4 context level: one box per kind, edges collapsed to kind->kind."""
    kind_counts = {}
    for n in nodes:
        kind_counts[n["kind"]] = kind_counts.get(n["kind"], 0) + 1
    context_nodes = [
        {"id": f"group_{kind}", "kind": kind, "label": f"{kind} ({count})"}
        for kind, count in sorted(kind_counts.items())
    ]
    kind_by_id = {n["id"]: n["kind"] for n in nodes}
    seen, context_edges = set(), []
    for src, dst, _label in edges:
        sk, dk = kind_by_id.get(src), kind_by_id.get(dst)
        if not sk or not dk or sk == dk or (sk, dk) in seen:
            continue
        seen.add((sk, dk))
        context_edges.append((f"group_{sk}", f"group_{dk}", ""))
    return context_nodes, context_edges


def _kind_subgraph_lines(group, indent):
    lines = []
    by_kind = {}
    for n in group:
        by_kind.setdefault(n["kind"], []).append(n)
    for kind, kgroup in sorted(by_kind.items()):
        lines.append(f"{indent}subgraph {kind}s")
        for n in kgroup:
            left, right = SHAPES.get(kind, ("[", "]"))
            lines.append(f'{indent}  {sanitize(n["id"])}{left}"{n["label"]}"{right}')
        lines.append(f"{indent}end")
    return lines


def to_mermaid(nodes, edges, title="Architecture"):
    lines = [
        "```mermaid",
        "flowchart TB",
        f"  %% {title} — generated by arch-map, do not edit by hand",
    ]
    by_module = {}
    for n in nodes:
        by_module.setdefault(n.get("module", ""), []).append(n)
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
            left, right = SHAPES.get(kind, ("[", "]"))
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


def to_plantuml(nodes, edges, title="Architecture"):
    lines = ["```plantuml", "@startuml", f"title {title}", "left to right direction"]
    by_kind = {}
    for n in nodes:
        by_kind.setdefault(n["kind"], []).append(n)
    for kind, group in sorted(by_kind.items()):
        lines.append(f'package "{kind}s" {{')
        for n in group:
            shape = PLANTUML_SHAPES.get(kind, "component")
            lines.append(f'  {shape} "{n["label"]}" as {sanitize(n["id"])}')
        lines.append("}")
    for src, dst, label in edges:
        arrow = f"{sanitize(src)} --> {sanitize(dst)}"
        lines.append(f"{arrow} : {label}" if label else arrow)
    kinds = _present_kinds(nodes)
    if kinds:
        lines.append("legend")
        for kind in kinds:
            shape = PLANTUML_SHAPES.get(kind, "component")
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


def to_d2(nodes, edges, title="Architecture"):
    lines = ["```d2", f"# {title} — generated by arch-map, do not edit by hand"]
    by_kind = {}
    for n in nodes:
        by_kind.setdefault(n["kind"], []).append(n)
    for kind, group in sorted(by_kind.items()):
        lines.append(f"{kind}s: {{")
        for n in group:
            shape = D2_SHAPES.get(kind, "rectangle")
            lines.append(f'  {sanitize(n["id"])}: "{n["label"]}" {{shape: {shape}}}')
        lines.append("}")
    for src, dst, label in edges:
        arrow = f"{sanitize(src)} -> {sanitize(dst)}"
        lines.append(f'{arrow}: "{label}"' if label else arrow)
    kinds = _present_kinds(nodes)
    if kinds:
        lines.append("legend: {")
        for kind in kinds:
            shape = D2_SHAPES.get(kind, "rectangle")
            lines.append(f'  {kind}: "{KIND_DESCRIPTIONS.get(kind, kind)}" {{shape: {shape}}}')
        lines.append("}")
    lines.append("```")
    return "\n".join(lines)


RENDERERS = {"mermaid": to_mermaid, "plantuml": to_plantuml, "d2": to_d2}


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="arch-map", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--tfstate", help="terraform state JSON file")
    p.add_argument("--k8s", metavar="NAMESPACE", help="live cluster namespace")
    p.add_argument("-o", "--output", default="-", help="output file (default stdout)")
    p.add_argument("--title", default="Architecture")
    p.add_argument(
        "--level",
        choices=["context", "container", "component"],
        default="container",
        help=(
            "C4 level: context collapses to one box per kind; container (default) "
            "and component show every discovered node — this tool doesn't yet "
            "collect sub-component detail, so component == container"
        ),
    )
    p.add_argument(
        "--format",
        choices=sorted(RENDERERS),
        default="mermaid",
        help="diagram syntax (default: mermaid, renders natively on GitHub)",
    )
    args = p.parse_args(argv)

    if not args.tfstate and not args.k8s:
        p.error("need at least one of --tfstate / --k8s")

    nodes, edges = [], []
    if args.tfstate:
        with open(args.tfstate) as fh:
            tf_state = json.load(fh)
        tf_nodes = nodes_from_tfstate(tf_state)
        nodes.extend(tf_nodes)
        edges.extend(edges_from_tfstate(tf_state, {n["id"] for n in tf_nodes}))
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
