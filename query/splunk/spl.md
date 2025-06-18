# Splunk SPL Knowledge Base

## Commands

| Command | Category | Description | Documentation Link |
|---------|----------|-------------|-------------------|
| abstract | Transforming | Provides summary information about fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Abstract) |
| accum | Transforming | Keeps a running total of specified fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Accum) |
| addcoltotals | Transforming | Computes column totals for a result set | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Addcoltotals) |
| addinfo | Reporting | Adds fields containing search information | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Addinfo) |
| addtotals | Transforming | Computes total for specified fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Addtotals) |
| analyzefields | Organizing | Analyzes field values to find patterns | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Analyzefields) |
| anomalies | Analyzing | Computes anomalies in timeseries data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Anomalies) |
| anomalousvalue | Analyzing | Computes anomalous values in result set | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Anomalousvalue) |
| append | Combining | Appends results from subsearches | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Append) |
| appendcols | Combining | Appends columns from subsearches | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Appendcols) |
| appendpipe | Combining | Appends results from other pipelines | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Appendpipe) |
| arules | Analyzing | Finds association rules in data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Arules) |
| associate | Analyzing | Finds field value correlations | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Associate) |
| audit | Organizing | Filters search terms against audit index | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Audit) |
| autoregress | Analyzing | Creates predictions based on historical data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Autoregress) |
| bin | Organizing | Bins numerical fields into discrete values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Bin) |
| bucket | Organizing | Alias for the bin command | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Bucket) |
| chart | Transforming | Creates statistical charts | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Chart) |
| cluster | Analyzing | Clusters similar events | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Cluster) |
| cofilter | Analyzing | Filters events based on coincidence of values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Cofilter) |
| collect | Data Management | Puts search results into a summary index | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Collect) |
| concurrency | Analyzing | Calculates concurrent usage patterns | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Concurrency) |
| contingency | Analyzing | Creates a contingency table | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Contingency) |
| convert | Transforming | Converts field values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Convert) |
| correlate | Analyzing | Calculates correlation between fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Correlate) |
| count | Transforming | Returns count of matching events | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Count) |
| ctable | Transforming | Creates a contingency table | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Ctable) |
| datamodel | Data Management | Retrieve data from data models | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Datamodel) |
| dbinspect | Data Management | Returns information about Splunk indexes | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Dbinspect) |
| dedup | Organizing | Removes duplicates from results | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Dedup) |
| delete | Data Management | Removes events from index | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Delete) |
| delta | Transforming | Computes delta between successive values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Delta) |
| diff | Comparing | Compares result sets | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Diff) |
| erex | Extracting | Extracts regex pattern from examples | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Erex) |
| eval | Calculating | Calculates an expression | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Eval) |
| eventcount | Searching | Returns the count of events in an index | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Eventcount) |
| eventstats | Transforming | Adds calculated fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Eventstats) |
| extract | Extracting | Extracts fields using regular expressions | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Extract) |
| fieldformat | Transforming | Formats field values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Fieldformat) |
| fields | Filtering | Removes or keeps fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Fields) |
| fieldsummary | Reporting | Provides statistical summaries of fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Fieldsummary) |
| filldown | Transforming | Fills in null values with previous non-null values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Filldown) |
| fillnull | Transforming | Replaces null values with specified value | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Fillnull) |
| find | Searching | Finds events that match specified criteria | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Find) |
| findtypes | Analyzing | Determines event source types | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Findtypes) |
| folderize | Organizing | Creates folder paths from field values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Folderize) |
| foreach | Looping | Runs commands on field values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Foreach) |
| format | Transforming | Formats results as specified | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Format) |
| from | Data Input | Retrieves events from dataset | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/From) |
| gauge | Visualizing | Creates a gauge visualization | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Gauge) |
| gentimes | Data Input | Generates time ranges | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Gentimes) |
| geom | Visualizing | Applies geographic operations | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Geom) |
| geomfilter | Filtering | Filters events based on geographic criteria | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Geomfilter) |
| geostats | Visualizing | Generates statistics for geographic data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Geostats) |
| head | Filtering | Returns the first N results | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Head) |
| highlight | Transforming | Highlights specified terms | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Highlight) |
| history | Reporting | Returns search history | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/History) |
| iconify | Visualizing | Adds icons to results | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Iconify) |
| input | Data Input | Retrieves data from input source | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Input) |
| inputcsv | Data Input | Loads data from CSV file | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Inputcsv) |
| inputlookup | Data Input | Loads data from lookup file | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Inputlookup) |
| iplocation | Enriching | Adds location information to IP addresses | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Iplocation) |
| join | Combining | Joins results with common field values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Join) |
| kmeans | Analyzing | Performs k-means clustering | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Kmeans) |
| kvform | Transforming | Formats results in key-value form | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Kvform) |
| loadjob | Data Input | Loads results from another search job | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Loadjob) |
| localize | Transforming | Converts UTC times to local timezone | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Localize) |
| localop | Processing | Performs operations locally | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Localop) |
| lookup | Enriching | Enhances events with lookups | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Lookup) |
| makecontinuous | Transforming | Creates continuous data from sparse data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Makecontinuous) |
| makemv | Transforming | Converts field values to multivalue fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Makemv) |
| makeresults | Data Input | Creates arbitrary results | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Makeresults) |
| map | Transforming | Maps search results through eval expressions | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Map) |
| mcollect | Data Management | Writes metrics to metric index | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Mcollect) |
| metadata | Reporting | Returns metadata about sources, sourcetypes, and hosts | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Metadata) |
| metasearch | Reporting | Retrieves metadata about search jobs | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Metasearch) |
| meventcollect | Data Management | Writes multiple metric values to metric index | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Meventcollect) |
| mstats | Reporting | Returns statistical information from metric data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Mstats) |
| multikv | Extracting | Extracts fields from table-formatted events | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Multikv) |
| multisearch | Combining | Combines multiple searches | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Multisearch) |
| mvcombine | Transforming | Combines multivalue fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Mvcombine) |
| mvexpand | Transforming | Expands multivalue fields into separate events | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Mvexpand) |
| nomv | Transforming | Converts multivalue fields to single value | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Nomv) |
| outlier | Analyzing | Removes outliers from numerical data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Outlier) |
| outputcsv | Data Output | Outputs results to CSV file | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Outputcsv) |
| outputlookup | Data Output | Outputs results to lookup file | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Outputlookup) |
| outputtext | Data Output | Outputs results as raw text | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Outputtext) |
| overlap | Analyzing | Finds overlapping field values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Overlap) |
| pivot | Data Navigation | Pivots data using data model | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Pivot) |
| predict | Analyzing | Predicts future values based on historical data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Predict) |
| rangemap | Transforming | Maps ranges of values to discrete values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Rangemap) |
| rare | Reporting | Finds the least common field values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Rare) |
| regex | Filtering | Filters results by regex pattern | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Regex) |
| relevancy | Analyzing | Calculates relevancy of events | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Relevancy) |
| reltime | Transforming | Converts timestamps to relative timeframes | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Reltime) |
| rename | Organizing | Renames fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Rename) |
| replace | Transforming | Replaces field values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Replace) |
| rest | Data Input | Retrieves data via REST API | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Rest) |
| return | Processing | Returns values from a search | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Return) |
| reverse | Organizing | Reverses the order of results | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Reverse) |
| rex | Extracting | Extracts fields with regex | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Rex) |
| rtorder | Organizing | Reorders real-time search results | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Rtorder) |
| savedsearch | Data Input | Runs a saved search | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Savedsearch) |
| script | Processing | Runs a script on search results | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Script) |
| scrub | Filtering | Replaces sensitive values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Scrub) |
| search | Searching | Filters results by search expression | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Search) |
| searchtxn | Analyzing | Groups events into transactions | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Searchtxn) |
| selfjoin | Combining | Joins results with themselves | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Selfjoin) |
| sendemail | Alerting | Sends email with results | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Sendemail) |
| set | Processing | Sets values in search context | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Set) |
| setfields | Transforming | Sets field values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Setfields) |
| sichart | Transforming | Creates statistical charts with split-by | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Sichart) |
| sirare | Reporting | Finds the least common field values with split-by | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Sirare) |
| sistats | Transforming | Calculates statistics with split-by | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Sistats) |
| sitimechart | Visualizing | Creates time-based statistical charts with split-by | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Sitimechart) |
| sitop | Reporting | Finds the most common field values with split-by | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Sitop) |
| sort | Organizing | Sorts results | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Sort) |
| spath | Extracting | Extracts fields from structured data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Spath) |
| stats | Transforming | Calculates statistics | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Stats) |
| strcat | Transforming | Concatenates string values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Strcat) |
| streamstats | Transforming | Calculates running statistics | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Streamstats) |
| table | Transforming | Creates a tabular view of results | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Table) |
| tags | Enriching | Adds tags to events | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Tags) |
| tail | Filtering | Returns the last N results | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Tail) |
| timechart | Visualizing | Creates time-based statistical charts | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Timechart) |
| timewrap | Transforming | Wraps results into multiple time periods | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Timewrap) |
| top | Reporting | Finds the most common field values | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Top) |
| transaction | Analyzing | Groups events into transactions | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Transaction) |
| transpose | Transforming | Transposes rows and columns | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Transpose) |
| trendline | Analyzing | Computes a trendline for timeseries data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Trendline) |
| tscollect | Data Management | Stores timeseries data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Tscollect) |
| tstats | Reporting | Returns statistical information from indexed fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Tstats) |
| typeahead | Reporting | Returns typeahead information | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Typeahead) |
| typelearner | Reporting | Generates field extraction rules | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Typelearner) |
| typer | Extracting | Applies field extraction rules | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Typer) |
| union | Combining | Combines results from searches | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Union) |
| uniq | Filtering | Removes duplicates from fields | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Uniq) |
| untable | Transforming | Converts tabular results to events | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Untable) |
| where | Filtering | Filters results by expression | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Where) |
| x11 | Analyzing | Performs X11 time series decomposition | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/X11) |
| xmlkv | Extracting | Extracts fields from XML data | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Xmlkv) |
| xmlunescape | Transforming | Unescapes XML entities | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Xmlunescape) |
| xpath | Extracting | Extracts fields from XML data using XPath | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Xpath) |
| xyseries | Transforming | Creates coordinates for scatter plots | [Splunk Docs](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Xyseries) |
