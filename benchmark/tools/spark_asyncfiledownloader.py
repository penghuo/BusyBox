import re
import argparse
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

# Fixed time window constraints
START_TIME = datetime.strptime('25/03/24 20:24:05', '%d/%m/%y %H:%M:%S')
END_TIME = datetime.strptime('25/03/24 20:24:46', '%d/%m/%y %H:%M:%S')

def parse_log(log_file):
    download_events = []
    current_downloads = {}

    download_start_pattern = re.compile(
        r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*AsyncFileDownloader: TID: (\d+) - Downloading')
    
    download_end_pattern = re.compile(
        r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*AsyncFileDownloader: TID: (\d+) - Downloaded')

    with open(log_file, 'r') as f:
        for line in f:
            # Process only lines within our time window
            time_match = re.search(r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', line)
            if time_match:
                line_time = datetime.strptime(time_match.group(1), '%d/%m/%y %H:%M:%S')
                if line_time < START_TIME - timedelta(seconds=2) or line_time > END_TIME + timedelta(seconds=2):
                    continue

            # Track download starts
            if "Downloading ParquetFileChunkGroup" in line:
                match = download_start_pattern.search(line)
                if match:
                    timestamp = datetime.strptime(match.group(1), '%d/%m/%y %H:%M:%S')
                    if timestamp > END_TIME:
                        continue
                    tid = match.group(2)
                    current_downloads[tid] = {
                        'start': timestamp,
                        'tid': tid,
                        'end': None
                    }
            
            # Track download completions
            elif "Downloaded ParquetFileChunkGroup" in line:
                match = download_end_pattern.search(line)
                if match:
                    timestamp = datetime.strptime(match.group(1), '%d/%m/%y %H:%M:%S')
                    if timestamp < START_TIME:
                        continue
                    tid = match.group(2)
                    if tid in current_downloads:
                        current_downloads[tid]['end'] = timestamp
                        event = current_downloads[tid]
                        # Only include events that overlap with our window
                        if event['end'] >= START_TIME and event['start'] <= END_TIME:
                            event['duration'] = (event['end'] - event['start']).total_seconds()
                            download_events.append(event)
                        del current_downloads[tid]

    return download_events

def plot_parallel_downloads(download_events):
    plt.figure(figsize=(14, 6))
    
    # Create colormap for TIDs
    unique_tids = list(set(event['tid'] for event in download_events))
    colors = ListedColormap(plt.cm.tab20.colors[:len(unique_tids)])
    tid_to_color = {tid: colors(i) for i, tid in enumerate(unique_tids)}

    # Plot each download with TID-based coloring
    for i, event in enumerate(download_events):
        plt.plot([event['start'], event['end']], [i, i],
                color=tid_to_color[event['tid']],
                linewidth=4,
                solid_capstyle='butt')

    # Calculate concurrency
    time_points = []
    for event in download_events:
        time_points.append((event['start'], 'start'))
        time_points.append((event['end'], 'end'))
    
    time_points.sort()
    current_concurrency = 0
    max_concurrency = 0
    concurrency = []
    
    for t, action in time_points:
        current_concurrency += 1 if action == 'start' else -1
        max_concurrency = max(max_concurrency, current_concurrency)
        concurrency.append((t, current_concurrency))

    # Plot concurrency
    times, values = zip(*concurrency)
    plt.step(times, values, 
            where='post', 
            color='black', 
            linestyle=':',
            linewidth=1,
            label='Concurrent Tasks')

    # Formatting
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
    ax.xaxis.set_major_locator(mdates.SecondLocator(interval=5))
    plt.xticks(rotation=45)
    
    plt.ylabel('Download Task Sequence')
    plt.xlabel('Time (Minutes:Seconds)')
    plt.title(f'Parallel Downloads Analysis ({START_TIME.strftime("%H:%M:%S")} to {END_TIME.strftime("%H:%M:%S")})\nMax Concurrent Tasks: {max_concurrency}')
    plt.grid(True, alpha=0.3)
    
    # Set axis limits to our focused window
    plt.xlim(START_TIME - timedelta(seconds=1), END_TIME + timedelta(seconds=1))
    
    # Create legend
    legend_elements = [Patch(facecolor=tid_to_color[tid], label=f'TID {tid}') 
                      for tid in unique_tids]
    legend_elements.append(plt.Line2D([0], [0], color='black', linestyle=':', 
                                   label='Concurrent Tasks'))
    
    plt.legend(handles=legend_elements, 
              loc='upper right',
              fontsize=9)

    plt.tight_layout()
    plt.savefig('focused_parallel_downloads.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Analyze parallel downloads in time window')
    parser.add_argument('log_file', help='Path to the stderr.txt log file')
    args = parser.parse_args()

    download_events = parse_log(args.log_file)
    plot_parallel_downloads(download_events)

if __name__ == "__main__":
    main()