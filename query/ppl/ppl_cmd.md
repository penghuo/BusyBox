# OpenSearch PPL Commands

This document provides a comprehensive list of Piped Processing Language (PPL) commands available in OpenSearch.

| Command | Category | Description | Documentation Link |
|---------|----------|-------------|-------------------|
| ad | Analytics | Anomaly detection command for identifying unusual patterns in data | [ad.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/ad.rst) |
| appendcol | Data Manipulation | Appends columns to the result set | [appendcol.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/appendcol.rst) |
| dedup | Data Manipulation | Removes duplicate results from data | [dedup.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/dedup.rst) |
| describe | Metadata | Returns the schema of a table or index | [describe.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/describe.rst) |
| eval | Data Manipulation | Calculates an expression and adds the result to the search output | [eval.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/eval.rst) |
| expand | Data Manipulation | Expands multi-value fields into separate rows | [expand.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/expand.rst) |
| explain | Performance | Returns the execution plan for a PPL query | [explain.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/explain.rst) |
| fields | Data Manipulation | Selects fields to include or exclude from search results | [fields.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/fields.rst) |
| fillnull | Data Manipulation | Replaces null values in search results with a specified value | [fillnull.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/fillnull.rst) |
| flatten | Data Manipulation | Flattens nested data structures into simple tabular format | [flatten.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/flatten.rst) |
| grok | Data Manipulation | Parses unstructured text into structured data | [grok.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/grok.rst) |
| head | Data Manipulation | Returns the first N results of a search | [head.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/head.rst) |
| information_schema | Metadata | Returns metadata about indices and their fields | [information_schema.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/information_schema.rst) |
| join | Data Manipulation | Combines records from two or more tables | [join.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/join.rst) |
| kmeans | Analytics | Performs k-means clustering on dataset | [kmeans.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/kmeans.rst) |
| lookup | Data Manipulation | Performs lookups from an external dataset | [lookup.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/lookup.rst) |
| ml | Analytics | Machine learning operations | [ml.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/ml.rst) |
| parse | Data Manipulation | Extracts fields from raw text based on a pattern | [parse.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/parse.rst) |
| patterns | Analytics | Identifies patterns in the data | [patterns.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/patterns.rst) |
| rare | Analytics | Finds the least common values in a field | [rare.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/rare.rst) |
| rename | Data Manipulation | Renames fields in the search results | [rename.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/rename.rst) |
| search | Search | Primary command for retrieving data from indices | [search.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/search.rst) |
| showdatasources | Metadata | Lists available data sources (indices) | [showdatasources.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/showdatasources.rst) |
| sort | Data Manipulation | Sorts results by specified fields | [sort.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/sort.rst) |
| stats | Analytics | Calculates statistics like count, sum, avg on the data | [stats.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/stats.rst) |
| subquery | Data Manipulation | Allows embedding a query within another query | [subquery.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/subquery.rst) |
| syntax | Reference | Describes PPL syntax and usage | [syntax.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/syntax.rst) |
| top | Analytics | Returns the most common values in a field | [top.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/top.rst) |
| trendline | Analytics | Generates trend lines based on time series data | [trendline.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/trendline.rst) |
| where | Data Manipulation | Filters results based on a condition | [where.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd/where.rst) |

## Categories

The commands are categorized as follows:

1. **Search** - Core search functionality
2. **Data Manipulation** - Commands that transform, filter, or modify data
3. **Analytics** - Commands for statistical analysis and machine learning
4. **Metadata** - Commands that provide information about data structure
5. **Performance** - Commands related to query performance and optimization
6. **Reference** - Documentation and syntax reference

## References

All commands are documented in the [OpenSearch SQL repository](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/cmd).
