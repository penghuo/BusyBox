```
val data = Seq(
  (30, "Alice"),
  (25, "Bob"),
  (35, "Charlie"),
  (28, "Tony"),
).toDF("age", "name")

data
  .repartition(2)  // Creates 2 files
  .write
  .mode("overwrite")
  .parquet("/Users/penghuo/oss/BusyBox/data/parquet/people")
```
