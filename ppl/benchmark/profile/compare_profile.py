#!/usr/bin/env python3
"""
compare_profiles.py

Purpose
-------
Compare two OpenSearch/Elasticsearch "profile": true search responses and
visualize why one query is faster/slower than the other.

Input
-----
Two JSON files that are full search responses (the top-level object includes "took" and "profile").

Output
------
1) A PNG with side-by-side comparisons across key dimensions (query vs aggregation time,
   next_doc/collect counters, optimized-segment usage, and per-aggregator timing).
2) A textual summary printed to stdout with the top drivers of the performance delta.

Usage
-----
python compare_profiles.py profileA.json profileB.json \
  --out compare.png --title "Composite vs DateHistogram"
"""

import argparse
import json
import os
from collections import defaultdict, namedtuple
from typing import Dict, Any, Tuple

import matplotlib.pyplot as plt

# -------- Helpers --------

def _nz(x):
    """Return 0 if x is falsy or not a number-like."""
    try:
        return 0 if x is None else float(x)
    except Exception:
        return 0.0

def _get(d: Dict[str, Any], *path, default=0):
    """Safely get nested key; return default if missing."""
    cur = d
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur

def _sum_breakdown(node: Dict[str, Any], key: str) -> float:
    """Sum breakdown[key] across a query or aggregation node (already in nanos)."""
    return _nz(_get(node, "breakdown", key, default=0))

def _sum_debug(node: Dict[str, Any], key: str) -> float:
    """Sum debug[key] across aggregation node if present."""
    return _nz(_get(node, "debug", key, default=0))

def _walk_query_nodes(query_nodes):
    """Yield all query nodes (top + children recursively)."""
    stack = list(query_nodes) if isinstance(query_nodes, list) else [query_nodes]
    while stack:
        n = stack.pop()
        yield n
        for ch in n.get("children", []):
            stack.append(ch)

def _collect_search_times(shard: Dict[str, Any]) -> Tuple[float, float, Dict[str, float]]:
    """
    Return total query_time_ns, collector_time_ns and a dict of collector child times for a shard.
    """
    total_query_ns = 0.0
    total_collector_ns = 0.0
    collectors_detail = defaultdict(float)

    for s in shard.get("searches", []):
        # Sum time of top-level query nodes (already includes children in time_in_nanos).
        for q in s.get("query", []):
            total_query_ns += _nz(q.get("time_in_nanos", 0))

        # Sum collectors
        for c in s.get("collector", []):
            ns = _nz(c.get("time_in_nanos", 0))
            total_collector_ns += ns
            name = c.get("name", "collector")
            collectors_detail[name] += ns

    return total_query_ns, total_collector_ns, collectors_detail

def _collect_query_breakdown(shard: Dict[str, Any]) -> Dict[str, float]:
    """
    Aggregate key query breakdown counters across all query nodes.
    Returns nanos or counts as floats.
    """
    acc = defaultdict(float)
    for s in shard.get("searches", []):
        for q in s.get("query", []):
            for node in _walk_query_nodes([q]):
                bd = node.get("breakdown", {}) or {}
                # Time-based keys (nanos)
                for k in [
                    "next_doc", "build_scorer", "advance", "shallow_advance",
                    "score", "match", "create_weight", "compute_max_score",
                    "set_min_competitive_score"
                ]:
                    acc[k + "_ns"] += _nz(bd.get(k, 0))
                # Count-based keys
                for k in [
                    "next_doc_count", "build_scorer_count", "advance_count",
                    "shallow_advance_count", "score_count", "match_count"
                ]:
                    acc[k] += _nz(bd.get(k, 0))
    return acc

