NOTE: If this is your first time configuring field extractions in
      props.conf, review the following information first. Additional
      information is also available in the Getting Data In Manual
      in the Splunk Documentation.

There are three different "field extraction types" that you can use to
configure field extractions: TRANSFORMS, REPORT, and EXTRACT. They differ in
two significant ways: 1) whether they create indexed fields (fields
extracted at index time) or extracted fields (fields extracted at search
time), and 2), whether they include a reference to an additional component
called a "field transform," which you define separately in transforms.conf.

**Field extraction configuration: index time versus search time**

Use the TRANSFORMS field extraction type to create index-time field
extractions. Use the REPORT or EXTRACT field extraction types to create
search-time field extractions.

NOTE: Index-time field extractions have performance implications.
      Create additions to the default set of indexed fields ONLY
      in specific circumstances. Whenever possible, extract
      fields only at search time.

There are times when you may find that you need to change or add to your set
of indexed fields. For example, you may have situations where certain
search-time field extractions are noticeably impacting search performance.
This can happen when the value of a search-time extracted field exists
outside of the field more often than not. For example, if you commonly
search a large event set with the expression company_id=1 but the value 1
occurs in many events that do *not* have company_id=1, you may want to add
company_id to the list of fields extracted by Splunk software at index time.
This is because at search time, Splunk software checks each
instance of the value 1 to see if it matches company_id, and that kind of
thing slows down performance when you have Splunk searching a large set of
data.

Conversely, if you commonly search a large event set with expressions like
company_id!=1 or NOT company_id=1, and the field company_id nearly *always*
takes on the value 1, you may want to add company_id to the list of fields
extracted by Splunk software at index time.

For more information about index-time field extraction, search the
documentation for "index-time extraction." For more information about
search-time field extraction, search the documentation for
"search-time extraction."

**Field extraction configuration: field transforms vs. "inline" (props.conf only) configs**

The TRANSFORMS and REPORT field extraction types reference an additional
component called a field transform, which you define separately in
transforms.conf. Field transforms contain a field-extracting regular
expression and other settings that govern the way that the transform
extracts fields. Field transforms are always created in conjunction with
field extraction stanzas in props.conf; they do not stand alone.

The EXTRACT field extraction type is considered to be "inline," which means
that it does not reference a field transform. It contains the regular
expression that Splunk software uses to extract fields at search time. You
can use EXTRACT to define a field extraction entirely within props.conf, no
transforms.conf component is required.

**Search-time field extractions: Why use REPORT if EXTRACT will do?**

This is a good question. And much of the time, EXTRACT is all you need for
search-time field extraction. But when you build search-time field
extractions, there are specific cases that require the use of REPORT and the
field transform that it references. Use REPORT if you want to:

* Reuse the same field-extracting regular expression across multiple
  sources, source types, or hosts. If you find yourself using the same regex
  to extract fields across several different sources, source types, and
  hosts, set it up as a transform, and then reference it in REPORT
  extractions in those stanzas. If you need to update the regex you only
  have to do it in one place. Handy!
* Apply more than one field-extracting regular expression to the same
  source, source type, or host. This can be necessary in cases where the
  field or fields that you want to extract from a particular source, source
  type, or host appear in two or more very different event patterns.
* Set up delimiter-based field extractions. Useful if your event data
  presents field-value pairs (or just field values) separated by delimiters
  such as commas, spaces, bars, and so on.
* Configure extractions for multivalued fields. You can have Splunk software
  append additional values to a field as it finds them in the event data.
* Extract fields with names beginning with numbers or underscores.
  Ordinarily, the key cleaning functionality removes leading numeric
  characters and underscores from field names. If you need to keep them,
  configure your field transform to turn key cleaning off.
* Manage formatting of extracted fields, in cases where you are extracting
  multiple fields, or are extracting both the field name and field value.

**Precedence rules for TRANSFORMS, REPORT, and EXTRACT field extraction types**

* For each field extraction, Splunk software takes the configuration from the
  highest precedence configuration stanza (see precedence rules at the
  beginning of this file).
