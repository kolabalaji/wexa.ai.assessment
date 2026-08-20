"""
generate_readme_tables.py

Reads every results/*.json file produced by the loader_*.py and
benchmark_*.py scripts, and generates formatted markdown tables
ready to paste into README.md.

Usage:
    python3 generate_readme_tables.py > results/RESULTS_TABLES.md

This keeps your README's numbers script-generated rather than
hand-typed, per the assignment's reproducibility requirement --
anyone re-running the benchmarks can regenerate this file fresh.
"""

import json
import os
import glob

RESULTS_DIR = "results"

LOAD_FILES = {
    "CognoDB": "load_result_cognodb.json",
    "Memgraph": "load_result_memgraph.json",
    "Neo4j-Local": "load_result_neo4j_local.json",
    "ArangoDB": "load_result_arangodb.json",
}


def load_json(path):
    full_path = os.path.join(RESULTS_DIR, path)
    if not os.path.exists(full_path):
        return None
    with open(full_path) as f:
        return json.load(f)


def load_benchmark_results():
    """Combines the Cypher-family list-of-platforms file with the
    single-platform ArangoDB file into one flat list, keyed by platform name."""
    combined = {}

    cypher_path = os.path.join(RESULTS_DIR, "benchmark_results_cypher.json")
    if os.path.exists(cypher_path):
        with open(cypher_path) as f:
            for entry in json.load(f):
                combined[entry["platform"]] = entry

    arango_path = os.path.join(RESULTS_DIR, "benchmark_results_arangodb.json")
    if os.path.exists(arango_path):
        with open(arango_path) as f:
            entry = json.load(f)
            combined[entry["platform"]] = entry

    return combined


def fmt(value, suffix=""):
    if value is None:
        return "N/A"
    return f"{value}{suffix}"


def generate_load_table():
    lines = []
    lines.append("### Data Loading\n")
    lines.append("| Platform | Nodes | Relationships | Node Load Time | Nodes/sec | Rel Load Time | Rels/sec |")
    lines.append("|---|---|---|---|---|---|---|")

    for platform, filename in LOAD_FILES.items():
        data = load_json(filename)
        if data is None:
            lines.append(f"| {platform} | *not run* | | | | | |")
            continue
        lines.append(
            f"| {platform} "
            f"| {fmt(data.get('verified_node_count', data.get('node_count')))} "
            f"| {fmt(data.get('verified_relationship_count', data.get('relationship_count')))} "
            f"| {fmt(data.get('node_load_time_sec'), 's')} "
            f"| {fmt(data.get('nodes_per_sec'))} "
            f"| {fmt(data.get('relationship_load_time_sec'), 's')} "
            f"| {fmt(data.get('relationships_per_sec'))} |"
        )

    return "\n".join(lines)


def generate_traversal_table(benchmarks):
    lines = []
    lines.append("### Traversal Latency (p50 / p95, ms)\n")
    lines.append("| Platform | 1-hop | 2-hop | 3-hop |")
    lines.append("|---|---|---|---|")

    for platform in LOAD_FILES.keys():
        entry = benchmarks.get(platform)
        if entry is None:
            lines.append(f"| {platform} | *not run* | | |")
            continue
        t = entry.get("traversals", {})
        row = [platform]
        for hop in ("1_hop", "2_hop", "3_hop"):
            h = t.get(hop)
            if h:
                row.append(f"{h['p50_ms']} / {h['p95_ms']}")
            else:
                row.append("N/A")
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def generate_lookup_table(benchmarks):
    lines = []
    lines.append("### Lookup & Aggregation Latency (p50 / p95, ms)\n")
    lines.append("| Platform | Point Lookup | Indexed Lookup | Aggregation |")
    lines.append("|---|---|---|---|")

    for platform in LOAD_FILES.keys():
        entry = benchmarks.get(platform)
        if entry is None:
            lines.append(f"| {platform} | *not run* | | |")
            continue

        pl = entry.get("point_lookup")
        pl_str = f"{pl['p50_ms']} / {pl['p95_ms']}" if pl else "N/A"

        # Cypher-family platforms don't have a separate indexed_lookup entry --
        # their point_lookup already uses the index (see README note on this).
        il = entry.get("indexed_lookup")
        il_str = f"{il['p50_ms']} / {il['p95_ms']}" if il else "same as point lookup*"

        agg = entry.get("aggregation")
        agg_str = f"{agg['p50_ms']} / {agg['p95_ms']}" if agg else "N/A"

        lines.append(f"| {platform} | {pl_str} | {il_str} | {agg_str} |")

    lines.append(
        "\n*For Cypher-family platforms (CognoDB, Memgraph, Neo4j-Local), the point "
        "lookup query already uses the `Person.id` index, so no separate indexed-lookup "
        "number is reported. ArangoDB's point lookup uses the primary `_key` path, "
        "while its indexed lookup exercises a separate persistent index -- these are "
        "architecturally different read paths, noted here for fairness."
    )

    return "\n".join(lines)


def generate_mixed_workload_table(benchmarks):
    lines = []
    lines.append("### Concurrent Read/Write Throughput\n")
    lines.append("| Platform | Clients | Duration | Read/Write Mix | Total Ops | Queries/sec |")
    lines.append("|---|---|---|---|---|---|")

    for platform in LOAD_FILES.keys():
        entry = benchmarks.get(platform)
        if entry is None:
            lines.append(f"| {platform} | *not run* | | | | |")
            continue
        m = entry.get("mixed_workload", {})
        lines.append(
            f"| {platform} "
            f"| {fmt(m.get('concurrent_clients'))} "
            f"| {fmt(m.get('duration_sec'), 's')} "
            f"| {fmt(m.get('read_write_mix'))} "
            f"| {fmt(m.get('total_operations'))} "
            f"| {fmt(m.get('queries_per_sec'))} |"
        )

    return "\n".join(lines)


def generate_missing_data_warning():
    missing = []
    for platform, filename in LOAD_FILES.items():
        if load_json(filename) is None:
            missing.append(f"- Load results missing for **{platform}** (expected `results/{filename}`)")

    benchmarks = load_benchmark_results()
    for platform in LOAD_FILES.keys():
        if platform not in benchmarks:
            missing.append(f"- Benchmark results missing for **{platform}**")

    if not missing:
        return ""

    return (
        "> **Note:** This table was generated with incomplete results. "
        "Re-run the missing loader/benchmark scripts before finalizing your README.\n\n"
        + "\n".join(missing) + "\n"
    )


def main():
    benchmarks = load_benchmark_results()

    warning = generate_missing_data_warning()
    if warning:
        print(warning)

    print("## Results\n")
    print(f"*Generated by `generate_readme_tables.py`. Regenerate anytime with the same command "
          f"after re-running the loaders/benchmarks.*\n")

    print(generate_load_table())
    print()
    print(generate_traversal_table(benchmarks))
    print()
    print(generate_lookup_table(benchmarks))
    print()
    print(generate_mixed_workload_table(benchmarks))


if __name__ == "__main__":
    main()
