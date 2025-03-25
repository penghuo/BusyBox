import re
import argparse
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def parse_log(log_file):
    download_events = []
    scan_events = []
    current_download = None

    # Regex patterns
    download_start_pattern = re.compile(
        r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) INFO AsyncFileDownloader: TID: (\d+) - Downloading (ParquetFileChunkGroup\(.*?\)), downloadSize=([\d.]+) MiB')
    
    download_end_pattern = re.compile(
        r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) INFO AsyncFileDownloader: TID: (\d+) - Downloaded (ParquetFileChunkGroup\(.*?\)), elapsedTime=(\d+) micros')
    
    scan_pattern = re.compile(
        r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) INFO FileScanRDD: TID: (\d+) - Got next file: (.*?)\. Elapsed time: (\d+) micros')

    with open(log_file, 'r') as f:
        for line in f:
            # Parse download start events
            if "Downloading ParquetFileChunkGroup" in line:
                match = download_start_pattern.search(line)
                if match:
                    timestamp = datetime.strptime(match.group(1), '%d/%m/%y %H:%M:%S')
                    tid = match.group(2)
                    file_info = match.group(3)
                    size = float(match.group(4))
                    current_download = {
                        'start': timestamp,
                        'tid': tid,
                        'file': file_info,
                        'size': size,
                        'end': None
                    }
            
            # Parse download end events
            elif "Downloaded ParquetFileChunkGroup" in line:
                match = download_end_pattern.search(line)
                if match and current_download:
                    timestamp = datetime.strptime(match.group(1), '%d/%m/%y %H:%M:%S')
                    tid = match.group(2)
                    file_info = match.group(3)
                    duration = int(match.group(4)) / 1e6  # Convert microseconds to seconds
                    
                    if current_download['tid'] == tid:
                        current_download['end'] = timestamp
                        current_download['duration'] = duration
                        download_events.append(current_download)
                        current_download = None
            
            # Parse file scan events
            elif "Got next file" in line:
                match = scan_pattern.search(line)
                if match:
                    timestamp = datetime.strptime(match.group(1), '%d/%m/%y %H:%M:%S')
                    tid = match.group(2)
                    file_info = match.group(3)
                    elapsed = int(match.group(4)) / 1e6  # Convert microseconds to seconds
                    scan_events.append({
                        'timestamp': timestamp,
                        'tid': tid,
                        'file_info': file_info,
                        'elapsed': elapsed
                    })

    return download_events, scan_events

def plot_timeline(download_events, scan_events):
    plt.figure(figsize=(18, 10))
    
    # Plot download durations with annotations
    max_y = len(download_events) + 2  # For annotation space
    for i, dl in enumerate(download_events):
        # Plot download duration line
        line = plt.plot([dl['start'], dl['end']], [i, i],
                       linewidth=3,
                       color='royalblue',
                       marker='|',
                       markersize=10,
                       markeredgewidth=2)
        
        # Add duration and size annotation
        mid_time = dl['start'] + (dl['end'] - dl['start']) / 2
        plt.text(mid_time, i + 0.3,
                f"{dl['size']} MiB ({dl['duration']:.1f}s)",
                rotation=40,
                ha='center',
                va='bottom',
                fontsize=9,
                color='darkblue',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    # Plot scan events with different markers
    scan_times = [s['timestamp'] for s in scan_events]
    scan_labels = [f"Scan: {s['elapsed']:.1f}s" for s in scan_events]
    
    scatter = plt.scatter(scan_times, 
                        [-0.5] * len(scan_times),
                        color='crimson',
                        marker='X',
                        s=100,
                        edgecolor='black',
                        linewidth=0.8,
                        label='FileScan Start',
                        zorder=3)

    # Add scan time annotations
    for i, (time, label) in enumerate(zip(scan_times, scan_labels)):
        plt.text(time, -0.8, label,
                rotation=45,
                ha='right',
                va='top',
                fontsize=8,
                color='darkred')

    # Formatting
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.SecondLocator(interval=5))
    plt.xticks(rotation=45)
    
    # Set axis limits
    plt.ylim(-2, max_y)
    plt.xlim(download_events[0]['start'] - timedelta(seconds=2), 
            scan_events[-1]['timestamp'] + timedelta(seconds=2))

    # Create custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='royalblue', lw=3, 
               label='File Download (Size + Duration)'),
        Line2D([0], [0], marker='X', color='crimson', lw=0,
               markerfacecolor='crimson', markersize=10,
               label='FileScanRDD Start (Processing Time)')
    ]
    
    plt.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    plt.ylabel('Download Sequence', fontsize=12)
    plt.xlabel('Timeline', fontsize=12)
    plt.title('I/O Operation Timeline Analysis\nBlue: File Downloads with Size/Duration, Red: Scan Start Times', 
             fontsize=14, pad=20)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save and show
    plt.savefig('detailed_io_timeline.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Analyze Spark I/O timeline')
    parser.add_argument('log_file', help='Path to the stderr.txt log file')
    args = parser.parse_args()

    download_events, scan_events = parse_log(args.log_file)
    plot_timeline(download_events, scan_events)

if __name__ == "__main__":
    main()