* If a particular field extraction is specified for a source and a source
  type, the field extraction for source wins out.
* Similarly, if a particular field extraction is specified in ../local/ for
  a <spec>, it overrides that field extraction in ../default/.


TRANSFORMS-<class> = <transform_stanza_name>, <transform_stanza_name2>,...
* Used for creating indexed fields (index-time field extractions).
* <class> is a unique literal string that identifies the namespace of the
  field you're extracting.
  **Note:** <class> values do not have to follow field name syntax
  restrictions. You can use characters other than a-z, A-Z, and 0-9, and
  spaces are allowed. <class> values are not subject to key cleaning.
* <transform_stanza_name> is the name of your stanza from transforms.conf.
* Use a comma-separated list to apply multiple transform stanzas to a single
  TRANSFORMS extraction. Splunk software applies them in the list order. For
  example, this sequence ensures that the [yellow] transform stanza gets
  applied first, then [blue], and then [red]:
        [source::color_logs]
        TRANSFORMS-colorchange = yellow, blue, red
* See the RULESET-<class> setting for additional index-time transformation options.

RULESET-<class> = <string>
* This setting is used to perform index-time transformations, such as filtering, 
  routing, and masking.
* A <class> is a unique string that identifies the name of a ruleset.
* Supply one or more transform stanza names as values for this setting. A
  transform stanza name is the name of a stanza in the transforms.conf 
  file where you define your data transformations.
* Use a comma-separated list to apply multiple transform stanzas to a single
  RULESET extraction. Each transform stanza is applied in the order defined in the list.
* Use the REST endpoint: /services/data/ingest/rulesets to configure this setting.
* This setting is nearly identical to the TRANSFORMS-<class> setting, with the
  following exceptions:
  * If a RULESET is configured for a particular data stream on both indexers and
    heavy forwarders, the processor processes the RULESET on both Splunk platform
    instances. This is different from TRANSFORMS, which the processor ignores on an 
    indexer if it has already been processed on the heavy forwarder.
  * If a data source matches both a TRANSFORMS and a RULESET, the processor applies
    the TRANSFORMS setting before the RULESET setting.
* Default: empty string

RULESET_DESC-<class> = <string>
* Description of 'RULESET-' to help users understand what a specific
  'RULESET-' index-time field extraction does.
  For example:
  RULESET_DESC-drop_debug_logs = Describes the 'RULESET-drop_debug_logs' field transform.

REPORT-<class> = <transform_stanza_name>, <transform_stanza_name2>,...
* Used for creating extracted fields (search-time field extractions) that
  reference one or more transforms.conf stanzas.
* <class> is a unique literal string that identifies the namespace of the
  field you're extracting.
  NOTE: <class> values do not have to follow field name syntax
  restrictions. You can use characters other than a-z, A-Z, and 0-9, and
  spaces are allowed. <class> values are not subject to key cleaning.
* <transform_stanza_name> is the name of your stanza from transforms.conf.
* Use a comma-separated list to apply multiple transform stanzas to a single
  REPORT extraction.
  Splunk software applies them in the list order. For example, this sequence
  insures that the [yellow] transform stanza gets applied first, then [blue],
  and then [red]:
    [source::color_logs]
    REPORT-colorchange = yellow, blue, red

EXTRACT-<class> = [<regex>|<regex> in <src_field>]
* Used to create extracted fields (search-time field extractions) that do
  not reference transforms.conf stanzas.
* Performs a regex-based field extraction from the value of the source
  field.
* <class> is a unique literal string that identifies the namespace of the
  field you're extracting.
  NOTE: <class> values do not have to follow field name syntax
  restrictions. You can use characters other than a-z, A-Z, and 0-9, and
  spaces are allowed. <class> values are not subject to key cleaning.
* The <regex> is required to have named capturing groups. When the <regex>
  matches, the named capturing groups and their values are added to the
  event.
* dotall (?s) and multi-line (?m) modifiers are added in front of the regex.
  So internally, the regex becomes (?ms)<regex>.
