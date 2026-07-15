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
}


def nodes_from_tfstate(state):
    """Extract interesting nodes from a terraform state dict."""
    nodes = []
    resources = state.get("resources", [])
    # `terraform show -json` nests under values.root_module
    if not resources and "values" in state:
        resources = state["values"].get("root_module", {}).get("resources", [])
        for r in resources:
            kind = TF_KINDS.get(r.get("type"))
            if kind:
                nodes.append(
                    {
                        "id": r["address"],
                        "kind": kind[0],
                        "label": f"{kind[1]}: {r.get('name', r['address'])}",
                    }
                )
        return nodes
    for r in resources:
        kind = TF_KINDS.get(r.get("type"))
        if kind:
            nodes.append(
                {
                    "id": f"{r['type']}.{r['name']}",
                    "kind": kind[0],
                    "label": f"{kind[1]}: {r['name']}",
                }
            )
    return nodes


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


def edges_from_env_dsns(nodes, env_by_workload):
    """Heuristic service->datastore edges: DSN env vars matched against node ids by name."""
    edges = []
    datastores = [n for n in nodes if n["kind"] in DATASTORE_KINDS]
    for wid, values in env_by_workload.items():
        for value in values:
            m = DSN_RE.search(value)
            if not m:
                continue
            host = m.group("host").lower()
            for n in datastores:
                name_part = n["id"].rsplit(".", 1)[-1].lower()
                if name_part and name_part in host:
                    edges.append((wid, n["id"], m.group("scheme").lower()))
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


def sanitize(node_id):
    return node_id.replace(".", "_").replace("-", "_")


def to_mermaid(nodes, edges, title="Architecture"):
    lines = [
        "```mermaid",
        "flowchart TB",
        f"  %% {title} — generated by arch-map, do not edit by hand",
    ]
    by_kind = {}
    for n in nodes:
        by_kind.setdefault(n["kind"], []).append(n)
    for kind, group in sorted(by_kind.items()):
        lines.append(f"  subgraph {kind}s")
        for n in group:
            left, right = SHAPES.get(kind, ("[", "]"))
            lines.append(f'    {sanitize(n["id"])}{left}"{n["label"]}"{right}')
        lines.append("  end")
    for src, dst, label in edges:
        arrow = f"-->|{label}|" if label else "-->"
        lines.append(f"  {sanitize(src)} {arrow} {sanitize(dst)}")
    lines.append("```")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="arch-map", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--tfstate", help="terraform state JSON file")
    p.add_argument("--k8s", metavar="NAMESPACE", help="live cluster namespace")
    p.add_argument("-o", "--output", default="-", help="output file (default stdout)")
    p.add_argument("--title", default="Architecture")
    args = p.parse_args(argv)

    if not args.tfstate and not args.k8s:
        p.error("need at least one of --tfstate / --k8s")

    nodes, edges = [], []
    if args.tfstate:
        with open(args.tfstate) as fh:
            nodes.extend(nodes_from_tfstate(json.load(fh)))
    if args.k8s:
        knodes, kedges, env_by_workload = nodes_edges_from_k8s(args.k8s)
        nodes.extend(knodes)
        edges.extend(kedges)
        edges.extend(edges_from_env_dsns(nodes, env_by_workload))

    doc = (
        f"# {args.title}\n\n_Generated by arch-map — regenerate, don't edit._\n\n"
        + to_mermaid(nodes, edges, args.title)
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
