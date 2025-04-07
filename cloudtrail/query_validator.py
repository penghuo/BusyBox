#!/usr/bin/env python3
"""
Improved Presto to Spark SQL Validator with Custom Rules

This script:
1. Reads table creation SQL from a JSON file and creates the table
2. Reads Presto SQL queries from a JSON file
3. Uses either SQLGlot or custom rules to translate Presto SQL to Spark SQL
4. Executes both original Presto SQL and translated Spark SQL in Spark
5. Generates a simplified HTML report showing results

Usage:
    python query_validator.py <queries_json_file> <table_file> <table_name> [--output-dir <dir>] [--use-sqlglot]

Example:
    python query_validator.py queries.json table_create.json ct_eds --output-dir ./results --use-sqlglot

Requirements:
- PySpark
- sqlglot (optional, only if --use-sqlglot is specified)
- pandas
"""

import os
import sys
import re
import json
import logging
import argparse
import pandas as pd
import difflib
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException, ParseException

# Configure logging
def setup_logging(output_dir):
    """Set up logging configuration"""
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def initialize_spark():
    """Initialize a local Spark session for SQL execution"""
    print("Initializing Spark session...")
    
    spark = SparkSession.builder \
        .appName("PrestoToSparkValidator") \
        .master("local[*]") \
        .config("spark.sql.session.timeZone", "UTC") \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .config("spark.sql.ansi.enabled", "false") \
        .getOrCreate()
    
    # Log the Spark version
    print(f"Using Spark version: {spark.version}")
    
    return spark, spark.version