* Use '<regex> in <src_field>' to match the regex against the values of a
  specific field.  Otherwise it just matches against _raw (all raw event
  data).
* NOTE: <src_field> has the following restrictions:
  * It can only contain alphanumeric characters and underscore
    (a-z, A-Z, 0-9, and _).
  * It must already exist as a field that has either been extracted at
    index time or has been derived from an EXTRACT-<class> configuration
    whose <class> ASCII value is *lower* than the configuration in which
    you are attempting to extract the field. For example, if you
    have an EXTRACT-ZZZ configuration that extracts <src_field>, then
    you can only use 'in <src_field>' in an EXTRACT configuration with
    a <class> of 'aaa' or higher, as 'aaa' is higher in ASCII value
    than 'ZZZ'.
  * It cannot be a field that has been derived from a transform field
    extraction (REPORT-<class>), an automatic key-value field extraction
    (in which you configure the KV_MODE setting to be something other
    than 'none'), a field alias, a calculated field, or a lookup,
    as these operations occur after inline field extractions (EXTRACT-
    <class>) in the search-time operations sequence.
* If your regex needs to end with 'in <string>' where <string> is *not* a
  field name, change the regex to end with '[i]n <string>' to ensure that
  Splunk software doesn't try to match <string> to a field name.

KV_MODE = [none|auto|auto_escaped|multi|multi:<multikv.conf_stanza_name>|json|xml]
* Used for search-time field extractions only.
* Specifies the field/value extraction mode for the data.
* Set KV_MODE to one of the following:
  * none - Disables field extraction for the host, source, or source type.
  * auto_escaped - Extracts fields/value pairs separated by equal signs and
                   honors \" and \\ as escaped sequences within quoted
                   values. For example: field="value with \"nested\" quotes"
  * multi - Invokes the 'multikv' search command, which extracts fields from 
            table-formatted events.
  * multi:<multikv.conf_stanza_name> - Invokes a custom multikv.conf 
    configuration to extract fields from a specific type of table-formatted 
    event. Use this option in situations where the default behavior of the 
    'multikv' search command is not meeting your needs.
  * xml - Automatically extracts fields from XML data.
  * json - Automatically extracts fields from JSON data.
* Setting to 'none' can ensure that one or more custom field extractions are not
  overridden by automatic field/value extraction for a particular host,
  source, or source type. You can also use 'none' to increase search 
  performance by disabling extraction for common but nonessential fields.
* The 'xml' and 'json' modes do not extract any fields when used on data
  that isn't of the correct format (JSON or XML).
* If you set 'KV_MODE = json' for a source type, do not also set 
  'INDEXED_EXTRACTIONS = JSON' for the same source type. This causes the Splunk 
  software to extract the json fields twice: once at index time and again at 
  search time.
* When KV_MODE is set to 'auto' or 'auto_escaped', automatic JSON field 
  extraction can take place alongside other automatic field/value extractions. 
  To disable JSON field extraction when 'KV_MODE' is set to 'auto' or 
  'auto_escaped', add 'AUTO_KV_JSON = false' to the stanza. 
* Default: auto

MATCH_LIMIT = <integer>
* Only set in props.conf for EXTRACT type field extractions.
  For REPORT and TRANSFORMS field extractions, set this in transforms.conf.
* Optional. Limits the amount of resources spent by PCRE
  when running patterns that do not match.
* Use this to set an upper bound on how many times PCRE calls an internal
  function, match(). If set too low, PCRE may fail to correctly match a pattern.
* Default: 100000

DEPTH_LIMIT = <integer>
* Only set in props.conf for EXTRACT type field extractions.
  For REPORT and TRANSFORMS field extractions, set this in transforms.conf.
* Optional. Limits the amount of resources spent by PCRE
  when running patterns that do not match.
* Use this to limit the depth of nested backtracking in an internal PCRE
  function, match(). If set too low, PCRE might fail to correctly
  match a pattern.
* Default: 1000

AUTO_KV_JSON = <boolean>
* Used only for search-time field extractions.
* Specifies whether to extract fields from JSON data when 'KV_MODE' is set to 
  'auto' or 'auto_escaped'. 
