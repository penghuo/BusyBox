#!/usr/bin/env python3
"""
Performance Report Generator for OpenSearch Star-tree Optimization

This script generates detailed performance reports from benchmark results,
including tables, charts, and analysis of the performance improvements.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import csv

# Default configuration
DEFAULT_RESULTS_FILE = "benchmark_results.json"
DEFAULT_OUTPUT_DIR = "reports"
DEFAULT_REPORT_NAME = "star_tree_performance_report"

class PerformanceReportGenerator:
    """Generates performance reports from benchmark results."""
    
    def __init__(self, results_file, output_dir, report_name):
        """Initialize the report generator with file paths."""
        self.results_file = results_file
        self.output_dir = output_dir
        self.report_name = report_name
        self.results = None
    
    def load_results(self):
        """Load benchmark results from file."""
        print(f"Loading benchmark results from {self.results_file}...")
        try:
            with open(self.results_file, 'r') as f:
                self.results = json.load(f)
            print(f"✓ Results loaded successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to load results: {e}")
            return False
    
    def create_output_directory(self):
        """Create output directory if it doesn't exist."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"✓ Output directory ready: {self.output_dir}")
            return True
        except Exception as e:
            print(f"✗ Failed to create output directory: {e}")
            return False
    
    def generate_csv_report(self):
        """Generate CSV report with benchmark results."""
        if not self.results:
            print("✗ No results loaded")
            return False
        
        csv_file = os.path.join(self.output_dir, f"{self.report_name}.csv")
        print(f"Generating CSV report: {csv_file}")
        
        try:
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    "Query Name", 
                    "Description", 
                    "Original Avg Time (s)", 
                    "Optimized Avg Time (s)",
                    "Improvement (%)",
                    "Speedup (x)",
                    "Original Min Time (s)",
                    "Optimized Min Time (s)",
                    "Original Max Time (s)",
                    "Optimized Max Time (s)"
                ])
                
                # Write data for each query
                for query_name, query_results in self.results["queries"].items():
                    if ("original_index" in query_results and 
                        "optimized_index" in query_results and
                        "stats" in query_results["original_index"] and
                        "stats" in query_results["optimized_index"] and
                        "improvement" in query_results):
                        
                        orig_stats = query_results["original_index"]["stats"]
                        opt_stats = query_results["optimized_index"]["stats"]
                        improvement = query_results["improvement"]
                        
                        writer.writerow([
                            query_name,
                            query_results["description"],
                            f"{orig_stats['avg_time']:.4f}",
                            f"{opt_stats['avg_time']:.4f}",
                            f"{improvement['percentage']:.2f}",
                            f"{improvement['speedup']:.2f}",
                            f"{orig_stats['min_time']:.4f}",
                            f"{opt_stats['min_time']:.4f}",
                            f"{orig_stats['max_time']:.4f}",
                            f"{opt_stats['max_time']:.4f}"
                        ])
                
                # Write summary row
                if "summary" in self.results:
                    summary = self.results["summary"]
                    writer.writerow([])
                    writer.writerow([
                        "SUMMARY",
                        f"Queries: {summary.get('query_count', 0)}",
                        "",
                        "",
                        f"{summary.get('avg_improvement_percentage', 0):.2f}",
                        f"{summary.get('avg_speedup', 0):.2f}",
                        "",
                        "",
                        "",
                        ""
                    ])
            
            print(f"✓ CSV report generated: {csv_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to generate CSV report: {e}")
            return False
    
    def generate_markdown_report(self):
        """Generate Markdown report with benchmark results."""
        if not self.results:
            print("✗ No results loaded")
            return False
        
        md_file = os.path.join(self.output_dir, f"{self.report_name}.md")
        print(f"Generating Markdown report: {md_file}")
        
        try:
            with open(md_file, 'w') as f:
                # Write header
                f.write("# OpenSearch Star-tree Performance Report\n\n")
                
                # Write metadata
                metadata = self.results.get("metadata", {})
                f.write("## Benchmark Configuration\n\n")
                f.write(f"- **Date:** {metadata.get('timestamp', 'Unknown')}\n")
                f.write(f"- **OpenSearch URL:** {metadata.get('opensearch_url', 'Unknown')}\n")
                f.write(f"- **Original Index:** {metadata.get('original_index', 'Unknown')}\n")
                f.write(f"- **Optimized Index:** {metadata.get('optimized_index', 'Unknown')}\n")
                f.write(f"- **Benchmark Iterations:** {metadata.get('iterations', 'Unknown')}\n")
                f.write(f"- **Warmup Iterations:** {metadata.get('warmup_iterations', 'Unknown')}\n\n")
                
                # Write summary
                if "summary" in self.results:
                    summary = self.results["summary"]
                    f.write("## Performance Summary\n\n")
                    f.write(f"- **Average Improvement:** {summary.get('avg_improvement_percentage', 0):.2f}%\n")
                    f.write(f"- **Average Speedup:** {summary.get('avg_speedup', 0):.2f}x\n")
                    f.write(f"- **Queries Benchmarked:** {summary.get('query_count', 0)}\n\n")
                
                # Write detailed results
                f.write("## Detailed Query Results\n\n")
                
                for query_name, query_results in self.results["queries"].items():
                    f.write(f"### Query: {query_name}\n\n")
                    f.write(f"**Description:** {query_results.get('description', 'Unknown')}\n\n")
                    
                    if ("original_index" in query_results and 
                        "optimized_index" in query_results and
                        "stats" in query_results["original_index"] and
                        "stats" in query_results["optimized_index"]):
                        
                        orig_stats = query_results["original_index"]["stats"]
                        opt_stats = query_results["optimized_index"]["stats"]
                        
                        f.write("#### Performance Metrics\n\n")
                        f.write("| Metric | Original Index | Optimized Index | Improvement |\n")
                        f.write("|--------|---------------|-----------------|------------|\n")
                        f.write(f"| Average Time | {orig_stats['avg_time']:.4f}s | {opt_stats['avg_time']:.4f}s | ")
                        
                        if "improvement" in query_results:
                            improvement = query_results["improvement"]
                            f.write(f"{improvement['percentage']:.2f}% ({improvement['speedup']:.2f}x) |\n")
                        else:
                            f.write("N/A |\n")
                            
                        f.write(f"| Min Time | {orig_stats['min_time']:.4f}s | {opt_stats['min_time']:.4f}s | N/A |\n")
                        f.write(f"| Max Time | {orig_stats['max_time']:.4f}s | {opt_stats['max_time']:.4f}s | N/A |\n")
                        f.write(f"| Median Time | {orig_stats['median_time']:.4f}s | {opt_stats['median_time']:.4f}s | N/A |\n")
                        f.write(f"| Std Deviation | {orig_stats['stdev_time']:.4f}s | {opt_stats['stdev_time']:.4f}s | N/A |\n\n")
                    
                    # Add query details
                    if "original_index_first_result" in query_results:
                        f.write("#### Query Details\n\n")
                        f.write("```json\n")
                        f.write(json.dumps(self.benchmark_queries.get(query_name, {}).get("query", {}), indent=2))
                        f.write("\n```\n\n")
                
                # Write conclusion
                f.write("## Conclusion\n\n")
                if "summary" in self.results and self.results["summary"].get("avg_improvement_percentage", 0) > 0:
                    f.write("The star-tree optimization significantly improved query performance. ")
                    f.write(f"With an average improvement of {self.results['summary']['avg_improvement_percentage']:.2f}%, ")
                    f.write(f"queries run {self.results['summary']['avg_speedup']:.2f}x faster on the optimized index.\n\n")
                    
                    if self.results["summary"]["avg_improvement_percentage"] > 50:
                        f.write("This substantial performance gain demonstrates the effectiveness of star-tree indexing ")
                        f.write("for accelerating GROUP BY aggregation queries in OpenSearch.\n")
                    else:
                        f.write("The performance improvement shows that star-tree indexing can be beneficial ")
                        f.write("for accelerating GROUP BY aggregation queries in OpenSearch.\n")
                else:
                    f.write("The benchmark results show mixed performance between the original and optimized indexes. ")
                    f.write("Further tuning of the star-tree configuration may be needed to achieve optimal performance.\n")
            
            print(f"✓ Markdown report generated: {md_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to generate Markdown report: {e}")
            return False
    
    def generate_json_report(self):
        """Generate a cleaned JSON report with the most important metrics."""
        if not self.results:
            print("✗ No results loaded")
            return False
        
        json_file = os.path.join(self.output_dir, f"{self.report_name}.json")
        print(f"Generating JSON report: {json_file}")
        
        try:
            # Create a simplified version of the results
            simplified_results = {
                "metadata": self.results.get("metadata", {}),
                "summary": self.results.get("summary", {}),
                "queries": {}
            }
            
            for query_name, query_results in self.results["queries"].items():
                simplified_results["queries"][query_name] = {
                    "description": query_results.get("description", ""),
                    "original": {
                        "avg_time": query_results.get("original_index", {}).get("stats", {}).get("avg_time", 0),
                        "min_time": query_results.get("original_index", {}).get("stats", {}).get("min_time", 0),
                        "max_time": query_results.get("original_index", {}).get("stats", {}).get("max_time", 0)
                    },
                    "optimized": {
                        "avg_time": query_results.get("optimized_index", {}).get("stats", {}).get("avg_time", 0),
                        "min_time": query_results.get("optimized_index", {}).get("stats", {}).get("min_time", 0),
                        "max_time": query_results.get("optimized_index", {}).get("stats", {}).get("max_time", 0)
                    },
                    "improvement": query_results.get("improvement", {})
                }
            
            with open(json_file, 'w') as f:
                json.dump(simplified_results, f, indent=2)
            
            print(f"✓ JSON report generated: {json_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to generate JSON report: {e}")
            return False
    
    def generate_html_report(self):
        """Generate HTML report with benchmark results."""
        if not self.results:
            print("✗ No results loaded")
            return False
        
        html_file = os.path.join(self.output_dir, f"{self.report_name}.html")
        print(f"Generating HTML report: {html_file}")
        
        try:
            with open(html_file, 'w') as f:
                # Write HTML header
                f.write("<!DOCTYPE html>\n")
                f.write("<html lang=\"en\">\n")
                f.write("<head>\n")
                f.write("  <meta charset=\"UTF-8\">\n")
                f.write("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n")
                f.write("  <title>OpenSearch Star-tree Performance Report</title>\n")
                f.write("  <style>\n")
                f.write("    body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }\n")
                f.write("    h1 { color: #0066cc; }\n")
                f.write("    h2 { color: #0099cc; margin-top: 30px; }\n")
                f.write("    h3 { color: #00aacc; }\n")
                f.write("    table { border-collapse: collapse; width: 100%; margin: 20px 0; }\n")
                f.write("    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n")
                f.write("    th { background-color: #f2f2f2; }\n")
                f.write("    tr:nth-child(even) { background-color: #f9f9f9; }\n")
                f.write("    .improvement-positive { color: green; }\n")
                f.write("    .improvement-negative { color: red; }\n")
                f.write("    .summary-box { background-color: #f0f7ff; border: 1px solid #cce0ff; padding: 15px; border-radius: 5px; margin: 20px 0; }\n")
                f.write("    .query-box { background-color: #f9f9f9; border: 1px solid #ddd; padding: 15px; border-radius: 5px; margin: 20px 0; }\n")
                f.write("    pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }\n")
                f.write("    code { font-family: monospace; }\n")
                f.write("  </style>\n")
                f.write("</head>\n")
                f.write("<body>\n")
                
                # Write header
                f.write("  <h1>OpenSearch Star-tree Performance Report</h1>\n")
                
                # Write metadata
                metadata = self.results.get("metadata", {})
                f.write("  <h2>Benchmark Configuration</h2>\n")
                f.write("  <table>\n")
                f.write("    <tr><th>Parameter</th><th>Value</th></tr>\n")
                f.write(f"    <tr><td>Date</td><td>{metadata.get('timestamp', 'Unknown')}</td></tr>\n")
                f.write(f"    <tr><td>OpenSearch URL</td><td>{metadata.get('opensearch_url', 'Unknown')}</td></tr>\n")
                f.write(f"    <tr><td>Original Index</td><td>{metadata.get('original_index', 'Unknown')}</td></tr>\n")
                f.write(f"    <tr><td>Optimized Index</td><td>{metadata.get('optimized_index', 'Unknown')}</td></tr>\n")
                f.write(f"    <tr><td>Benchmark Iterations</td><td>{metadata.get('iterations', 'Unknown')}</td></tr>\n")
                f.write(f"    <tr><td>Warmup Iterations</td><td>{metadata.get('warmup_iterations', 'Unknown')}</td></tr>\n")
                f.write("  </table>\n")
                
                # Write summary
                if "summary" in self.results:
                    summary = self.results["summary"]
                    f.write("  <h2>Performance Summary</h2>\n")
                    f.write("  <div class=\"summary-box\">\n")
                    
                    improvement_class = "improvement-positive" if summary.get('avg_improvement_percentage', 0) > 0 else "improvement-negative"
                    
                    f.write("    <table>\n")
                    f.write("      <tr><th>Metric</th><th>Value</th></tr>\n")
                    f.write(f"      <tr><td>Average Improvement</td><td class=\"{improvement_class}\">{summary.get('avg_improvement_percentage', 0):.2f}%</td></tr>\n")
                    f.write(f"      <tr><td>Average Speedup</td><td class=\"{improvement_class}\">{summary.get('avg_speedup', 0):.2f}x</td></tr>\n")
                    f.write(f"      <tr><td>Queries Benchmarked</td><td>{summary.get('query_count', 0)}</td></tr>\n")
                    f.write("    </table>\n")
                    f.write("  </div>\n")
                
                # Write detailed results
                f.write("  <h2>Detailed Query Results</h2>\n")
                
                for query_name, query_results in self.results["queries"].items():
                    f.write(f"  <div class=\"query-box\">\n")
                    f.write(f"    <h3>Query: {query_name}</h3>\n")
                    f.write(f"    <p><strong>Description:</strong> {query_results.get('description', 'Unknown')}</p>\n")
                    
                    if ("original_index" in query_results and 
                        "optimized_index" in query_results and
                        "stats" in query_results["original_index"] and
                        "stats" in query_results["optimized_index"]):
                        
                        orig_stats = query_results["original_index"]["stats"]
                        opt_stats = query_results["optimized_index"]["stats"]
                        
                        f.write("    <h4>Performance Metrics</h4>\n")
                        f.write("    <table>\n")
                        f.write("      <tr><th>Metric</th><th>Original Index</th><th>Optimized Index</th><th>Improvement</th></tr>\n")
                        
                        # Average time row
                        f.write("      <tr>\n")
                        f.write("        <td>Average Time</td>\n")
                        f.write(f"        <td>{orig_stats['avg_time']:.4f}s</td>\n")
                        f.write(f"        <td>{opt_stats['avg_time']:.4f}s</td>\n")
                        
                        if "improvement" in query_results:
                            improvement = query_results["improvement"]
                            improvement_class = "improvement-positive" if improvement['percentage'] > 0 else "improvement-negative"
                            f.write(f"        <td class=\"{improvement_class}\">{improvement['percentage']:.2f}% ({improvement['speedup']:.2f}x)</td>\n")
                        else:
                            f.write("        <td>N/A</td>\n")
                        
                        f.write("      </tr>\n")
                        
                        # Other metrics
                        metrics = [
                            ("Min Time", "min_time", "s"),
                            ("Max Time", "max_time", "s"),
                            ("Median Time", "median_time", "s"),
                            ("Std Deviation", "stdev_time", "s")
                        ]
                        
                        for label, key, unit in metrics:
                            f.write("      <tr>\n")
                            f.write(f"        <td>{label}</td>\n")
                            f.write(f"        <td>{orig_stats[key]:.4f}{unit}</td>\n")
                            f.write(f"        <td>{opt_stats[key]:.4f}{unit}</td>\n")
                            f.write("        <td>N/A</td>\n")
                            f.write("      </tr>\n")
                        
                        f.write("    </table>\n")
                    
                    # Add query details
                    if "original_index_first_result" in query_results:
                        f.write("    <h4>Query Details</h4>\n")
                        f.write("    <pre><code>\n")
                        query_json = json.dumps(query_results.get("query", {}), indent=2)
                        f.write(query_json.replace("<", "&lt;").replace(">", "&gt;"))
                        f.write("    </code></pre>\n")
                    
                    f.write("  </div>\n")
                
                # Write conclusion
                f.write("  <h2>Conclusion</h2>\n")
                if "summary" in self.results and self.results["summary"].get("avg_improvement_percentage", 0) > 0:
                    f.write("  <p>The star-tree optimization significantly improved query performance. ")
                    f.write(f"With an average improvement of {self.results['summary']['avg_improvement_percentage']:.2f}%, ")
                    f.write(f"queries run {self.results['summary']['avg_speedup']:.2f}x faster on the optimized index.</p>\n")
                    
                    if self.results["summary"]["avg_improvement_percentage"] > 50:
                        f.write("  <p>This substantial performance gain demonstrates the effectiveness of star-tree indexing ")
                        f.write("for accelerating GROUP BY aggregation queries in OpenSearch.</p>\n")
                    else:
                        f.write("  <p>The performance improvement shows that star-tree indexing can be beneficial ")
                        f.write("for accelerating GROUP BY aggregation queries in OpenSearch.</p>\n")
                else:
                    f.write("  <p>The benchmark results show mixed performance between the original and optimized indexes. ")
                    f.write("Further tuning of the star-tree configuration may be needed to achieve optimal performance.</p>\n")
                
                # Write footer
                f.write("  <hr>\n")
                f.write(f"  <p><em>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>\n")
                f.write("</body>\n")
                f.write("</html>\n")
            
            print(f"✓ HTML report generated: {html_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to generate HTML report: {e}")
            return False
    
    def generate_all_reports(self):
        """Generate all report formats."""
        if not self.load_results():
            return False
        
        if not self.create_output_directory():
            return False
        
        # Store benchmark queries for reference in reports
        if "queries" in self.results:
            self.benchmark_queries = {}
            for query_name, query_results in self.results["queries"].items():
                if "original_index_first_result" in query_results:
                    self.benchmark_queries[query_name] = {
                        "description": query_results.get("description", ""),
                        "query": query_results.get("query", {})
                    }
        
        success = True
        success &= self.generate_csv_report()
        success &= self.generate_markdown_report()
        success &= self.generate_json_report()
        success &= self.generate_html_report()
        
        if success:
            print("\n✓ All reports generated successfully!")
            print(f"✓ Reports directory: {self.output_dir}")
        else:
            print("\n! Some reports failed to generate")
        
        return success

def main():
    """Parse command line arguments and run the report generator."""
    parser = argparse.ArgumentParser(
        description="Generate performance reports from benchmark results"
    )
    
    parser.add_argument('--results', default=DEFAULT_RESULTS_FILE,
                       help=f'Benchmark results file (default: {DEFAULT_RESULTS_FILE})')
    parser.add_argument('--output-dir', default=DEFAULT_OUTPUT_DIR,
                       help=f'Output directory for reports (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--name', default=DEFAULT_REPORT_NAME,
                       help=f'Base name for report files (default: {DEFAULT_REPORT_NAME})')
    
    args = parser.parse_args()
    
    generator = PerformanceReportGenerator(
        results_file=args.results,
        output_dir=args.output_dir,
        report_name=args.name
    )
    
    success = generator.generate_all_reports()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
