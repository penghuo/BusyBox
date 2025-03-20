import json
import csv
import re
import matplotlib.pyplot as plt
import numpy as np

def load_report_data(file_path):
    """Load JSON report and structure by query ID"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return {item['query_id']: item for item in data['results']}

def natural_sort_key(query_id):
    """Natural sort key for Query IDs (Q1, Q2, Q10 order)"""
    match = re.match(r"([A-Za-z]+)(\d+)", query_id)
    if match:
        return (match.group(1), int(match.group(2)))
    return (query_id, 0)

def format_latency(value):
    """Format latency to 2 decimal places or return N/A"""
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None

def generate_comparison(presto_json, spark_json, output_csv, chart_path):
    # Load both reports
    presto_data = load_report_data(presto_json)
    spark_data = load_report_data(spark_json)
    
    # Get sorted query IDs
    all_query_ids = sorted(
        set(presto_data.keys()).union(spark_data.keys()),
        key=natural_sort_key
    )
    
    # Prepare data for CSV and chart
    csv_rows = []
    chart_data = {
        'queries': [],
        'presto': [],
        'spark': []
    }
    
    for qid in all_query_ids:
        presto_time = format_latency(presto_data.get(qid, {}).get('max_time'))
        spark_time = format_latency(spark_data.get(qid, {}).get('max_time'))
        
        # CSV data
        csv_rows.append([
            qid,
            f"{presto_time:.2f}" if presto_time is not None else 'N/A',
            f"{spark_time:.2f}" if spark_time is not None else 'N/A'
        ])
        
        # Chart data
        chart_data['queries'].append(qid)
        chart_data['presto'].append(presto_time)
        chart_data['spark'].append(spark_time)
    
    # Generate CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['QueryID', 'PrestoLatency', 'SparkLatency'])
        writer.writerows(csv_rows)
    
    # Generate bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    index = np.arange(len(chart_data['queries']))
    bar_width = 0.35
    
    presto_bars = ax.bar(
        index - bar_width/2,
        [t if t else 0 for t in chart_data['presto']],
        bar_width,
        label='Presto',
        color='#1f77b4'
    )
    
    spark_bars = ax.bar(
        index + bar_width/2,
        [t if t else 0 for t in chart_data['spark']],
        bar_width,
        label='Spark',
        color='#ff7f0e'
    )
    
    # Add labels and formatting
    ax.set_xlabel('Query ID')
    ax.set_ylabel('Latency (seconds)')
    ax.set_title('Query Latency Comparison (Presto vs Spark)')
    ax.set_xticks(index)
    ax.set_xticklabels(chart_data['queries'], rotation=45, ha='right')
    ax.legend()
    
    # Add value labels
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{height:.2f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
    
    add_labels(presto_bars)
    add_labels(spark_bars)
    
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 5:
        print("Usage: python compare_reports.py <presto.json> <spark.json> <output.csv> <chart.png>")
        sys.exit(1)
    
    generate_comparison(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print(f"CSV report: {sys.argv[3]}")
    print(f"Chart saved: {sys.argv[4]}")