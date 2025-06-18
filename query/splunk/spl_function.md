# Splunk SPL Functions Reference

This document provides a comprehensive reference for Splunk Search Processing Language (SPL) functions organized by category.

## Table of Contents
- [Evaluation Functions](#evaluation-functions)
  - [Bitwise Functions](#bitwise-functions)
  - [Comparison Functions](#comparison-functions)
  - [Conditional Functions](#conditional-functions)
  - [Conversion Functions](#conversion-functions)
  - [Cryptographic Functions](#cryptographic-functions)
  - [Date & Time Functions](#date--time-functions)
  - [Information Functions](#information-functions)
  - [IP Functions](#ip-functions)
  - [JSON Functions](#json-functions)
  - [Mathematical Functions](#mathematical-functions)
  - [Multivalue Functions](#multivalue-functions)
  - [Search Functions](#search-functions)
  - [String Functions](#string-functions)
  - [Type Checking Functions](#type-checking-functions)
  - [URL Functions](#url-functions)
  - [XML Functions](#xml-functions)
- [Statistical and Charting Functions](#statistical-and-charting-functions)
  - [Aggregation Functions](#aggregation-functions)
  - [Distribution Functions](#distribution-functions)
  - [Prediction Functions](#prediction-functions)
  - [Time Series Functions](#time-series-functions)
  - [Correlation Functions](#correlation-functions)

## Evaluation Functions

### Bitwise Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| bitnot() | Bitwise NOT operation | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/BitwiseFunctions#bitnot.28X.29) |
| bitand() | Bitwise AND operation | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/BitwiseFunctions#bitand.28X.2C_Y.2C_...) |
| bitor() | Bitwise OR operation | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/BitwiseFunctions#bitor.28X.2C_Y.2C_...) |
| bitxor() | Bitwise XOR operation | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/BitwiseFunctions#bitxor.28X.2C_Y.2C_...) |
| shiftleft() | Shift bits to the left | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/BitwiseFunctions#shiftleft.28X.2C_Y.29) |
| shiftright() | Shift bits to the right | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/BitwiseFunctions#shiftright.28X.2C_Y.29) |

### Comparison Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| = | Equal to | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/CommonEvalFunctions#.3D_equal_to) |
| == | Equal to (alternate syntax) | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/CommonEvalFunctions#.3D.3D_equal_to) |
| != | Not equal to | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/CommonEvalFunctions#.21.3D_not_equal_to) |
| < | Less than | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/CommonEvalFunctions#.3C_less_than) |
| <= | Less than or equal to | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/CommonEvalFunctions#.3C.3D_less_than_or_equal_to) |
| > | Greater than | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/CommonEvalFunctions#.3E_greater_than) |
| >= | Greater than or equal to | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/CommonEvalFunctions#.3E.3D_greater_than_or_equal_to) |

### Conditional Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| if() | Returns value based on condition | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConditionalFunctions#if.28X.2CY.2CZ.29) |
| case() | Returns value based on multiple conditions | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConditionalFunctions#case.28X.2CY.2C...) |
| coalesce() | Returns first non-null value | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConditionalFunctions#coalesce.28X.2C_Y.2C_...) |
| nullif() | Returns null if X equals Y, else X | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConditionalFunctions#nullif.28X.2C_Y.29) |
| isnotnull() | Tests if value is not null | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConditionalFunctions#isnotnull.28X.29) |
| isnull() | Tests if value is null | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConditionalFunctions#isnull.28X.29) |
| true() | Returns boolean value true | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConditionalFunctions#true.28.29) |
| false() | Returns boolean value false | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConditionalFunctions#false.28.29) |

### Conversion Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| tonumber() | Converts to number | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConversionFunctions#tonumber.28X.2C_Y.29) |
| tostring() | Converts to string | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConversionFunctions#tostring.28X.2C_Y.29) |
| toboolean() | Converts to boolean | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConversionFunctions#toboolean.28X.29) |
| typeof() | Returns type of value | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/ConversionFunctions#typeof.28X.29) |

### Cryptographic Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| md5() | Calculates MD5 hash | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/CryptographicFunctions#md5.28X.29) |
| sha1() | Calculates SHA1 hash | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/CryptographicFunctions#sha1.28X.29) |
| sha256() | Calculates SHA256 hash | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/CryptographicFunctions#sha256.28X.29) |
| sha512() | Calculates SHA512 hash | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/CryptographicFunctions#sha512.28X.29) |

### Date & Time Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| now() | Returns current time | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/DateandTimeFunctions#now.28.29) |
| time() | Returns time value | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/DateandTimeFunctions#time.28.29) |
| relative_time() | Returns time relative to specified time | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/DateandTimeFunctions#relative_time.28X.2CY.29) |
| strftime() | Formats time | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/DateandTimeFunctions#strftime.28X.2CY.29) |
| strptime() | Parses time | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/DateandTimeFunctions#strptime.28X.2CY.29) |
| mktime() | Creates time from parts | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/DateandTimeFunctions#mktime.28.29) |
| mytime() | Returns current time for evaluation | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/DateandTimeFunctions#mytime.28.29) |

### Information Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| info_max_time | Returns maximum time of events | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/InformationFunctions#info_max_time.28.29) |
| info_min_time | Returns minimum time of events | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/InformationFunctions#info_min_time.28.29) |
| info_search_time | Returns search execution time | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/InformationFunctions#info_search_time.28.29) |

### IP Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| cidrmatch() | Tests if IP is in CIDR range | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/IPFunctions#cidrmatch.28subnet.2C_ip.29) |
| ipv4_is_private() | Tests if IPv4 address is private | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/IPFunctions#ipv4_is_private.28X.29) |
| ipv6_is_private() | Tests if IPv6 address is private | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/IPFunctions#ipv6_is_private.28X.29) |

### JSON Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| json_extract() | Extracts values from JSON | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/JSONFunctions#json_extract.28X.29) |
| json_keys() | Returns keys from JSON | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/JSONFunctions#json_keys.28X.29) |
| json_valid() | Tests if JSON is valid | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/JSONFunctions#json_valid.28X.29) |
| spath() | Extracts fields from JSON/XML | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/JSONFunctions#spath.28X.2C_Y.29) |

### Mathematical Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| abs() | Returns absolute value | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#abs.28X.29) |
| ceiling() | Rounds up to nearest integer | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#ceiling.28X.29) |
| floor() | Rounds down to nearest integer | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#floor.28X.29) |
| round() | Rounds to nearest integer | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#round.28X.29) |
| sqrt() | Returns square root | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#sqrt.28X.29) |
| exp() | Returns e raised to power | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#exp.28X.29) |
| ln() | Returns natural logarithm | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#ln.28X.29) |
| log() | Returns base-10 logarithm | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#log.28X.2C_Y.29) |
| pow() | Returns X raised to power Y | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#pow.28X.2C_Y.29) |
| pi() | Returns value of pi | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#pi.28.29) |
| random() | Returns random number | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#random.28.29) |
| sigfig() | Rounds to significant figures | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MathematicalFunctions#sigfig.28X.2C_Y.29) |

### Multivalue Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| mvappend() | Appends values to multivalue field | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MultivalueFunctions#mvappend.28X.2C_Y.2C_...) |
| mvcount() | Counts values in multivalue field | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MultivalueFunctions#mvcount.28X.29) |
| mvdedup() | Removes duplicate values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MultivalueFunctions#mvdedup.28X.29) |
| mvfilter() | Filters values in multivalue field | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MultivalueFunctions#mvfilter.28X.29) |
| mvfind() | Finds index of value in multivalue field | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MultivalueFunctions#mvfind.28X.2C_Y.29) |
| mvindex() | Returns value at index | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MultivalueFunctions#mvindex.28X.2C_Y.29) |
| mvjoin() | Joins multivalue field values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MultivalueFunctions#mvjoin.28X.2C_Y.29) |
| mvrange() | Creates multivalue field with range | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MultivalueFunctions#mvrange.28X.2C_Y.2C_Z.29) |
| mvsort() | Sorts values in multivalue field | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MultivalueFunctions#mvsort.28X.29) |
| mvzip() | Combines multivalue fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/MultivalueFunctions#mvzip.28X.2C_Y.2C_Z.29) |

### Search Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| match() | Tests if string matches regex | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#match.28X.2C_Y.29) |
| like() | Pattern matching with wildcards | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#like.28X.2C_Y.29) |
| searchmatch() | Tests if event matches search expression | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/SearchStringFunctions#searchmatch.28X.29) |
| rex() | Extracts fields using regex | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Rex) |

### String Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| len() | Returns length of string | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#len.28X.29) |
| lower() | Converts to lowercase | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#lower.28X.29) |
| upper() | Converts to uppercase | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#upper.28X.29) |
| replace() | Replaces string patterns | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#replace.28X.2C_Y.2C_Z.29) |
| substr() | Returns substring | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#substr.28X.2C_Y.2C_Z.29) |
| trim() | Removes leading and trailing whitespace | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#trim.28X.29) |
| ltrim() | Removes leading whitespace | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#ltrim.28X.29) |
| rtrim() | Removes trailing whitespace | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#rtrim.28X.29) |
| split() | Splits string into multivalue field | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#split.28X.2C.22Y.22.29) |
| strcat() | Concatenates strings | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#strcat.28X.2CY.2C...29) |
| strlen() | Returns string length | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#strlen.28X.29) |
| strpos() | Returns position of substring | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StringFunctions#strpos.28X.2C_Y.29) |

### Type Checking Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| isint() | Tests if value is integer | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/TypeChecking#isint.28X.29) |
| isnotnull() | Tests if value is not null | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/TypeChecking#isnotnull.28X.29) |
| isnull() | Tests if value is null | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/TypeChecking#isnull.28X.29) |
| isnum() | Tests if value is number | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/TypeChecking#isnum.28X.29) |
| isstr() | Tests if value is string | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/TypeChecking#isstr.28X.29) |

### URL Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| urldecode() | Decodes URL-encoded string | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/URLFunctions#urldecode.28X.29) |
| urlencode() | URL-encodes string | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/URLFunctions#urlencode.28X.29) |
| validate() | Validates field against regex | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/URLFunctions#validate.28X.2C_Y.29) |

### XML Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| xmlkv() | Extracts XML key-value pairs | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/XMLFunctions#xmlkv.28X.29) |
| xpath() | Extracts values using XPath | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/XMLFunctions#xpath.28X.2C_Y.29) |

## Statistical and Charting Functions

### Aggregation Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| avg() | Average of values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#avg.28X.29) |
| count() | Count of events | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#count.28.29) |
| count(distinct) | Count of unique values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#count.28distinct_X.29) |
| dc() | Count of distinct values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#dc.28X.29) |
| distinct_count() | Count of unique values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#distinct_count.28X.29) |
| estdc() | Estimated count of distinct values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#estdc.28X.29) |
| exactperc() | Calculate exact percentile | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#exactperc.28X.2C_Y.29) |
| first() | First value | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#first.28X.29) |
| last() | Last value | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#last.28X.29) |
| max() | Maximum value | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#max.28X.29) |
| mean() | Average of values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#mean.28X.29) |
| median() | Median of values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#median.28X.29) |
| min() | Minimum value | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#min.28X.29) |
| mode() | Mode of values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#mode.28X.29) |
| range() | Range of values (max-min) | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#range.28X.29) |
| stdev() | Standard deviation | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#stdev.28X.29) |
| stdevp() | Population standard deviation | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#stdevp.28X.29) |
| sum() | Sum of values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#sum.28X.29) |
| sumsq() | Sum of squared values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#sumsq.28X.29) |
| values() | List of distinct values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#values.28X.29) |
| var() | Variance | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#var.28X.29) |
| varp() | Population variance | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#varp.28X.29) |

### Distribution Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| percentile() | Calculate percentile | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#percentile.28X.2C_Y.29) |
| perc() | Calculate percentiles | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#perc.28X.2C_Y.29) |
| exactperc() | Calculate exact percentile | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#exactperc.28X.2C_Y.29) |
| upperperc() | Calculate upper percentile | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#upperperc.28X.2C_Y.29) |
| lowerperc() | Calculate lower percentile | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatsFunctions#lowerperc.28X.2C_Y.29) |

### Prediction Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| predict() | Predict future values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Predict) |
| forecast() | Forecast future values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/StatisticalandchartingfunctionStandalones#forecast.28.29) |

### Time Series Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| trendline() | Generate trendline | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Trendline) |
| anomalies() | Detect anomalies in time series | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Anomalies) |
| timechart() | Create time-based chart | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Timechart) |

### Correlation Functions

| Function | Description | Documentation Link |
|----------|-------------|-------------------|
| correlate() | Calculate correlation | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Correlate) |
| contingency() | Create contingency table | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Contingency) |
