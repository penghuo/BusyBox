import boto3
import time
import numpy as np
import csv

# Initialize boto3 clients
glue_client = boto3.client('glue')

job_name = 'glueetl-spark'
script_location = 's3://flint-data-dp-us-west-2-beta/code/penghuo/glueetl/glueetl-spark.scala'
num_iterations = 10

total_runtimes = []
execution_times = []

# Function to submit a job
def submit_job(job_name):
    response = glue_client.start_job_run(JobName=job_name)
    job_run_id = response['JobRunId']
    return job_run_id

# Function to get job state
def get_job_status(job_name, job_run_id):
    response = glue_client.get_job_run(JobName=job_name, RunId=job_run_id)
    return response['JobRun']['JobRunState'], response

# Function to monitor job until completion
def monitor_job(job_name, job_run_id):
    while True:
        status, response = get_job_status(job_name, job_run_id)
        if status in ['SUCCEEDED', 'FAILED', 'STOPPED']:
            return status, response
        time.sleep(30)  # Check status every 30 seconds

# Function to collect and print metrics
def collect_metrics(response):
    # Get start and complete times in milliseconds
    started_on = response['JobRun']['StartedOn'].timestamp()
    completed_on = response['JobRun']['CompletedOn'].timestamp()

    total_runtime = completed_on - started_on  # Convert to seconds
    execution_time = response['JobRun']['ExecutionTime'] / 1000  # Execution time in seconds

    # Append times to the arrays
    total_runtimes.append(total_runtime)
    execution_times.append(execution_time)

    print(f"Job Run ID: {response['JobRun']['Id']}")
    print(f"Total Runtime: {total_runtime} seconds")
    print(f"Execution Time: {execution_time} seconds")

# Function to calculate P50, P90, and Max latency
def calculate_percentiles(times, label):
    p50 = np.percentile(times, 50)
    p90 = np.percentile(times, 90)
    max_latency = max(times)
    
    print(f"\n{label} Latency Metrics:")
    print(f"P50 (Median): {p50} seconds")
    print(f"P90: {p90} seconds")
    print(f"Max: {max_latency} seconds")
    
    return p50, p90, max_latency

# Function to write latency data to CSV
def dump_to_csv(total_runtime_metrics, execution_time_metrics, filename='latency_metrics.csv'):
    header = ['Metric', 'P50', 'P90', 'Max']
    rows = [
        ['Total Runtime', total_runtime_metrics[0], total_runtime_metrics[1], total_runtime_metrics[2]],
        ['Execution Time', execution_time_metrics[0], execution_time_metrics[1], execution_time_metrics[2]]
    ]
    
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)
        csvwriter.writerows(rows)
    
    print(f"\nLatency metrics written to {filename}")

# Benchmark loop
for i in range(num_iterations):
    print(f"Submitting job iteration {i+1}/{num_iterations}")
    start_time = time.time()
    
    # Submit the job
    job_run_id = submit_job(job_name)
    
    # Monitor the job status
    status, response = monitor_job(job_name, job_run_id)
    
    if status == 'SUCCEEDED':
        # Collect metrics
        collect_metrics(response)
    else:
        print(f"Job {job_run_id} failed with status: {status}")
    
    end_time = time.time()
    print(f"Total time for iteration {i+1}: {end_time - start_time} seconds")
    print("-" * 60)

# Calculate and print P50, P90, and Max for total_runtime and execution_time
if total_runtimes and execution_times:
    total_runtime_metrics = calculate_percentiles(total_runtimes, "Total Runtime")
    execution_time_metrics = calculate_percentiles(execution_times, "Execution Time")
    
    # Dump the results to a CSV file
    dump_to_csv(total_runtime_metrics, execution_time_metrics)