def _collect_agg_times(shard: Dict[str, Any]) -> Tuple[float, Dict[str, float], Dict[str, float], Dict[str, float]]:
    """
    Sum aggregation time and breakdowns by aggregator type.

    Returns:
      total_agg_ns,
      agg_type_ns:     {type -> time_in_nanos}
      agg_breakdown_ns:{metric -> nanos}  (collect_ns, post_collection_ns, build_leaf_collector_ns, initialize_ns, reduce_ns, build_aggregation_ns)
      agg_counts:      {metric -> count}  (collect_count, build_leaf_collector_count, build_aggregation_count, reduce_count, initialize_count)
    """
    total_agg_ns = 0.0
    agg_type_ns = defaultdict(float)
    agg_breakdown_ns = defaultdict(float)
    agg_counts = defaultdict(float)

    for agg in shard.get("aggregations", []):
        typ = agg.get("type", "Aggregator")
        ns = _nz(agg.get("time_in_nanos", 0))
        total_agg_ns += ns
        agg_type_ns[typ] += ns

        bd = agg.get("breakdown", {}) or {}
        for k_src, k_dst in [
            ("collect", "collect_ns"),
            ("post_collection", "post_collection_ns"),
            ("build_leaf_collector", "build_leaf_collector_ns"),
            ("initialize", "initialize_ns"),
            ("reduce", "reduce_ns"),
            ("build_aggregation", "build_aggregation_ns"),
        ]:
            agg_breakdown_ns[k_dst] += _nz(bd.get(k_src, 0))

        for k in [
            "collect_count", "build_leaf_collector_count",
            "build_aggregation_count", "reduce_count", "initialize_count"
        ]:
            agg_counts[k] += _nz(bd.get(k, 0))

    return total_agg_ns, agg_type_ns, agg_breakdown_ns, agg_counts

ProfileMetrics = namedtuple("ProfileMetrics", [
    "took_ms",
    "query_time_ns", "collector_time_ns",
    "agg_time_ns",
    "query_bd", "agg_bd_ns", "agg_counts",
    "collector_detail",
    "agg_type_ns",
    "optimized_segments", "total_buckets", "leaf_visited", "inner_visited",
])

def extract_metrics(resp: Dict[str, Any]) -> ProfileMetrics:
    took_ms = _nz(resp.get("took", 0))
    prof = resp.get("profile", {}) or {}
    shards = prof.get("shards", []) or []

    total_query_ns = 0.0
    total_collector_ns = 0.0
    total_agg_ns = 0.0
    query_bd_acc = defaultdict(float)
    agg_bd_ns_acc = defaultdict(float)
    agg_counts_acc = defaultdict(float)
    collector_detail_acc = defaultdict(float)
    agg_type_ns_acc = defaultdict(float)

    # aggregator debug (if present)
    optimized_segments = 0.0
    total_buckets = 0.0
    leaf_visited = 0.0
    inner_visited = 0.0

    for sh in shards:
        q_ns, c_ns, col_detail = _collect_search_times(sh)
        total_query_ns += q_ns
        total_collector_ns += c_ns
        for k, v in col_detail.items():
            collector_detail_acc[k] += v

        # query breakdown
        qbd = _collect_query_breakdown(sh)
        for k, v in qbd.items():
            query_bd_acc[k] += v

        # aggregation
        agg_ns, agg_type_ns, agg_bd_ns, agg_counts = _collect_agg_times(sh)
        total_agg_ns += agg_ns
        for k, v in agg_type_ns.items():
            agg_type_ns_acc[k] += v
        for k, v in agg_bd_ns.items():
            agg_bd_ns_acc[k] += v
        for k, v in agg_counts.items():
            agg_counts_acc[k] += v

        # debug per-aggregation (sum)
        for agg in sh.get("aggregations", []):
            optimized_segments += _sum_debug(agg, "optimized_segments")
            total_buckets += _sum_debug(agg, "total_buckets")
            leaf_visited  += _sum_debug(agg, "leaf_visited")
            inner_visited += _sum_debug(agg, "inner_visited")

    return ProfileMetrics(
        took_ms=took_ms,
        query_time_ns=total_query_ns,
        collector_time_ns=total_collector_ns,
        agg_time_ns=total_agg_ns,
        query_bd=dict(query_bd_acc),
        agg_bd_ns=dict(agg_bd_ns_acc),
        agg_counts=dict(agg_counts_acc),
        collector_detail=dict(collector_detail_acc),
        agg_type_ns=dict(agg_type_ns_acc),
        optimized_segments=optimized_segments,
        total_buckets=total_buckets,
        leaf_visited=leaf_visited,
        inner_visited=inner_visited,
    )