def load_create_table_sql(file_path, logger):
    """Load the CREATE TABLE SQL from a JSON file"""
    if not os.path.exists(file_path):
        logger.error(f"Table file not found: {file_path}")
        sys.exit(1)
    
    logger.info(f"Loading table creation SQL from {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if 'sql' not in data:
            logger.error("Missing 'sql' field in table file")
            sys.exit(1)
        
        return data['sql']
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing table file JSON: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading table SQL: {str(e)}")
        sys.exit(1)

def create_table(spark, create_sql, table_name, logger):
    """Create the table using the provided SQL"""
    try:
        # Replace table name placeholder
        create_sql = create_sql.replace('$EDS_ID', table_name)
        
        # Drop table if it exists
        logger.info(f"Creating table '{table_name}'")
        spark.sql(f"DROP TABLE IF EXISTS {table_name}")
        
        # Execute the CREATE TABLE statement
        spark.sql(create_sql)
        logger.info(f"Successfully created table '{table_name}'")
        
        return True
    except Exception as e:
        logger.error(f"Failed to create table: {str(e)}")
        return False

def read_queries_from_json(file_path, table_name, logger):
    """Read SQL queries from the specified JSON file and replace placeholders"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    logger.info(f"Reading queries from {file_path}")
    
    # Read JSON file
    try:
        with open(file_path, 'r') as f:
            queries_data = json.load(f)
        
        # Process each query - replace $EDS_ID with actual table name
        processed_queries = []
        for i, item in enumerate(queries_data, 1):
            if isinstance(item, dict) and 'sql' in item:
                query = item['sql'].replace('$EDS_ID', table_name)
                processed_queries.append({
                    'query_id': i,
                    'original_sql': item['sql'],
                    'presto_sql': query,
                    'name': item.get('name', f'Query {i}'),
                    'description': item.get('description', '')
                })
        
        logger.info(f"Found {len(processed_queries)} queries to validate")
        return processed_queries
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON file: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading queries: {str(e)}")
        sys.exit(1)

def translate_with_custom_rules(query, logger):
    """
    Translate Presto SQL to Spark SQL using custom translation rules
    Focusing on date functions and other common Presto->Spark differences
    """
    # Initialize translated query with the original
    translated = query

    # Rule 6: Convert CROSS JOIN UNNEST with JSON parsing to LATERAL VIEW explode
    cross_join_pattern = re.compile(
        r'CROSS\s+JOIN\s+UNNEST\s*\(\s*map_values\s*\(\s*cast\s*\(\s*json_parse\s*\(\s*element_at\s*\(([^,]+),\s*[\'"]expressionAttributeNames[\'"]\s*\)\s*\)\s*as\s+map\s*\(\s*varchar\s*,\s*varchar\s*\)\s*\)\s*\)\s*\)\s+as\s+t\s*\(\s*scanfields\s*\)',
        re.IGNORECASE
    )
    def replace_cross_join(match):
        map_source = match.group(1).strip()  # Extract the map source (e.g., requestParameters)
        return (
            f"LATERAL VIEW explode(map_values(from_json({map_source}['expressionAttributeNames'], 'map<string, string>'))) t AS scanfields"
        )
    translated = cross_join_pattern.sub(replace_cross_join, translated)

    cross_join_pattern = re.compile(
        r'CROSS\s+JOIN\s+UNNEST\s*\(\s*map_values\s*\(\s*cast\s*\(\s*json_parse\s*\(\s*element_at\s*\(([^,]+),\s*[\'"]expressionAttributeNames[\'"]\s*\)\s*\)\s*as\s+map\s*\(\s*varchar\s*,\s*varchar\s*\)\s*\)\s*\)\s*\)\s+as\s+t\s*\(\s*queryfields\s*\)',
        re.IGNORECASE
    )
    def replace_cross_join(match):
        map_source = match.group(1).strip()  # Extract the map source (e.g., requestParameters)
        return (
            f"LATERAL VIEW explode(map_values(from_json({map_source}['expressionAttributeNames'], 'map<string, string>'))) t AS queryfields"
        )
    translated = cross_join_pattern.sub(replace_cross_join, translated)

    cross_unnest_pattern = re.compile(
        r'CROSS\s+JOIN\s+UNNEST\s*\(\s*cast\s*\(\s*json_extract\s*\(\s*json_parse\s*\(\s*element_at\s*\(\s*([^,]+)\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)\s*\)\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)\s*as\s+array\s*\(\s*varchar\s*\)\s*\)\s*\)\s+as\s+t\s*\(\s*([^,]+)\s*\)',
        re.IGNORECASE
    )
    def replace_cross_unnest(match):
        map_var = match.group(1).strip()  # e.g., responseElements
        map_key = match.group(2)          # e.g., 'instancesSet'
        json_path = match.group(3)        # e.g., '$.items[*].instanceId'
        table = match.group(4)
        return (
            f"LATERAL VIEW explode("
            f"from_json("
            f"get_json_object({map_var}['{map_key}'], '{json_path}'), "
            f"'array<string>'"
            f")) t AS {table}"
        )    
    translated = cross_unnest_pattern.sub(replace_cross_unnest, translated)

    cross_unnest_pattern = re.compile(
        r'CROSS\s+JOIN\s+UNNEST\s*\(\s*cast\s*\(\s*json_extract\s*\(\s*element_at\s*\(\s*([^,]+)\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)\s*as\s+array\s*\(\s*varchar\s*\)\s*\)\s*\)\s+t\s*\(\s*([^,]+)\s*\)',
        re.IGNORECASE
    )
    def replace_cross_unnest(match):
        map_var = match.group(1).strip()  # e.g., responseElements
        map_key = match.group(2)          # e.g., 'instancesSet'
        json_path = match.group(3)        # e.g., '$.items[*].instanceId'
        table = match.group(4)
        return (
            f"LATERAL VIEW explode("
            f"from_json("
            f"get_json_object({map_var}['{map_key}'], '{json_path}'), "
            f"'array<string>'"
            f")) t AS {table}"
        )    
    translated = cross_unnest_pattern.sub(replace_cross_unnest, translated)    

    cross_unnest_pattern = re.compile(
        r'CROSS\s+JOIN\s+UNNEST\s*\(\s*cast\s*\(\s*json_extract\s*\(\s*element_at\s*\(\s*([^,]+)\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)\s*as\s+array\s*\(\s*varchar\s*\)\s*\)\s*\)\s+as\s+t\s*\(\s*([^,]+)\s*\)',
        re.IGNORECASE
    )
    def replace_cross_unnest(match):
        map_var = match.group(1).strip()  # e.g., responseElements
        map_key = match.group(2)          # e.g., 'instancesSet'
        json_path = match.group(3)        # e.g., '$.items[*].instanceId'
        table = match.group(4)
        return (
            f"LATERAL VIEW explode("
            f"from_json("
            f"get_json_object({map_var}['{map_key}'], '{json_path}'), "
            f"'array<string>'"
            f")) t AS {table}"
        )    
    translated = cross_unnest_pattern.sub(replace_cross_unnest, translated)
    
    # Rule 1: DATE_DIFF function - convert quoted time unit to literal
    # Example: DATE_DIFF('millisecond', eventTime, now()) → DATE_DIFF(MILLISECOND, eventTime, now())
    date_diff_pattern = r"DATE_DIFF\s*\(\s*'([^']+)'\s*,\s*([^,]+),\s*([^)]+)\s*\)"
    date_diff_repl = lambda m: f"DATE_DIFF({m.group(1).upper()}, {m.group(2)}, {m.group(3)})"
    translated = re.sub(date_diff_pattern, date_diff_repl, translated)
    
    # Rule 2: DATE_ADD function - convert quoted time unit to literal
    # Example: DATE_ADD('week', -7, timestamp) → DATE_ADD(WEEK, -7, timestamp)
    date_add_pattern = r"DATE_ADD\s*\(\s*'([^']+)'\s*,\s*([^,]+),\s*([^)]+)\s*\)"
    date_add_repl = lambda m: f"DATE_ADD({m.group(1).upper()}, {m.group(2)}, {m.group(3)})"
    translated = re.sub(date_add_pattern, date_add_repl, translated)


    # New Rule 0: Convert json_extract(json_parse(element_at())) to get_json_object(element_at())
    json_extract_pattern = re.compile(
        r'json_extract\s*\(\s*json_parse\s*\(\s*element_at\s*\(\s*([^,]+)\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)\s*\)\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)',
        re.IGNORECASE
    )
    
    def replace_json_extract(match):
        map_var = match.group(1).strip()
        map_key = match.group(2)
        json_path = match.group(3)
        return f"get_json_object(element_at({map_var}, '{map_key}'), '{json_path}')"
    
    translated = json_extract_pattern.sub(replace_json_extract, translated)
    
    # # Existing Rule 1: Convert element_at to map access (now converts remaining element_at)
    # translated = re.sub(
    #     r"element_at\s*\(\s*([^,]+)\s*,\s*['\"]([^'\"]+)['\"]\s*\)",
    #     r"\1['\2']",
    #     translated,
    #     flags=re.IGNORECASE
    # )

    # Rule 3: json_extract to get_json_object conversion
    # Simple replacement of function name
    json_extract_pattern = r"json_extract\s*\("
    json_extract_repl = "get_json_object("
    translated = re.sub(json_extract_pattern, json_extract_repl, translated, flags=re.IGNORECASE)

    
    # # Existing Rule 1: Convert element_at to map access
    # translated = re.sub(
    #     r"element_at\s*\(\s*([^,]+)\s*,\s*['\"]([^'\"]+)['\"]\s*\)",
    #     r"\1['\2']",
    #     translated,
    #     flags=re.IGNORECASE
    # )    

    # Rule 4: Convert VARCHAR to STRING in various contexts
    # Handle both CAST and type definitions
    varchar_patterns = [
        # Convert 'AS VARCHAR' in CAST expressions
        (r'\bAS\s+VARCHAR\b', 'AS STRING', re.IGNORECASE),
        # Convert map(varchar, varchar) type definitions
        (r'\bmap\s*\(\s*varchar\s*,\s*varchar\s*\)', 'map<string, string>', re.IGNORECASE)
    ]
    
    # Apply all conversions
    for pattern, replacement, flags in varchar_patterns:
        translated = re.sub(pattern, replacement, translated, flags=flags)
    
    # Log changes if any were made
    if translated != query:
        logger.info("Applied custom translation rules")
        logger.debug(f"Original: {query}")
        logger.debug(f"Translated: {translated}")
    
    return translated

def translate_with_sqlglot(query, logger):
    """Translate Presto SQL to Spark SQL using SQLGlot"""
    try:
        # Import sqlglot here to make it optional
        import sqlglot
        from sqlglot.errors import ErrorLevel
        
        # Use SQLGlot to translate from Presto to Spark
        translated = sqlglot.transpile(
            query, 
            read="presto", 
            write="spark",
            # Let's not raise errors but collect all warnings
            unsupported_level=ErrorLevel.WARN
        )
        
        if translated and len(translated) > 0:
            return translated[0]
        else:
            logger.warning(f"SQLGlot translation returned empty result for: {query}")
            return query
    except ImportError:
        logger.error("SQLGlot is not installed. Please install it using: pip install sqlglot")
        return query
    except Exception as e:
        logger.error(f"SQLGlot translation error: {str(e)}")
        return query

def generate_diff_html(presto_sql, spark_sql):
    """Generate HTML that highlights only the specific differences between presto_sql and spark_sql"""
    # Split both SQL strings into tokens (words, symbols, etc.)
    import re
    
    def tokenize(sql):
        # Pattern to split on whitespace, parentheses, commas, operators, etc., 
        # but keep the delimiters as separate tokens
        pattern = r'(\s+|[,().]|\b)'
        tokens = []
        # Split the string into tokens but preserve the delimiters
        parts = re.split(pattern, sql)
        # Filter out empty strings and join whitespace with adjacent tokens
        for part in parts:
            if part.strip():  # Not just whitespace
                tokens.append(part)
            elif part:  # Is whitespace
                if tokens:
                    tokens[-1] = tokens[-1] + part
                else:
                    tokens.append(part)
        return tokens
    
    # Get tokens for both strings
    presto_tokens = tokenize(presto_sql)
    spark_tokens = tokenize(spark_sql)
    
    # Use difflib to find differences at the token level
    matcher = difflib.SequenceMatcher(None, presto_tokens, spark_tokens)
    
    # Create the HTML with highlighted differences
    html = ['<div class="diff">']
    html.append('<div class="diff-section"><h4>Highlighted Changes:</h4>')
    html.append('<div class="diff-line">')
    
    # Process the differences
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == 'equal':
            # Join the unchanged tokens
            html.append('<span class="unchanged">')
            html.append(''.join(presto_tokens[i1:i2]))
            html.append('</span>')
        elif op == 'replace':
            # Show the replaced tokens
            html.append('<span class="diff-removed">')
            html.append(''.join(presto_tokens[i1:i2]))
            html.append('</span>')
            html.append('<span class="diff-added">')
            html.append(''.join(spark_tokens[j1:j2]))
            html.append('</span>')
        elif op == 'delete':
            # Show deleted tokens
            html.append('<span class="diff-removed">')
            html.append(''.join(presto_tokens[i1:i2]))
            html.append('</span>')
        elif op == 'insert':
            # Show inserted tokens
            html.append('<span class="diff-added">')
            html.append(''.join(spark_tokens[j1:j2]))
            html.append('</span>')
    
    html.append('</div>')  # Close diff-line
    
    # Add the full queries below for reference
    html.append('<div class="full-queries">')
    html.append('<h4>Original Presto SQL:</h4>')
    html.append(f'<pre>{presto_sql}</pre>')
    html.append('<h4>Translated Spark SQL:</h4>')
    html.append(f'<pre>{spark_sql}</pre>')
    html.append('</div>')
    
    html.append('</div>')  # Close diff
    
    return '\n'.join(html)

def execute_query(spark, query_item, use_sqlglot, logger):
    """Execute both Presto and Spark SQL versions of a query and compare results"""
    presto_query = query_item['presto_sql']
    query_id = query_item['query_id']
    
    # First, translate the Presto SQL to Spark SQL using the specified method
    if use_sqlglot:
        spark_query = translate_with_sqlglot(presto_query, logger)
    else:
        spark_query = translate_with_custom_rules(presto_query, logger)
    
    query_item['spark_sql'] = spark_query
    
    if not presto_query.strip():
        return {
            'query_id': query_id,
            'name': query_item.get('name', f'Query {query_id}'),
            'presto_sql': presto_query,
            'spark_sql': spark_query,
            'presto_success': False,
            'spark_success': False,
            'presto_error': "Empty query",
            'spark_error': "Empty query",
            'execution_time_ms': 0,
            'diff_html': ''
        }
    
    logger.info(f"Executing query {query_id}: {presto_query[:80]}{'...' if len(presto_query) > 80 else ''}")
    logger.info(f"Translated to: {spark_query[:80]}{'...' if len(spark_query) > 80 else ''}")
    
    # Execute the original Presto SQL (as is) in Spark
    presto_start_time = datetime.now()
    presto_success = False
    presto_error = None
    
    try:
        # Spark will attempt to run the Presto SQL as is
        spark.sql(presto_query)
        presto_success = True
    except Exception as e:
        presto_error = str(e)
    
    presto_execution_time = (datetime.now() - presto_start_time).total_seconds() * 1000
    
    # Execute the translated Spark SQL
    spark_start_time = datetime.now()
    spark_success = False
    spark_error = None
    
    try:
        # Execute the translated Spark SQL
        spark.sql(spark_query)
        spark_success = True
    except Exception as e:
        spark_error = str(e)
    
    spark_execution_time = (datetime.now() - spark_start_time).total_seconds() * 1000
    
    # Generate diff HTML
    diff_html = generate_diff_html(presto_query, spark_query)
    
    # Determine error message to display
    error_message = ""
    if not presto_success:
        error_message += f"Presto Error: {presto_error}\n"
    if not spark_success:
        error_message += f"Spark Error: {spark_error}\n"
    
    # Log the results
    if presto_success:
        logger.info(f"Presto query {query_id} executed successfully in {presto_execution_time:.2f} ms")
    else:
        logger.error(f"Presto query {query_id} failed: {presto_error}")
        
    if spark_success:
        logger.info(f"Spark query {query_id} executed successfully in {spark_execution_time:.2f} ms")
    else:
        logger.error(f"Spark query {query_id} failed: {spark_error}")
    
    return {
        'query_id': query_id,
        'name': query_item.get('name', f'Query {query_id}'),
        'presto_sql': presto_query,
        'spark_sql': spark_query,
        'presto_success': presto_success,
        'spark_success': spark_success,
        'presto_error': presto_error,
        'spark_error': spark_error,
        'error_message': error_message.strip(),
        'presto_execution_time_ms': presto_execution_time,
        'spark_execution_time_ms': spark_execution_time,
        'diff_html': diff_html
    }

def generate_html_report(results, output_file, spark_version, table_name, use_sqlglot):
    """Generate simplified HTML report"""
    presto_success = len([r for r in results if r['presto_success']])
    spark_success = len([r for r in results if r['spark_success']])
    total = len(results)
    
    # Generate simplified HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Presto to Spark SQL Report</title>
    <style>
        body {{ font-family: Arial; margin: 20px; }}
        .header {{ background-color: #4a86e8; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
        .summary {{ margin-bottom: 20px; }}
        .progress-bar {{ width: 100%; background-color: #f3f3f3; height: 30px; border-radius: 5px; margin-bottom: 20px; }}
        .progress {{ height: 100%; background-color: #4CAF50; text-align: center; line-height: 30px; color: white; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
        th {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .query {{ max-width: 400px; overflow-x: auto; }}
        .actions {{ white-space: nowrap; }}
        .filter-bar {{ margin-bottom: 15px; }}
        .tabs {{ display: flex; }}
        .tab {{ padding: 5px 10px; cursor: pointer; border: 1px solid #ccc; }}
        .tab.active {{ background-color: #4a86e8; color: white; }}
        .improved {{ background-color: #d4edda; }}
        pre {{ margin: 0; white-space: pre-wrap; }}
        .hidden {{ display: none; }}
        input[type=text] {{ padding: 5px; width: 30%; }}
        button {{ padding: 5px 10px; margin-right: 5px; cursor: pointer; }}
        
        /* Diff styling */
        .diff {{
            font-family: monospace;
            border: 1px solid #ccc;
            padding: 10px;
            margin-top: 10px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .diff-section {{ margin-bottom: 15px; }}
        .diff-line {{ white-space: pre-wrap; font-size: 14px; line-height: 1.5; }}
        .diff-removed {{ background-color: #ffdddd; color: #994444; }}
        .diff-added {{ background-color: #ddffdd; color: #449944; }}
        .unchanged {{ color: #666; }}
        .full-queries {{ margin-top: 15px; border-top: 1px solid #eee; padding-top: 10px; }}
        .error-message {{ white-space: pre-wrap; color: #d9534f; }}
    </style>
    <script>
        function toggleQuery(id) {{
            const elem = document.getElementById('query-'+id);
            elem.classList.toggle('hidden');
        }}
        
        function filterStatus(status) {{
            const rows = document.querySelectorAll('#resultsTable tr[data-id]');
            rows.forEach(row => {{
                if (status === 'all' || 
                    (status === 'success' && row.getAttribute('data-spark') === 'true') ||
                    (status === 'failed' && row.getAttribute('data-spark') === 'false') ||
                    (status === 'improved' && row.getAttribute('data-presto') === 'false' && row.getAttribute('data-spark') === 'true')) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
            
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById('tab-'+status).classList.add('active');
        }}
        
        function filterText() {{
            const filter = document.getElementById('filterInput').value.toLowerCase();
            const rows = document.querySelectorAll('#resultsTable tr[data-id]');
            
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                if (text.includes(filter)) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}
    </script>
</head>
<body>
    <div class="header">
        <h1>Presto to Spark SQL Compatibility Report</h1>
        <p>Table: {table_name} | Spark: {spark_version} | Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p>Translation Method: {'SQLGlot' if use_sqlglot else 'Custom Rules'}</p>
    </div>
    
    <div class="summary">
        <p>Total queries: <b>{total}</b></p>
        <p>Presto success: <b>{presto_success}</b> ({presto_success/total*100:.1f}%)</p>
        <p>Spark success: <b>{spark_success}</b> ({spark_success/total*100:.1f}%)</p>
        <p>Improvement from translation: <b>{spark_success - presto_success}</b> queries</p>
        
        <div class="progress-bar">
            <div class="progress" style="width: {spark_success/total*100:.1f}%;">
                {spark_success/total*100:.1f}%
            </div>
        </div>
    </div>
    
    <div class="filter-bar">
        <div class="tabs">
            <div id="tab-all" class="tab active" onclick="filterStatus('all')">All Queries</div>
            <div id="tab-success" class="tab" onclick="filterStatus('success')">Successful</div>
            <div id="tab-failed" class="tab" onclick="filterStatus('failed')">Failed</div>
            <div id="tab-improved" class="tab" onclick="filterStatus('improved')">Improved</div>
        </div>
        <div style="margin-top: 10px;">
            <input type="text" id="filterInput" onkeyup="filterText()" placeholder="Search...">
        </div>
    </div>
    
    <table id="resultsTable">
        <tr>
            <th>#</th>
            <th>Name</th>
            <th>Presto</th>
            <th>Spark</th>
            <th>Presto Error</th>
            <th>Spark Error</th>
            <th>Details</th>
        </tr>
    """
    
    # Add rows
    for result in results:
        presto_status = "Success" if result['presto_success'] else "Failed"
        spark_status = "Success" if result['spark_success'] else "Failed"
        presto_class = "success" if result['presto_success'] else "error"
        spark_class = "success" if result['spark_success'] else "error"
        improved = not result['presto_success'] and result['spark_success']
        row_class = "improved" if improved else ""
        
        presto_error = result.get('presto_error', '') if not result['presto_success'] else ''
        spark_error = result.get('spark_error', '') if not result['spark_success'] else ''
        
        html += f"""
        <tr data-id="{result['query_id']}" data-presto="{str(result['presto_success']).lower()}" data-spark="{str(result['spark_success']).lower()}" class="{row_class}">
            <td>{result['query_id']}</td>
            <td>{result['name']}</td>
            <td class="{presto_class}">{presto_status}</td>
            <td class="{spark_class}">{spark_status}</td>
            <td class="error-message">{presto_error[:150]}{"..." if presto_error and len(presto_error) > 150 else ""}</td>
            <td class="error-message">{spark_error[:150]}{"..." if spark_error and len(spark_error) > 150 else ""}</td>
            <td class="actions">
                <button onclick="toggleQuery({result['query_id']})">Show/Hide</button>
            </td>
        </tr>
        <tr id="query-{result['query_id']}" class="hidden">
            <td colspan="6">
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <div>
                        <h4>Presto SQL:</h4>
                        <pre>{result['presto_sql']}</pre>
                    </div>
                    <div>
                        <h4>Spark SQL:</h4>
                        <pre>{result['spark_sql']}</pre>
                    </div>
                    <div>
                        <h4>Differences:</h4>
                        {result['diff_html']}
                    </div>
                </div>
            </td>
        </tr>
        """
    
    html += """
    </table>
</body>
</html>
    """
    
    # Write HTML to file
    with open(output_file, 'w') as f:
        f.write(html)

def export_reports(results, output_dir, spark_version, table_name, use_sqlglot):
    """Export validation results to various report formats"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Simplified results for CSV export
    simple_results = []
    for r in results:
        simple_results.append({
            'query_id': r['query_id'],
            'name': r['name'],
            'presto_success': r['presto_success'],
            'spark_success': r['spark_success'],
            'improvement': not r['presto_success'] and r['spark_success'],
            'presto_error': r['presto_error'],
            'spark_error': r['spark_error'],
            'presto_execution_time_ms': r['presto_execution_time_ms'],
            'spark_execution_time_ms': r['spark_execution_time_ms']
        })
    
    # Save to CSV
    df_results = pd.DataFrame(simple_results)
    csv_file = os.path.join(output_dir, f"results_{timestamp}.csv")
    df_results.to_csv(csv_file, index=False)
    
    # Generate HTML report
    html_report = os.path.join(output_dir, f"report_{timestamp}.html")
    generate_html_report(results, html_report, spark_version, table_name, use_sqlglot)
    
    # Create summary stats
    presto_success = len([r for r in results if r['presto_success']])
    spark_success = len([r for r in results if r['spark_success']])
    total = len(results)
    
    return html_report, csv_file, {
        'total': total,
        'presto_success': presto_success,
        'spark_success': spark_success,
        'improvement': spark_success - presto_success
    }

def validate_queries(queries_file, table_file, table_name, output_dir, use_sqlglot):
    """Main function to validate queries and generate reports"""
    # Set up logging
    logger = setup_logging(output_dir)
    
    # Initialize Spark
    spark, spark_version = initialize_spark()
    
    # Load and execute table creation SQL
    create_sql = load_create_table_sql(table_file, logger)
    if not create_table(spark, create_sql, table_name, logger):
        logger.error("Failed to create table, exiting")
        sys.exit(1)
    
    # Read and process queries
    queries = read_queries_from_json(queries_file, table_name, logger)
    
    # Execute queries and collect results
    results = []
    for query in queries:
        result = execute_query(spark, query, use_sqlglot, logger)
        results.append(result)
    
    # Export reports
    html_report, csv_file, summary = export_reports(results, output_dir, spark_version, table_name, use_sqlglot)
    
    # Log summary
    logger.info("=" * 50)
    logger.info(f"Validation complete:")
    logger.info(f"Total queries: {summary['total']}")
    logger.info(f"Presto SQL successful: {summary['presto_success']}/{summary['total']} ({summary['presto_success']/summary['total']*100:.1f}%)")
    logger.info(f"Spark SQL successful: {summary['spark_success']}/{summary['total']} ({summary['spark_success']/summary['total']*100:.1f}%)")
    logger.info(f"Improvement from translation: {summary['improvement']} queries")
    logger.info(f"HTML report: {html_report}")
    logger.info(f"CSV results: {csv_file}")
    
    # Stop Spark session
    spark.stop()
    logger.info("Spark session stopped")
    
    # Print summary to console
    print("\n" + "=" * 50)
    print(f"Validation complete!")
    print(f"Total queries: {summary['total']}")
    print(f"Presto SQL successful: {summary['presto_success']}/{summary['total']} ({summary['presto_success']/summary['total']*100:.1f}%)")
    print(f"Spark SQL successful: {summary['spark_success']}/{summary['total']} ({summary['spark_success']/summary['total']*100:.1f}%)")
    print(f"Improvement from translation: {summary['improvement']} queries")
    print(f"Reports saved to: {output_dir}")
    print(f"HTML report: {html_report}")
    
    # Try to open the HTML report
    try:
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(html_report)}")
        print(f"Opening HTML report in browser...")
    except Exception:
        print(f"Please open the HTML report manually: {html_report}")
    
    print("=" * 50)
    
    return results, summary

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(description='Validate Presto SQL queries against Spark SQL with translation')
    parser.add_argument('queries_file', help='JSON file containing Presto SQL queries')
    parser.add_argument('table_file', help='JSON file containing table creation SQL')
    parser.add_argument('table_name', help='Table name to replace $EDS_ID in queries and table creation SQL')
    parser.add_argument('--output-dir', '-o', default='./results', help='Output directory for reports (default: ./results)')
    parser.add_argument('--use-sqlglot', action='store_true', help='Use SQLGlot for translation instead of custom rules')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.queries_file):
        print(f"Error: Queries file not found: {args.queries_file}")
        sys.exit(1)
    
    if not os.path.exists(args.table_file):
        print(f"Error: Table file not found: {args.table_file}")
        sys.exit(1)
    
    # Run validation
    results, summary = validate_queries(
        args.queries_file, 
        args.table_file, 
        args.table_name, 
        args.output_dir,
        args.use_sqlglot
    )

if __name__ == "__main__":
    main()