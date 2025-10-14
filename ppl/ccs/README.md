# Cross-Cluster Search (CCS) with Two OpenSearch Nodes via Docker

A concise, reproducible walkthrough to spin up **two single-node OpenSearch clusters**, configure **CCS**, and validate with **terms aggregation**.

---

## 1) Prerequisites

* Docker (Desktop or Engine) and `docker compose`

```bash
docker --version
docker compose version
```

---

## 2) Create `docker-compose.yml`

```yaml
version: "3.8"

services:
  opensearch-a:
    image: opensearchproject/opensearch:2.14.0
    container_name: opensearch-a
    environment:
      - cluster.name=cluster_a
      - node.name=opensearch-a
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g"
      - DISABLE_SECURITY_PLUGIN=true
    ulimits:
      memlock: { soft: -1, hard: -1 }
      nofile:  { soft: 65536, hard: 65536 }
    ports:
      - "9200:9200"   # REST
      - "9300:9300"   # transport (used by CCS)
    networks: [opensearch-net]

  opensearch-b:
    image: opensearchproject/opensearch:2.14.0
    container_name: opensearch-b
    environment:
      - cluster.name=cluster_b
      - node.name=opensearch-b
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g"
      - DISABLE_SECURITY_PLUGIN=true
    ulimits:
      memlock: { soft: -1, hard: -1 }
      nofile:  { soft: 65536, hard: 65536 }
    ports:
      - "19200:9200"  # REST
      - "19300:9300"  # transport
    networks: [opensearch-net]

networks:
  opensearch-net:
```

> Notes
> • Security is disabled to focus on CCS mechanics.
> • Services are reachable inside the compose network by DNS names `opensearch-a` / `opensearch-b`.

---

## 3) Start and Sanity Check

```bash
docker compose up -d

# Verify both clusters respond
curl -s localhost:9200 | jq '.cluster_name,.tagline'
curl -s localhost:19200 | jq '.cluster_name,.tagline'
```

Expected: `cluster_a` and `cluster_b`.

---

## 4) Configure CCS on Cluster A (point to B)

```bash
curl -s -X PUT localhost:9200/_cluster/settings \
  -H 'Content-Type: application/json' -d '{
  "persistent": {
    "cluster": {
      "remote": {
        "b": {
          "seeds": ["opensearch-b:9300"],
          "skip_unavailable": true
        }
      }
    }
  }
}'
```

Verify:

```bash
curl -s localhost:9200/_remote/info | jq
# Expect: "b": { "connected": true, ... }
```

---

## 5) Seed Example Data on Cluster B

```bash
# Create index with keyword field for terms aggs
curl -s -X PUT localhost:19200/products -H 'Content-Type: application/json' -d '{
  "mappings": {
    "properties": {
      "id":       { "type": "keyword" },
      "name":     { "type": "text" },
      "category": { "type": "keyword" },
      "price":    { "type": "double" }
    }
  }
}'

# Bulk documents
curl -s -X POST localhost:19200/_bulk -H 'Content-Type: application/x-ndjson' -d '
{ "index": { "_index": "products", "_id": "1" } }
{ "id":"1","name":"OpenSearch Hoodie","category":"apparel","price":49.99 }
{ "index": { "_index": "products", "_id": "2" } }
{ "id":"2","name":"Query Language Mug","category":"merch","price":14.95 }
{ "index": { "_index": "products", "_id": "3" } }
{ "id":"3","name":"Calcite Hat","category":"apparel","price":24.50 }
{ "index": { "_index": "products", "_id": "4" } }
{ "id":"4","name":"Data Hoodie","category":"apparel","price":39.99 }
{ "index": { "_index": "products", "_id": "5" } }
{ "id":"5","name":"PPL Sticker","category":"merch","price":2.99 }
{ "index": { "_index": "products", "_id": "6" } }
{ "id":"6","name":"Observability T-shirt","category":"apparel","price":19.99 }
'

# Make searchable
curl -s -X POST localhost:19200/products/_refresh >/dev/null
```

---

## 6) Run CCS Searches from Cluster A

### 6.1 Basic search (remote index via alias `b`)

```bash
curl -s 'localhost:9200/b:products/_search?q=category:apparel' | jq '.hits.hits[]._source'
```

### 6.2 Query DSL example

```bash
curl -s -X POST 'localhost:9200/b:products/_search' \
  -H 'Content-Type: application/json' -d '{
  "query": { "range": { "price": { "lt": 30 } } },
  "sort":  [{ "price": "asc" }],
  "size":  10
}' | jq '.hits.hits[]._source'
```

---

## 7) Test Terms Aggregation (Remote)

### 7.1 Basic terms agg

```bash
curl -s -X POST 'localhost:9200/b:products/_search' \
  -H 'Content-Type: application/json' -d '{
  "size": 0,
  "aggs": {
    "by_category": {
      "terms": { "field": "category", "size": 10 }
    }
  }
}' | jq '.aggregations.by_category.buckets'
```

### 7.2 With sorting, shard_size, min_doc_count, missing

```bash
curl -s -X POST 'localhost:9200/b:products/_search' \
  -H 'Content-Type: application/json' -d '{
  "size": 0,
  "aggs": {
    "by_category": {
      "terms": {
        "field": "category",
        "order": { "_count": "desc" },
        "size": 10,
        "shard_size": 100,
        "min_doc_count": 1,
        "missing": "unknown"
      }
    }
  }
}' | jq '.aggregations.by_category.buckets'
```

### 7.3 Filter + aggregate

```bash
curl -s -X POST 'localhost:9200/b:products/_search' \
  -H 'Content-Type: application/json' -d '{
  "size": 0,
  "query": { "range": { "price": { "lt": 30 } } },
  "aggs": { "by_category": { "terms": { "field": "category", "size": 10 } } }
}' | jq '.aggregations.by_category.buckets'
```

### 7.4 Composite aggregation (large cardinality, paginated)

**Page 1**

```bash
curl -s -X POST 'localhost:9200/b:products/_search' \
  -H 'Content-Type: application/json' -d '{
  "size": 0,
  "aggs": {
    "by_category": {
      "composite": {
        "size": 2,
        "sources": [ { "category": { "terms": { "field": "category" } } } ]
      }
    }
  }
}'
```

Use `"after_key"` from the response for **next page**:

```bash
curl -s -X POST 'localhost:9200/b:products/_search' \
  -H 'Content-Type: application/json' -d '{
  "size": 0,
  "aggs": {
    "by_category": {
      "composite": {
        "size": 2,
        "sources": [ { "category": { "terms": { "field": "category" } } } ],
        "after": { "category": "REPLACE_ME" }
      }
    }
  }
}'
```

---

## 8) Troubleshooting

* **Remote not connected**: check seeds `"opensearch-b:9300"`, both containers on same network, and logs:

  ```bash
  docker logs opensearch-a
  docker logs opensearch-b
  curl -s localhost:9200/_remote/info | jq
  ```
* **Field type**: `terms` requires a `keyword` (or numeric/boolean) field, not analyzed `text`. Use `.keyword` subfield if needed.
* **Shard accuracy**: for many shards/high cardinality, increase `shard_size` or prefer **composite**.
* **Version drift**: use matching OpenSearch minor versions across clusters.

---

## 9) Cleanup

```bash
docker compose down -v
```

---

## 10) Hardening (Next Steps)

* Enable Security plugin and mTLS on **transport** for CCS, configure trusted CAs and roles.
* Add dedicated data nodes, ISM policies, and PIT/search-after for realistic CCS flows.
* Benchmark CCS latency/throughput and memory under aggregations and mixed local+remote queries.
