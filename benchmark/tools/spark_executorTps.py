import re
from datetime import datetime

def parse_log(file_path, start_time, end_time):
    total_size = 0
    pattern = re.compile(r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) INFO AsyncFileDownloader: .*?downloadSize=([\d\.]+)\s*(KiB|MiB)')
    
    start_dt = datetime.strptime(start_time, "%d/%m/%y %H:%M:%S")
    end_dt = datetime.strptime(end_time, "%d/%m/%y %H:%M:%S")
    
    with open(file_path, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                log_time = datetime.strptime(match.group(1), "%d/%m/%y %H:%M:%S")
                if start_dt <= log_time <= end_dt:
                    size, unit = float(match.group(2)), match.group(3)
                    if unit == 'MiB':
                        size *= 1024  # Convert MiB to KiB
                    total_size += size
    
    duration_seconds = (end_dt - start_dt).total_seconds()
    throughput_mbps = (total_size * 8) / (duration_seconds * 1024) if duration_seconds > 0 else 0  # Convert KiB to Mbps
    
    return total_size / 1024, throughput_mbps  # Convert KiB to MiB for final output

if __name__ == "__main__":
    log_file = "/Users/penghuo/logs/stderr.txt"
    start_time = "25/03/24 20:24:05"
    end_time = "25/03/24 20:24:46"
    total_download_size, throughput = parse_log(log_file, start_time, end_time)
    print(f"Total Download Size: {total_download_size:.2f} MiB")
    print(f"Throughput: {throughput:.2f} Mbps")
