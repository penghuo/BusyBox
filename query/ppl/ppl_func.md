# OpenSearch PPL Functions

This document provides a comprehensive list of Piped Processing Language (PPL) functions available in OpenSearch.

## Mathematical Functions

| Function | Description | Documentation Link |
|---------|-------------|-------------------|
| ABS | Calculates the absolute value of a number | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#abs) |
| ACOS | Calculates the arc cosine of x; returns NULL if x is not in the range -1 to 1 | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#acos) |
| ASIN | Calculates the arc sine of x; returns NULL if x is not in the range -1 to 1 | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#asin) |
| ATAN | Calculates the arc tangent of x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#atan) |
| ATAN2 | Calculates the arc tangent of y/x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#atan2) |
| CEIL | Rounds a value up to the nearest integer | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#ceil) |
| CEILING | Rounds a value up to the nearest integer (alias for CEIL) | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#ceiling) |
| CONV | Converts a number between different number bases | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#conv) |
| COS | Calculates the cosine of x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#cos) |
| E | Returns the value of e (the base of natural logarithms) | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#e) |
| EXP | Calculates e raised to the power of x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#exp) |
| FLOOR | Rounds a value down to the nearest integer | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#floor) |
| LN | Calculates the natural logarithm of x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#ln) |
| LOG | Calculates the natural logarithm of x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#log) |
| LOG2 | Calculates the base-2 logarithm of x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#log2) |
| LOG10 | Calculates the base-10 logarithm of x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#log10) |
| MOD | Calculates the remainder of a division operation | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#mod) |
| PI | Returns the value of π (pi) | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#pi) |
| POW | Calculates x raised to the power of y | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#pow) |
| POWER | Calculates x raised to the power of y (alias for POW) | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#power) |
| RADIANS | Converts a value in degrees to radians | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#radians) |
| RAND | Generates a random floating-point value between 0 and 1 | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#rand) |
| ROUND | Rounds a value to the nearest integer or to a specified number of decimal places | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#round) |
| SIGN | Returns the sign of a numeric value | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#sign) |
| SIN | Calculates the sine of x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#sin) |
| SQRT | Calculates the square root of x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#sqrt) |
| CBRT | Calculates the cube root of x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#cbrt) |
| TAN | Calculates the tangent of x | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#tan) |
| TRUNCATE | Truncates a number to a specified number of decimal places | [math.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/math.rst#truncate) |

## String Functions

| Function | Description | Documentation Link |
|---------|-------------|-------------------|
| CONCAT | Concatenates up to 9 strings together | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#concat) |
| CONCAT_WS | Concatenates strings with a separator | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#concat_ws) |
| LENGTH | Returns the length of a string | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#length) |
| LOWER | Converts a string to lowercase | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#lower) |
| LTRIM | Removes leading whitespace from a string | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#ltrim) |
| POSITION | Returns the position of a substring in a string | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#position) |
| REPLACE | Replaces occurrences of a substring within a string | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#replace) |
| REVERSE | Reverses the characters in a string | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#reverse) |
| RIGHT | Extracts a specified number of rightmost characters from a string | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#right) |
| RTRIM | Removes trailing whitespace from a string | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#rtrim) |
| SUBSTRING | Extracts a substring from a string | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#substring) |
| TRIM | Removes both leading and trailing whitespace from a string | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#trim) |
| UPPER | Converts a string to uppercase | [string.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/string.rst#upper) |

## Date and Time Functions

| Function | Description | Documentation Link |
|---------|-------------|-------------------|
| ADDDATE | Synonym for DATE_ADD | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#adddate) |
| ADDTIME | Adds time values | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#addtime) |
| CURRENT_TIME | Returns the current time | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#current_time) |
| CURRENT_TIMESTAMP | Returns the current date and time | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#current_timestamp) |
| CURTIME | Returns the current time | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#curtime) |
| DATE | Extracts the date part from a datetime expression | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#date) |
| DATE_ADD | Adds a specified time interval to a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#date_add) |
| DATE_FORMAT | Formats a date/time value according to a specified format | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#date_format) |
| DATETIME | Converts a value to a datetime | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#datetime) |
| DATE_SUB | Subtracts a specified time interval from a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#date_sub) |
| DATEDIFF | Returns the difference between two dates | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#datediff) |
| DAY | Extracts the day of the month from a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#day) |
| DAYNAME | Returns the name of the weekday | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#dayname) |
| DAYOFMONTH | Extracts the day of the month from a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#dayofmonth) |
| DAY_OF_MONTH | Synonym for DAYOFMONTH | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#day_of_month) |
| DAYOFWEEK | Returns the weekday index for a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#dayofweek) |
| DAY_OF_WEEK | Synonym for DAYOFWEEK | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#day_of_week) |
| DAYOFYEAR | Returns the day of the year for a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#dayofyear) |
| DAY_OF_YEAR | Synonym for DAYOFYEAR | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#day_of_year) |
| EXTRACT | Extracts parts from a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#extract) |
| FROM_DAYS | Converts a day number to a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#from_days) |
| HOUR | Extracts the hour from a time/datetime | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#hour) |
| HOUR_OF_DAY | Extracts the hour from a time/datetime | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#hour_of_day) |
| LAST_DAY | Returns the last day of the month for a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#last_day) |
| LOCALTIMESTAMP | Returns the current date and time | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#localtimestamp) |
| LOCALTIME | Returns the current date and time | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#localtime) |
| MAKEDATE | Creates a date from year and day-of-year values | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#makedate) |
| MAKETIME | Creates a time from hour, minute, and second values | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#maketime) |
| MICROSECOND | Returns the microseconds from a time/datetime | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#microsecond) |
| MINUTE | Extracts the minute from a time/datetime | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#minute) |
| MINUTE_OF_DAY | Returns the minute within the day | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#minute_of_day) |
| MINUTE_OF_HOUR | Synonym for MINUTE | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#minute_of_hour) |
| MONTH | Extracts the month from a date/datetime | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#month) |
| MONTH_OF_YEAR | Synonym for MONTH | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#month_of_year) |
| MONTHNAME | Returns the name of the month for a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#monthname) |
| NOW | Returns the current date and time | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#now) |
| PERIOD_ADD | Adds a period to a year-month | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#period_add) |
| PERIOD_DIFF | Returns the difference between periods | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#period_diff) |
| QUARTER | Returns the quarter of the year for a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#quarter) |
| SECOND | Extracts the second from a time/datetime | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#second) |
| SEC_TO_TIME | Converts seconds to time format | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#sec_to_time) |
| SUBDATE | Synonym for DATE_SUB | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#subdate) |
| SUBTIME | Subtracts a time value from another | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#subtime) |
| SYSDATE | Returns the current date and time | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#sysdate) |
| TIME | Extracts the time portion from a datetime expression | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#time) |
| TIME_FORMAT | Formats a time by a specified format | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#time_format) |
| TIME_TO_SEC | Converts time to seconds | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#time_to_sec) |
| TIMEDIFF | Returns the difference between two time expressions | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#timediff) |
| TIMESTAMP | Converts an expression to a datetime value | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#timestamp) |
| TIMESTAMPADD | Adds an interval to a datetime expression | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#timestampadd) |
| TIMESTAMPDIFF | Returns the difference between two datetime expressions | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#timestampdiff) |
| TO_DAYS | Returns the day number for a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#to_days) |
| TO_SECONDS | Converts a date or datetime to seconds since Year 0 | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#to_seconds) |
| UNIX_TIMESTAMP | Returns a Unix timestamp | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#unix_timestamp) |
| UTC_DATE | Returns the current UTC date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#utc_date) |
| UTC_TIME | Returns the current UTC time | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#utc_time) |
| UTC_TIMESTAMP | Returns the current UTC date and time | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#utc_timestamp) |
| WEEK | Returns the week number for a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#week) |
| WEEKDAY | Returns the weekday index for a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#weekday) |
| WEEK_OF_YEAR | Returns the calendar week of the year for a date | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#week_of_year) |
| YEAR | Extracts the year from a date/datetime | [datetime.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/datetime.rst#year) |

## Condition Functions

| Function | Description | Documentation Link |
|---------|-------------|-------------------|
| CASE | Evaluates a list of conditions and returns a corresponding result | [condition.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/condition.rst#case) |
| IF | Returns one value if a condition is true and another value if a condition is false | [condition.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/condition.rst#if) |
| IFNULL | Returns the first non-NULL value in a list | [condition.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/condition.rst#ifnull) |
| NULLIF | Returns NULL if two expressions are equal, otherwise returns the first expression | [condition.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/condition.rst#nullif) |
| ISNULL | Tests whether a value is NULL | [condition.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/condition.rst#isnull) |
| COALESCE | Returns the first non-NULL value in a list | [condition.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/condition.rst#coalesce) |
| GREATEST | Returns the largest value from a list of expressions | [condition.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/condition.rst#greatest) |
| LEAST | Returns the smallest value from a list of expressions | [condition.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/condition.rst#least) |

## Conversion Functions

| Function | Description | Documentation Link |
|---------|-------------|-------------------|
| CAST | Converts a value from one data type to another | [conversion.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/conversion.rst#cast) |
| CONVERT | Converts a value from one data type to another | [conversion.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/conversion.rst#convert) |

## Collection Functions

| Function | Description | Documentation Link |
|---------|-------------|-------------------|
| ARRAY | Creates an array from a list of values | [collection.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/collection.rst#array) |
| ARRAY_CONCAT | Concatenates arrays | [collection.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/collection.rst#array_concat) |
| ARRAY_CONTAINS | Checks if an array contains a specific value | [collection.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/collection.rst#array_contains) |
| ARRAY_DISTINCT | Returns an array with distinct values | [collection.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/collection.rst#array_distinct) |
| ARRAY_LENGTH | Returns the length of an array | [collection.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/collection.rst#array_length) |
| ARRAY_REMOVE | Removes all elements from an array that match a specified value | [collection.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/collection.rst#array_remove) |
| ARRAY_SORT | Sorts an array in ascending order | [collection.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/collection.rst#array_sort) |

## JSON Functions

| Function | Description | Documentation Link |
|---------|-------------|-------------------|
| JSON_EXTRACT | Extracts data from a JSON document | [json.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/json.rst#json_extract) |
| JSON_EXTRACT_SCALAR | Extracts a scalar value from a JSON document | [json.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/json.rst#json_extract_scalar) |

## IP Functions

| Function | Description | Documentation Link |
|---------|-------------|-------------------|
| CIDR_MATCH | Tests whether an IP address is contained within a CIDR block | [ip.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/ip.rst#cidr_match) |

## System Functions

| Function | Description | Documentation Link |
|---------|-------------|-------------------|
| USER | Returns the current user's username | [system.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/system.rst#user) |
| VERSION | Returns the current version of the database | [system.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/system.rst#version) |

## Cryptographic Functions

| Function | Description | Documentation Link |
|---------|-------------|-------------------|
| ISEMPTY | Tests if a field is empty or NULL | [cryptographic.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/cryptographic.rst#isempty) |
| ISBLANK | Tests if a string field is blank (empty or only whitespace) | [cryptographic.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/cryptographic.rst#isblank) |
| ISPRESENT | Tests if a field is present and not NULL | [cryptographic.rst](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions/cryptographic.rst#ispresent) |

## References

All functions are documented in the [OpenSearch SQL repository](https://github.com/opensearch-project/sql/tree/main/docs/user/ppl/functions).