* To disable automatic extraction of fields from JSON data when 'KV_MODE' is 
  set to 'auto' or 'auto_escaped', set 'AUTO_KV_JSON = false'.  
* Setting 'AUTO_KV_JSON = false' when 'KV_MODE' is set to 'none', 'multi', 
  'json', or 'xml' has no effect.
* Default: true

KV_TRIM_SPACES = <boolean>
* Modifies the behavior of KV_MODE when set to auto, and auto_escaped.
* Traditionally, automatically identified fields have leading and trailing
  whitespace removed from their values.
  * Example event: 2014-04-04 10:10:45 myfield=" apples "
    would result in a field called 'myfield' with a value of 'apples'.
* If this value is set to false, then external whitespace then this outer
  space is retained.
  * Example: 2014-04-04 10:10:45 myfield=" apples "
    would result in a field called 'myfield' with a value of ' apples '.
* The trimming logic applies only to space characters, not tabs, or other
  whitespace.
* NOTE: Splunk Web currently has limitations with displaying and
  interactively clicking on fields that have leading or trailing
  whitespace. Field values with leading or trailing spaces may not look
  distinct in the event viewer, and clicking on a field value typically
  inserts the term into the search string without its embedded spaces.
  * The limitations are not specific to this feature. Any embedded spaces
    behave this way.
  * The Splunk search language and included commands respect the spaces.
* Default: true

CHECK_FOR_HEADER = <boolean>
* Used for index-time field extractions only.
* Set to true to enable header-based field extraction for a file.
* If the file has a list of columns and each event contains a field value
  (without field name), Splunk software picks a suitable header line to
  use for extracting field names.
* Can only be used on the basis of [<sourcetype>] or [source::<spec>],
  not [host::<spec>].
* Disabled when LEARN_SOURCETYPE = false.
* Causes the indexed source type to have an appended numeral; for
  example, sourcetype-2, sourcetype-3, and so on.
* The field names are stored in etc/apps/learned/local/props.conf.
  * Because of this, this feature does not work in most environments where
    the data is forwarded.
* This setting applies at input time, when data is first read by Splunk
  software, such as on a forwarder that has configured inputs acquiring the
  data.
* Default: false

SEDCMD-<class> = <sed script>
* Only used at index time.
* Commonly used to anonymize incoming data at index time, such as credit
  card or social security numbers. For more information, search the online
  documentation for "anonymize data."
* Used to specify a sed script which Splunk software applies to the _raw
  field.
* A sed script is a space-separated list of sed commands. Currently the
  following subset of sed commands is supported:
    * replace (s) and character substitution (y).
* Syntax:
    * replace - s/regex/replacement/flags
      * regex is a perl regular expression (optionally containing capturing
        groups).
      * replacement is a string to replace the regex match. Use \n for back
        references, where "n" is a single digit.
      * flags can be either: g to replace all matches, or a number to
        replace a specified match.
    * substitute - y/string1/string2/
      * substitutes the string1[i] with string2[i]
* No default.

FIELDALIAS-<class> = (<orig_field_name> AS|ASNEW <new_field_name>)+
* Use FIELDALIAS configurations to apply aliases to a field. This lets you
  search for the original field using one or more alias field names. For
  example, a search expression of <new_field_name>=<value> also
  finds events that match <orig_field_name>=<value>.
* <orig_field_name> is the original name of the field. It is not removed by
  this configuration.
* <new_field_name> is the alias to assign to the <orig_field_name>.
* You can create multiple aliases for the same field. For example, a single
  <orig_field_name> may have multiple <new_field_name>s as long as all of
  the <new_field_name>s are distinct.
  * Example of a valid configuration:
    FIELDALIAS-vendor = vendor_identifier AS vendor_id    \
                        vendor_identifier AS vendor_name
