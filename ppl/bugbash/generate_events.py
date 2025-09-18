#!/usr/bin/env python3
"""
Event Generator Script

Generates n JSON events based on a sample event template with configurable fields.
Output is written as NDJSON (newline-delimited JSON) to events.json.
"""

import argparse
import copy
import json
import random
import sys
from datetime import datetime, timedelta
import dateutil.parser

class Configuration:
    """Configuration for event generation with field distributions"""
    
    def __init__(self):
        # Default field distributions
        self.field_distributions = {
            # Product ID distribution
            "resource.attributes.k8s_label.productid": [
                ("pr12", 10),
                ("pr34", 10),
                ("pr56", 10),
                ("pr78", 20),
                ("pr90", 50)
            ],
            # Also set the same value for productid
            "resource.attributes.productid": [
                ("pr12", 10),
                ("pr34", 10),
                ("pr56", 10),
                ("pr78", 20),
                ("pr90", 50)
            ],
            # Message distribution for body.msg
            "body.msg": [
                ("Error finding unassigned IPs for ENI xyz", 1),
                ("success", 99)
            ],
            # Example of another configurable field
            "resource.attributes.applicationid": [
                ("ap123456", 100)  # Default value with 100% probability
            ]
        }
    
    def add_field_distribution(self, field_path, distribution):
        """
        Add or update a field distribution
        
        Args:
            field_path: Dot-notation path to the field (e.g., "resource.attributes.applicationid")
            distribution: List of tuples (value, percentage)
        """
        self.field_distributions[field_path] = distribution
    
    def get_field_distribution(self, field_path):
        """
        Get the distribution for a field
        
        Args:
            field_path: Dot-notation path to the field
            
        Returns:
            List of tuples (value, percentage) or None if not found
        """
        return self.field_distributions.get(field_path)

class WeightedRandomSelector:
    """Utility for selecting items based on weighted probabilities"""
    
    @staticmethod
    def select(items_with_weights):
        """
        Select an item based on its weight
        
        Args:
            items_with_weights: List of tuples (item, weight)
            
        Returns:
            Selected item
        """
        total_weight = sum(weight for _, weight in items_with_weights)
        r = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for item, weight in items_with_weights:
            cumulative_weight += weight
            if r <= cumulative_weight:
                return item
        
        # Fallback to last item (should not happen with proper weights)
        return items_with_weights[-1][0]

class TimestampManager:
    """Manages timestamp generation and formatting"""
    
    def __init__(self, start_timestamp):
        """
        Initialize with a starting timestamp
        
        Args:
            start_timestamp: ISO 8601 timestamp string
        """
        self.current_timestamp = dateutil.parser.parse(start_timestamp)
    
    def generate_timestamp(self, event_index):
        """
        Generate a timestamp with random milliseconds added to the previous timestamp
        
        Args:
            event_index: Index of the event (0-based)
            
        Returns:
            Tuple of (timestamp string, datetime object)
        """
        if event_index > 0:
            # Add random milliseconds (1-1000) to the previous timestamp
            random_ms = random.randint(1, 1000)
            self.current_timestamp += timedelta(milliseconds=random_ms)
        
        # Format timestamp as ISO 8601
        timestamp_str = self.current_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        return timestamp_str, self.current_timestamp

