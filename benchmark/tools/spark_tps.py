import re
import argparse
from datetime import datetime
import statistics

def parse_downloads(log_file):
    downloads = {}
    throughput_records = []  # List of dicts: {tid, throughput}
    
    # Regex patterns
    start_pattern = re.compile(
        r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*AsyncFileDownloader: TID: (\d+).*downloadSize=([\d.]+) MiB'
    )
    end_pattern = re.compile(
        r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*AsyncFileDownloader: TID: (\d+).*elapsedTime=(\d+) micros'
    )

    with open(log_file, 'r') as f:
        for line in f:
            # Process start events
            start_match = start_pattern.search(line)
            if start_match:
                timestamp = datetime.strptime(start_match.group(1), '%d/%m/%y %H:%M:%S')
                tid = start_match.group(2)
                size_mib = float(start_match.group(3))
                downloads[tid] = {
                    'start': timestamp,
                    'size_mib': size_mib,
                    'end': None,
                    'duration_sec': None
                }
                continue
                
            # Process end events
            end_match = end_pattern.search(line)
            if end_match:
                timestamp = datetime.strptime(end_match.group(1), '%d/%m/%y %H:%M:%S')
                tid = end_match.group(2)
                micros = int(end_match.group(3))
                
                if tid in downloads:
                    duration_sec = micros / 1_000_000
                    throughput = downloads[tid]['size_mib'] / duration_sec
                    
                    throughput_records.append({
                        'tid': tid,
                        'throughput': throughput,
                        'size_mib': downloads[tid]['size_mib'],
                        'duration_sec': duration_sec
                    })
                    del downloads[tid]

    return throughput_records

def calculate_stats(records):
    if not records:
        return None
    
    throughputs = [r['throughput'] for r in records]
    min_record = min(records, key=lambda x: x['throughput'])
    max_record = max(records, key=lambda x: x['throughput'])
    
    return {
        'avg': statistics.mean(throughputs),
        'min': min_record,
        'max': max_record,
        'count': len(records),
        'unit': 'MiB/s'
    }

def main():
    parser = argparse.ArgumentParser(description='Calculate AsyncFileDownloader throughput statistics')
    parser.add_argument('log_file', help='Path to the log file to analyze')
    args = parser.parse_args()

    records = parse_downloads(args.log_file)
    
    if not records:
        print("No complete download records found")
        return
    
    stats = calculate_stats(records)
    
    print(f"Throughput Analysis ({stats['count']} transfers):")
    print(f"Average: {stats['avg']:.2f} {stats['unit']}")
    print("\nMinimum Throughput Task:")
    print(f"  TID: {stats['min']['tid']}")
    print(f"  Throughput: {stats['min']['throughput']:.2f} {stats['unit']}")
    print(f"  Size: {stats['min']['size_mib']:.1f} MiB")
    print(f"  Duration: {stats['min']['duration_sec']:.2f}s")
    print("\nMaximum Throughput Task:")
    print(f"  TID: {stats['max']['tid']}")
    print(f"  Throughput: {stats['max']['throughput']:.2f} {stats['unit']}")
    print(f"  Size: {stats['max']['size_mib']:.1f} MiB")
    print(f"  Duration: {stats['max']['duration_sec']:.2f}s")

if __name__ == "__main__":
    main()