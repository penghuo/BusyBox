import boto3
import time
import numpy as np
import csv

# Initialize the Glue client
glue_client = boto3.client('glue')

# Define job details
role_arn = 'arn:aws:iam::924196221507:role/service-role/AWSGlueServiceRole-ALB'
session_name = 'my-glue-session'
num_iterations = 1


total_runtimes = []
execution_times = []
session_creation_times = []

# Function to create a Glue session
def create_glue_session(session_name, role_arn):
    start_time = time.time()
    response = glue_client.create_session(
        Id=session_name,
        Role=role_arn,
        Command={
            'Name': 'glueetl', 
            'PythonVersion': '3'
        },
        WorkerType='G.1X',  
        NumberOfWorkers=10  
    )
    session_id = response['Session']['Id']
    end_time = time.time()
    
    session_creation_time = end_time - start_time
    session_creation_times.append(session_creation_time)
    
    print(f"Created Glue Session ID: {session_id} in {session_creation_time} seconds")
    return session_id

def wait_for_session_ready(session_id):
    while True:
        response = glue_client.get_session(Id=session_id)
        status = response['Session']['Status']
        
        if status == 'READY':
            print(f"Session {session_id} is ready.")
            break
        elif status in ['FAILED', 'TIMEOUT']:
            print(f"Session {session_id} failed with status: {status}")
            raise Exception(f"Session {session_id} failed with status: {status}")
        
        print(f"Waiting for session {session_id} to be ready... Current status: {status}")
        time.sleep(10)  # Polling every 10 seconds


def submit_job_to_session(session_id, code):
    response = glue_client.run_statement(
        SessionId=session_id,
        Code=code
    )
    print(f"Submit job to session: {session_id}, job: {response['Id']}")
    return response['Id']

# Function to get job status
def check_job_status(session_id, statement_id):
    response = glue_client.get_statement(
        SessionId=session_id,
        Id=statement_id
    )
    print(f"Response: {session_id}, job: {response}")
    return response['Output']['Status']

# Function to retrieve job results
def get_job_result(session_id, statement_id):
    response = glue_client.get_statement_result(
        SessionId=session_id,
        Id=statement_id
    )
    return response['Result']

# Function to delete the Glue session
def delete_glue_session(session_id):
    glue_client.delete_session(SessionId=session_id)
    print(f"Deleted Glue Session ID: {session_id}")

# Function to collect and print metrics
def collect_metrics(start_time, end_time, execution_time):
    total_runtime = end_time - start_time
    total_runtimes.append(total_runtime)
    execution_times.append(execution_time / 1000)  # Convert ms to seconds

    print(f"Total Runtime: {total_runtime} seconds")
    print(f"Execution Time: {execution_time / 1000} seconds")

# Function to calculate P50, P90, and Max latency
def calculate_percentiles(times, label):
    p50 = np.percentile(times, 50)
    p90 = np.percentile(times, 90)
    max_latency = max(times)
    
    print(f"\n{label} Latency Metrics:")
    print(f"P50 (Median): {p50} seconds")
    print(f"P90: {p90} seconds")
    print(f"Max: {max_latency} seconds")

# Function to dump latency data to CSV
def dump_to_csv(total_runtime_metrics, execution_time_metrics, session_creation_metrics, filename='latency_metrics.csv'):
    header = ['Metric', 'P50', 'P90', 'Max']
    rows = [
        ['Total Runtime', total_runtime_metrics[0], total_runtime_metrics[1], total_runtime_metrics[2]],
        ['Execution Time', execution_time_metrics[0], execution_time_metrics[1], execution_time_metrics[2]],
        ['Session Creation Time', session_creation_metrics[0], session_creation_metrics[1], session_creation_metrics[2]]
    ]
    
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)
        csvwriter.writerows(rows)
    
    print(f"\nLatency metrics written to {filename}")

# Example Scala code to submit
scala_code = """
import com.amazonaws.services.glue.GlueContext
import com.amazonaws.services.glue.util.GlueArgParser
import com.amazonaws.services.glue.util.Job
import java.util.Calendar
import org.apache.spark.SparkContext
import org.apache.spark.sql.Dataset
import org.apache.spark.sql.Row
import org.apache.spark.sql.SaveMode
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions.from_json
import org.apache.spark.sql.streaming.Trigger
import scala.collection.JavaConverters._

object GlueApp {
  def main(sysArgs: Array[String]) {
    val spark: SparkContext = new SparkContext()
    val glueContext: GlueContext = new GlueContext(spark)
    val sparkSession: SparkSession = glueContext.getSparkSession
    import sparkSession.implicits._
    val args = GlueArgParser.getResolvedOptions(sysArgs, Seq("JOB_NAME").toArray)
    Job.init(args("JOB_NAME"), glueContext, args.asJava)

    sparkSession.sql("SELECT count(*) FROM `default`.`http_logs`").show()

    Job.commit()
  }
}
"""

# Benchmark loop
for i in range(num_iterations):
    print(f"Iteration {i+1}/{num_iterations}")

    # Create the Glue session and measure session creation time
    # session_id = create_glue_session(session_name, role_arn)
    session_id = "my-glue-session"

        # Wait for the session to become ready
    wait_for_session_ready(session_id)
    
    start_time = time.time()

    # Submit the Scala job
    statement_id = submit_job_to_session(session_id, scala_code)

    # Check the status until the job is completed
    while True:
        job_status = check_job_status(session_id, statement_id)
        if job_status == 'FINISHED':
            break
        elif job_status in ['FAILED', 'CANCELLED']:
            print(f"Job failed with status: {job_status}")
            break
        time.sleep(10)  # Check status every 10 seconds

    end_time = time.time()

    # Collect and print metrics if the job succeeded
    if job_status == 'FINISHED':
        job_result = get_job_result(session_id, statement_id)
        execution_time = job_result.get('ExecutionTime', 0)  # Get execution time in milliseconds
        collect_metrics(start_time, end_time, execution_time)

    print(f"Total time for iteration {i+1}: {end_time - start_time} seconds")
    print("-" * 60)

    # Delete the Glue session
    delete_glue_session(session_id)

# Calculate and print P50, P90, and Max for total_runtime, execution_time, and session creation time
if total_runtimes and execution_times and session_creation_times:
    total_runtime_metrics = calculate_percentiles(total_runtimes, "Total Runtime")
    execution_time_metrics = calculate_percentiles(execution_times, "Execution Time")
    session_creation_metrics = calculate_percentiles(session_creation_times, "Session Creation Time")
    
    # Dump the results to a CSV file
    dump_to_csv(total_runtime_metrics, execution_time_metrics, session_creation_metrics)