class EventGenerator:
    """Main class for generating events"""
    
    def __init__(self, sample_event, config):
        """
        Initialize with sample event and configuration
        
        Args:
            sample_event: Dictionary containing the sample event
            config: Configuration instance
        """
        self.sample_event = sample_event
        self.config = config
        self.selector = WeightedRandomSelector()
    
    def set_value_at_path(self, obj, path, value):
        """
        Set a value at a specified path in a nested dictionary
        
        Args:
            obj: Dictionary to modify
            path: Dot-notation path (e.g., "resource.attributes.applicationid")
            value: Value to set
            
        Returns:
            Modified dictionary
        """
        if path == "body.msg":
            # Special handling for body.msg since body is a JSON string
            body_json = json.loads(obj["body"]) if "body" in obj and obj["body"] else {}
            body_json["msg"] = value
            body_json["level"] = "error" if "Error" in value else "info"
            obj["body"] = json.dumps(body_json)
            return obj
        
        # Handle special case for fields with dots in their names
        if path.startswith("resource.attributes.k8s_label."):
            field_name = path.split("resource.attributes.")[1]
            if "resource" in obj and "attributes" in obj["resource"]:
                obj["resource"]["attributes"][field_name] = value
                return obj
        
        # Normal case: navigate through the path
        parts = path.split('.')
        current = obj
        
        # Navigate to the parent object
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
        return obj
    
    def generate_event(self, timestamp_str):
        """
        Generate a single event
        
        Args:
            timestamp_str: Timestamp string to use
            
        Returns:
            Dictionary containing the generated event
        """
        # Create a deep copy of the sample event
        event = copy.deepcopy(self.sample_event)
        
        # Update timestamp fields
        event["@timestamp"] = timestamp_str
        event["time"] = timestamp_str
        
        # Initialize body field if not present
        if "body" not in event or not event["body"]:
            event["body"] = json.dumps({
                "caller": "xyz/abc.go:702",
                "ts": timestamp_str
            })
        
        # Update body.ts field
        body_json = json.loads(event["body"])
        body_json["ts"] = timestamp_str
        event["body"] = json.dumps(body_json)
        
        # Apply all configured field distributions
        for field_path, distribution in self.config.field_distributions.items():
            value = self.selector.select(distribution)
            self.set_value_at_path(event, field_path, value)
        
        return event

def main():
    """Main function"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate JSON events based on a sample template')
    parser.add_argument('--count', '-n', type=int, required=True, help='Number of events to generate')
    parser.add_argument('--start-timestamp', '-t', type=str, required=True, 
                        help='Starting timestamp in ISO 8601 format (e.g., 2025-09-04T16:17:39.133Z)')
    parser.add_argument('--config', '-c', type=str, help='JSON configuration file for field distributions')
    args = parser.parse_args()
    
    # Validate arguments
    try:
        dateutil.parser.parse(args.start_timestamp)
    except ValueError:
        print(f"Error: Invalid timestamp format. Please use ISO 8601 format (e.g., 2025-09-04T16:17:39.133Z)")
        sys.exit(1)
    
    if args.count < 1:
        print(f"Error: Count must be at least 1")
        sys.exit(1)
    
    # Load sample event
    try:
        # Try with relative path first
        try:
            with open('sample_event.json', 'r') as f:
                sample_event = json.load(f)
        except FileNotFoundError:
            # Fall back to absolute path
            with open('ppl/bugbash/sample_event.json', 'r') as f:
                sample_event = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading sample event: {e}")
        sys.exit(1)
    
    # Initialize components
    config = Configuration()
    
    # Load custom configuration if provided
    if args.config:
        try:
            with open(args.config, 'r') as f:
                custom_config = json.load(f)
                
                # Apply custom field distributions
                for field_path, distribution in custom_config.items():
                    config.add_field_distribution(field_path, distribution)
                    
            print(f"Loaded custom configuration from {args.config}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading configuration file: {e}")
            sys.exit(1)
    
    timestamp_manager = TimestampManager(args.start_timestamp)
    generator = EventGenerator(sample_event, config)
    
    # Generate events and write to file
    with open('events.json', 'w') as f:
        for i in range(args.count):
            # Generate timestamp with random milliseconds
            timestamp_str, _ = timestamp_manager.generate_timestamp(i)
            
            # Generate event
            event = generator.generate_event(timestamp_str)
            
            # Write event as NDJSON (each event on a new line)
            f.write(json.dumps(event) + '\n')
            
            # Show progress for large generations
            if args.count > 100 and i % (args.count // 10) == 0:
                print(f"Progress: {i}/{args.count} events generated")
    
    print(f"Successfully generated {args.count} events and saved to events.json")

if __name__ == "__main__":
    main()
