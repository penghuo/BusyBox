## lookup
The lookup command enriches your fact table by performing a left join with a lookup (dimension) table. Specifically, it:
1. Joins the fact table with the lookup table based on a join key (lookupMappingField). By default, the command appends all columns from the lookup table (except the join key) to the fact table. Alternatively, you can explicitly specify the desired output fields.
2. Resolves column name conflicts between the two tables using one of two strategies:
    * REPLACE: The lookup table’s value replaces the fact table’s value.
    * APPEND: The lookup table’s value is used only if the corresponding fact table column is missing or null.

## data
* fact table

id | col1 | col2
-- | -- | --
1 | a | b
2 | aa | bb
3 | null | ccc

* dimension table

id | col1 | col3
-- | -- | --
1 | x | y
3 | xx | yy

## query
* lookup default behaviour
```
source="fact.csv" | lookup "dim.csv" id 
```

id | col1 | col2 | col3
-- | -- | -- | --
1 | x | b | y
2 | null | bb | null
3 | xx | ccc | yy

* lookup with OUTPUT, same as default behaviour
```
source="fact.csv" | lookup "dim.csv" id OUTPUT
```

id | col1 | col2 | col3
-- | -- | -- | --
1 | x | b | y
2 | null | bb | null
3 | xx | ccc | yy

* lookup with OUTPUT with all fields
```
source="fact.csv" | lookup "dim.csv" id OUTPUT id, col1, col3
```

id | col1 | col2 | col3
-- | -- | -- | --
1 | x | b | y
null | null | bb | null
3 | xx | ccc | yy

* lookup with OUTPUT with rename columns
```
source="fact.csv" | lookup "dim.csv" id OUTPUT col1 as dimCol1
```

id | col1 | col2 | dimCol1
-- | -- | -- | --
1 | a | b | x
2 | aa | bb | null
3 | null | ccc | xx

* lookup with OUTPUTNEW
```
source="fact.csv" | lookup "dim.csv" id OUTPUTNEW
```
id | col1 | col2 | col3
-- | -- | -- | --
1 | a | b | y
2 | aa | bb | null
3 | xx | ccc | yy
* lookup with OUTPUTNEW
```
source="fact.csv" | lookup "dim.csv" id OUTPUTNEW id, col1, col3
```

id | col1 | col2 | col3
-- | -- | -- | --
1 | a | b | y
2 | aa | bb | null
3 | xx | ccc | yy

* lookup with OUTPUTNEW with rename columns
```
source="fact.csv" | lookup "dim.csv" id OUTPUTNEW col1 as dimCol1
```

id | col1 | col2 | dimCol1
-- | -- | -- | --
1 | a | b | x
2 | aa | bb | null
3 | null | ccc | xx