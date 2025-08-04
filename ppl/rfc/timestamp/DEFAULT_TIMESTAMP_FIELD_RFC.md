# RFC: Support Implicit Time Modifiers and Time Functions in PPL

## Metadata
- **RFC Number:** TBD
- **Date:** July 31, 2025
- **Status:** Draft

## Introduction

This RFC proposes the introduction of implicit time modifiers and functions in PPL (Piped Processing Language) to improve user experience when working with time-based queries. Currently, users must explicitly specify timestamp fields in queries involving time operations, which leads to repetitive code and reduced readability. By establishing conventions for time operations, common time-based queries can be simplified while maintaining flexibility for diverse index patterns.

The proposal addresses several key use cases:
1. Applying time range filters (`earliest=-1d`) without explicitly naming the timestamp field
2. Using time-based aggregations (`span=5m`) with implicit timestamp field references
3. Leveraging time functions (`_time()`) that automatically use the timestamp field

## Background

### Current Behavior

Currently in PPL, timestamp operations require explicit field specification:

```sql
search source=my-index | where @timestamp >= "2023-01-01" | stats count() by span(@timestamp, 1h)
```

This approach:
- Requires repetitive field references
- Reduces query readability
- Creates friction when working across multiple indices with differently named timestamp fields
- Makes time-based operations more verbose than necessary

### Industry Context

Other query languages and analytics platforms often provide implicit timestamp handling:

- Elasticsearch query DSL supports a default `@timestamp` field for time-based operations
- Splunk Search Processing Language (SPL) has the `_time` field which serves as the default timestamp
- Many time-series databases provide special syntax for time-based operations

## Expected Query Behavior

The following query behaviors will be implemented:

### Time Range Operations

When using time range shorthand like `earliest` and `latest`, the default timestamp field will be used:

```sql
-- Before: Explicit timestamp reference
search source=my-index | where @timestamp >= now() - 1d

-- After: Implicit use of default timestamp field
search source=my-index | where earliest=-1d
```

### Time-based Aggregations

When specifying `span` without an explicit field, the default timestamp field will be used:

```sql
-- Before: Explicit timestamp in span
search source=my-index | stats count() by span(@timestamp, 5m)

-- After: Implicit use of default timestamp field
search source=my-index | stats count() by span(5m)
```

### Time Functions

The `_time()` function will return the value of the default timestamp field:

```sql
-- Before: No direct equivalent, would require explicit field access
search source=my-index | eval hour_of_day = hour(@timestamp)

-- After: Using _time() function with default timestamp
search source=my-index | eval hour_of_day = hour(_time())
```

## Implementation Approach

The system will implement the following approach:

1. All implicit time operations (`earliest`, `latest`, `span` without field, `_time()` function) will use `@timestamp` as the default field
2. Explicit field references will always take precedence over the default field
3. If the `@timestamp` field is not present in an index, any implicit time operation will throw an "@timestamp not found" exception
4. For backward compatibility, existing queries with explicit timestamp references will continue to work without modification

## Frequently Asked Questions

### Q1: My index has a date field, but it's named "time" instead of "@timestamp". How do I query it with PPL?

**Option 1:** You can add a field alias in your index mapping that points "time" field to "@timestamp":

```json
PUT my-index/_mapping
{
  "properties": {
    "@timestamp": {
      "type": "alias",
      "path": "time"
    }
  }
}
```

After adding this alias, all queries using the default timestamp field (or explicitly referencing @timestamp) will work as expected.

**Option 2:** You can continue using explicit field references in your queries:

```sql
search source=my-index time>="2023-07-31 00:00:00" | stats count() by span(time, 5m)
```

### Q2: My index doesn't have any date field. How do I query it with PPL?

For indices without a timestamp field, time-based operations will behave as follows:

- Time range operations (`earliest`, `latest`) will throw a "@timestamp not found" exception
- Time-based aggregations (`span` without a field) will throw a "@timestamp not found" exception
- The `_time()` function will return null or throw a "@timestamp not found" exception

For such indices, you should avoid using timestamp-dependent features or explicitly provide field references where applicable.