def ns_to_ms(x): return _nz(x) / 1e6
def ns_to_s(x):  return _nz(x) / 1e9

def human_ms(ms):
    return f"{ms:.1f} ms" if ms < 1000 else f"{ms/1000:.2f} s"

def pct_delta(a, b):
    if a == 0 and b == 0:
        return 0.0
    if a == 0:
        return float("inf")
    return (b - a) / a * 100.0

# -------- Visualization --------

def render(fig_title, a_name, b_name, A: ProfileMetrics, B: ProfileMetrics, out_png: str):
    fig = plt.figure(figsize=(14, 9), dpi=120)
    fig.suptitle(fig_title if fig_title else "Profile Comparison", fontsize=14)

    # Panel 1: High-level time breakdown (query vs aggregation vs collectors)
    ax1 = fig.add_axes([0.07, 0.63, 0.86, 0.28])
    labels = ["Query (profile query)", "Aggregation (all aggs)", "Collectors"]
    a_vals = [ns_to_ms(A.query_time_ns), ns_to_ms(A.agg_time_ns), ns_to_ms(A.collector_time_ns)]
    b_vals = [ns_to_ms(B.query_time_ns), ns_to_ms(B.agg_time_ns), ns_to_ms(B.collector_time_ns)]
    x = range(len(labels))
    width = 0.38
    ax1.bar([i - width/2 for i in x], a_vals, width, label=a_name)
    ax1.bar([i + width/2 for i in x], b_vals, width, label=b_name)
    ax1.set_ylabel("Time (ms)")
    ax1.set_title("High-level time")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels, rotation=10)
    ax1.legend(loc="upper right")

    # Panel 2: Core drivers (next_doc vs collect) + optimized segments
    ax2 = fig.add_axes([0.07, 0.34, 0.86, 0.22])
    labels2 = ["Query next_doc (ms)", "Agg collect (ms)", "Agg post_collection (ms)", "Optimized segments (count)"]
    a2 = [
        ns_to_ms(A.query_bd.get("next_doc_ns", 0)),
        ns_to_ms(A.agg_bd_ns.get("collect_ns", 0)),
        ns_to_ms(A.agg_bd_ns.get("post_collection_ns", 0)),
        A.optimized_segments,
    ]
    b2 = [
        ns_to_ms(B.query_bd.get("next_doc_ns", 0)),
        ns_to_ms(B.agg_bd_ns.get("collect_ns", 0)),
        ns_to_ms(B.agg_bd_ns.get("post_collection_ns", 0)),
        B.optimized_segments,
    ]
    x2 = range(len(labels2))
    ax2.bar([i - width/2 for i in x2], a2, width, label=a_name)
    ax2.bar([i + width/2 for i in x2], b2, width, label=b_name)
    ax2.set_title("Key drivers (time and fast-path usage)")
    ax2.set_xticks(list(x2))
    ax2.set_xticklabels(labels2, rotation=10)

    # Panel 3: Counts that imply work (log-scale for wide ranges)
    ax3 = fig.add_axes([0.07, 0.07, 0.86, 0.22])
    labels3 = ["Query next_doc_count", "Agg collect_count", "Leaf visited", "Buckets"]
    a3 = [
        A.query_bd.get("next_doc_count", 0),
        A.agg_counts.get("collect_count", 0),
        A.leaf_visited,
        A.total_buckets,
    ]
    b3 = [
        B.query_bd.get("next_doc_count", 0),
        B.agg_counts.get("collect_count", 0),
        B.leaf_visited,
        B.total_buckets,
    ]
    x3 = range(len(labels3))
    ax3.bar([i - width/2 for i in x3], a3, width, label=a_name)
    ax3.bar([i + width/2 for i in x3], b3, width, label=b_name)
    ax3.set_title("Work indicators (log scale)")
    ax3.set_xticks(list(x3))
    ax3.set_xticklabels(labels3, rotation=10)
    ax3.set_yscale("log")

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(out_png, bbox_inches="tight")
    print(f"[OK] Wrote {out_png}")