* You can include multiple field alias renames in the same stanza.
* Avoid applying the same alias field name to multiple original field
  names as a single alias cannot refer to multiple original source fields.
  Each alias can map to only one source field. If you attempt to create
  two field aliases that map two separate <orig_field_name>s onto the
  same <new_field_name>, only one of the aliases takes effect, not both.
  * For example, if you attempt to run the following configuration,
    which maps two <orig_field_name>s to the same <new_field_name>, only
    one of the aliases takes effect, not both. The following definition
    demonstrates an invalid configuration:
    FIELDALIAS-foo = userID AS user loginID AS user
  * If you must do this, set it up as a calculated field (an EVAL-* statement)
    that uses the 'coalesce' function to create a new field that takes the
    value of one or more existing fields. This method lets you be explicit
    about ordering of input field values in the case of NULL fields. For
    example: EVAL-ip = coalesce(clientip,ipaddress)
* The following is true if you use AS in this configuration:
  * If the alias field name <new_field_name> already exists, the Splunk
    software replaces its value with the value of <orig_field_name>.
  * If the <orig_field_name> field has no value or does not exist, the
    <new_field_name> is removed.
* The following is true if you use ASNEW in this configuration:
  * If the alias field name <new_field_name> already exists, the Splunk
    software does not change it.
  * If the <orig_field_name> field has no value or does not exist, the
    <new_field_name> is kept.
* Field aliasing is performed at search time, after field extraction, but
  before calculated fields (EVAL-* statements) and lookups.
  This means that:
  * Any field extracted at search time can be aliased.
  * You can specify a lookup based on a field alias.
  * You cannot alias a calculated field.
* No default.

EVAL-<fieldname> = <eval statement>
* Use this to automatically run the <eval statement> and assign the value of
  the output to <fieldname>. This creates a "calculated field."
* When multiple EVAL-* statements are specified, they behave as if they are
* run in parallel, rather than in any particular sequence.
  For example say you have two statements: EVAL-x = y*2 and EVAL-y=100. In
  this case, "x" is assigned the original value of "y * 2," not the
  value of "y" after it is set to 100.
* Splunk software processes calculated fields after field extraction and
  field aliasing but before lookups. This means that:
  * You can use a field alias in the eval statement for a calculated
    field.
  * You cannot use a field added through a lookup in an eval statement for a
    calculated field.
* No default.

LOOKUP-<class> = $TRANSFORM (<match_field> (AS <match_field_in_event>)?)+ (OUTPUT|OUTPUTNEW (<output_field> (AS <output_field_in_event>)? )+ )?
* At search time, identifies a specific lookup table and describes how that
  lookup table should be applied to events.
* <match_field> specifies a field in the lookup table to match on.
  * By default Splunk software looks for a field with that same name in the
    event to match with (if <match_field_in_event> is not provided)
  * You must provide at least one match field. Multiple match fields are
    allowed.
* <output_field> specifies a field in the lookup entry to copy into each
  matching event in the field <output_field_in_event>.
  * If you do not specify an <output_field_in_event> value, Splunk software
    uses <output_field>.
  * A list of output fields is not required.
* If they are not provided, all fields in the lookup table except for the
  match fields (and the timestamp field if it is specified) are output
  for each matching event.
* If the output field list starts with the keyword "OUTPUTNEW" instead of
  "OUTPUT", then each output field is only written out if it did not previous
  exist. Otherwise, the output fields are always overridden. Any event that
  has all of the <match_field> values but no matching entry in the lookup
  table clears all of the output fields.  NOTE that OUTPUTNEW behavior has
  changed since 4.1.x (where *none* of the output fields were written to if
  *any* of the output fields previously existed).
* Splunk software processes lookups after it processes field extractions,
  field aliases, and calculated fields (EVAL-* statements). This means that you
  can use extracted fields, aliased fields, and calculated fields to specify
  lookups. But you can't use fields discovered by lookups in the
  configurations of extracted fields, aliased fields, or calculated fields.
* The LOOKUP- prefix is actually case-insensitive. Acceptable variants include:
   LOOKUP_<class> = [...]
   LOOKUP<class>  = [...]
   lookup_<class> = [...]
   lookup<class>  = [...]
* No default.