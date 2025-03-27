import json
import argparse

def sum_max_times(file):
    # Read first file
    with open(file, 'r') as f:
        data1 = json.load(f)
    
    # Extract max times from both files
    max_times = []
    
    # Process first file's results
    for result in data1.get('results', []):
        max_times.append(result.get('max_time', 0))
    
    # Calculate total sum
    total = sum(max_times)
    return total

def main():
    parser = argparse.ArgumentParser(description='Sum max_time from two benchmark files')
    parser.add_argument('file', help='First benchmark JSON file')
    args = parser.parse_args()

    total = sum_max_times(args.file)
    print(f"Total sum of max_time values: {total:.4f} seconds")

if __name__ == "__main__":
    main()