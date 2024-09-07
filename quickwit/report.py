import json
import argparse

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Parse JSON and extract fields into TSV format.')
parser.add_argument('input_file', type=str, help='Path to the input JSON file')
args = parser.parse_args()

# Read the JSON file from the provided argument
with open(args.input_file, 'r') as f:
    data = json.load(f)

# Loop through each query in the "queries" array
print(f"Query\tLatency\tCPU Time")
for query in data['queries']:
    name = query['name']
    duration_mean = query['duration']['mean'] / 1e6  # Convert to seconds from microseconds
    cpu_time_mean = query['total_cpu_time_s']['mean']  # Already in seconds
    duration_median = query['duration']['median'] / 1e6  # Convert to seconds from microseconds
    cpu_time_median = query['total_cpu_time_s']['median']  # Already in seconds

    # Format the output as TSV
    output = f"{name}\t{duration_mean:.2f}\t{cpu_time_mean:.2f}\t{duration_median:.2f}\t{cpu_time_median:.2f}"
    
    # Print the output for each query
    print(output)