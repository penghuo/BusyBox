## Proposal

### Use case




* Shipping a new function json_at(path, mode) quickly:
  * Introduce in 1.7 behind FF=ppl.func.json_at_v1 (off by default).
  * Stabilize in 1.8 (enabled in Canary).
  * Enabled by default at PCL=7; still off at PCL≤6.

* Changing default NULL sort order (breaking):
  * Announce in 1.9 with FF=ppl.sort.nulls_last (opt-in).
  * Create PCL=8 where it is default-on; provide hint /*+ NULLS_FIRST */ and linter rewrite.
  * Remove legacy behavior no earlier than MAJOR 2.0 after two PCLs and an LTS cycle.


## SQL SERVER
COMPATIBILITY_LEVEL is a per-database setting that tells SQL Server to run T-SQL language parsing/semantics and query-optimizer behaviors as if the database were on a specific engine version, independent of the server binaries. In practice, it gates which T-SQL features are available and which optimizer rules (e.g., cardinality estimator, IQP features) apply. 
Microsoft Learn
+1

Key properties

Scope: Database-scoped; each database can pin its own level. 
Microsoft Learn

Values: Integer mapping to engine releases (e.g., 160 = SQL Server 2022). 
Microsoft Learn

Effects: T-SQL behavior and query processing choices are aligned to that level. 
Microsoft Learn

Inspection/Change:

View: SELECT name, compatibility_level FROM sys.databases; 
Stack Overflow

Change: ALTER DATABASE MyDb SET COMPATIBILITY_LEVEL = 160; (online operation). 
Microsoft Learn

Granular overrides: At the single-query level you can force optimizer behavior for a given level via the hint QUERY_OPTIMIZER_COMPATIBILITY_LEVEL_n.