def explain(a_name, b_name, A: ProfileMetrics, B: ProfileMetrics):
    print("\n=== Summary ===")
    print(f"{a_name}: took={human_ms(A.took_ms)} | "
          f"query={human_ms(ns_to_ms(A.query_time_ns))} | "
          f"agg={human_ms(ns_to_ms(A.agg_time_ns))}")
    print(f"{b_name}: took={human_ms(B.took_ms)} | "
          f"query={human_ms(ns_to_ms(B.query_time_ns))} | "
          f"agg={human_ms(ns_to_ms(B.agg_time_ns))}")

    def line(name, a, b, unit):
        delta = pct_delta(a, b)
        arrow = "↑" if delta > 0 else ("↓" if delta < 0 else "•")
        print(f"- {name:<26} {a:>12,.0f} {unit}  →  {b:>12,.0f} {unit}   ({arrow} {abs(delta):.1f}%)")

    print("\nKey time drivers:")
    line("query.next_doc_ns", A.query_bd.get("next_doc_ns", 0)/1e6, B.query_bd.get("next_doc_ns", 0)/1e6, "ms")
    line("agg.collect_ns",    A.agg_bd_ns.get("collect_ns", 0)/1e6,  B.agg_bd_ns.get("collect_ns", 0)/1e6,  "ms")
    line("agg.post_ns",       A.agg_bd_ns.get("post_collection_ns", 0)/1e6, B.agg_bd_ns.get("post_collection_ns", 0)/1e6, "ms")

    print("\nWork indicators:")
    line("query.next_doc_count", A.query_bd.get("next_doc_count", 0), B.query_bd.get("next_doc_count", 0), "")
    line("agg.collect_count",    A.agg_counts.get("collect_count", 0), B.agg_counts.get("collect_count", 0), "")
    line("agg.optimized_segments", A.optimized_segments, B.optimized_segments, "")
    line("agg.leaf_visited",    A.leaf_visited, B.leaf_visited, "")
    line("agg.total_buckets",   A.total_buckets, B.total_buckets, "")

    # Heuristics to explain the delta succinctly
    print("\nDiagnosis:")
    msgs = []
    if A.agg_counts.get("collect_count", 0) > 0 and B.agg_counts.get("collect_count", 0) == 0 and B.optimized_segments > 0:
        msgs.append(f"{b_name} likely used a segment-level fast path (no per-doc collect), "
                    f"while {a_name} iterated documents into the aggregator.")
    if B.query_bd.get("next_doc_count", 0) < 0.1 * max(1, A.query_bd.get("next_doc_count", 0)):
        msgs.append("Massively fewer doc cursor advances in the faster profile (lower next_doc_count).")
    if A.agg_type_ns and B.agg_type_ns and set(A.agg_type_ns.keys()) != set(B.agg_type_ns.keys()):
        msgs.append("Different aggregator types detected; they have different execution characteristics.")
    if not msgs:
        msgs.append("The slower profile spends more time in query iteration and/or aggregation collection.")
    for m in msgs:
        print(f"- {m}")

# -------- Main --------

def main():
    ap = argparse.ArgumentParser(description="Compare two OpenSearch/Elasticsearch profile JSON responses.")
    ap.add_argument("profile_a", help="First profile JSON")
    ap.add_argument("profile_b", help="Second profile JSON")
    ap.add_argument("--name-a", default="Profile A")
    ap.add_argument("--name-b", default="Profile B")
    ap.add_argument("--title", default=None, help="Figure title")
    ap.add_argument("--out", default=None, help="Output PNG path")
    args = ap.parse_args()

    with open(args.profile_a, "r") as f:
        A_json = json.load(f)
    with open(args.profile_b, "r") as f:
        B_json = json.load(f)

    A = extract_metrics(A_json)
    B = extract_metrics(B_json)

    out = args.out
    if not out:
        base_a = os.path.splitext(os.path.basename(args.profile_a))[0]
        base_b = os.path.splitext(os.path.basename(args.profile_b))[0]
        out = f"compare_{base_a}_vs_{base_b}.png"

    render(args.title, args.name_a, args.name_b, A, B, out)
    explain(args.name_a, args.name_b, A, B)

if __name__ == "__main__":
    main()
