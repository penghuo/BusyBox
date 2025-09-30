#!/usr/bin/env python3
"""
MTG Card Price and Availability Checker

This script reads MTG card names from a text file and queries configurable
MTG store websites to get availability and pricing information.

Usage:
    python mtg_price_checker.py [--input cards.txt] [--store elegantoctopus] [--output results.csv]
"""

import json
import csv
import requests
import argparse
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path


class MTGStore:
    """Base class for MTG store API interactions"""
    
    def __init__(self, store_config: Dict[str, Any]):
        self.config = store_config
        self.name = store_config.get('name', 'Unknown Store')
        self.search_url = store_config['search_url']
        self.inventory_url = store_config['inventory_url']
        self.headers = store_config.get('headers', {})
        self.search_payload_template = store_config['search_payload']
    
    def search_cards(self, card_name: str) -> List[Dict[str, Any]]:
        """Search for cards and return product information"""
        try:
            # Prepare search payload
            payload = self.search_payload_template.copy()
            payload['query'] = card_name
            
            # Make search request
            response = requests.post(
                self.search_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            products = data.get('products', {}).get('items', [])
            
            print(f"Found {len(products)} products for '{card_name}'")
            return products
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching for '{card_name}': {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing search response for '{card_name}': {e}")
            return []
    
    def get_inventory(self, product_ids: List[int]) -> List[Dict[str, Any]]:
        """Get inventory and pricing for product IDs"""
        if not product_ids:
            return []
        
        try:
            # Convert product IDs to comma-separated string
            product_ids_str = ','.join(map(str, product_ids))
            
            # Make inventory request
            inventory_url = f"{self.inventory_url}?productIds={product_ids_str}"
            response = requests.get(
                inventory_url,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            print(f"Retrieved inventory for {len(product_ids)} products")
            return data if isinstance(data, list) else []
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting inventory for product IDs {product_ids}: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing inventory response: {e}")
            return []


class MTGPriceChecker:
    """Main class for checking MTG card prices and availability"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config = self.load_config(config_file)
        self.stores = {}
        
        # Initialize stores from config
        for store_key, store_config in self.config['stores'].items():
            self.stores[store_key] = MTGStore(store_config)
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file '{config_file}' not found!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            sys.exit(1)
    
    def load_card_names(self, input_file: str) -> List[str]:
        """Load card names from text file (one per line)"""
        try:
            with open(input_file, 'r') as f:
                cards = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(cards)} card names from '{input_file}'")
            return cards
        except FileNotFoundError:
            print(f"Input file '{input_file}' not found!")
            sys.exit(1)
    
    def process_card_results(self, card_name: str, products: List[Dict], inventory_data: List[Dict]) -> Dict:
        """Process search and inventory results for a single card - return one consolidated result"""
        all_skus = []
        
        # Create a mapping of product ID to product info
        product_map = {product['id']: product for product in products}
        
        # Collect all available SKUs across all products
        for item in inventory_data:
            product_id = item.get('productId')
            skus = item.get('skus', [])
            
            if product_id not in product_map:
                continue
            
            # Process each SKU (inventory item)
            for sku in skus:
                quantity = sku.get('quantity', 0)
                price = sku.get('price', 0.0)
                
                # Only include items with quantity > 0
                if quantity > 0:
                    all_skus.append({
                        'price': price,
                        'quantity': quantity
                    })
        
        # Consolidate results for this card
        if all_skus:
            # Sort by price to get lowest price
            all_skus.sort(key=lambda x: x['price'])
            lowest_price = all_skus[0]['price']
            total_quantity = sum(sku['quantity'] for sku in all_skus)
            
            return {
                'card_name': card_name,
                'availability': 'Available',
                'price': lowest_price,
                'quantity': total_quantity
            }
        else:
            # No available inventory found
            return {
                'card_name': card_name,
                'availability': 'n/a',
                'price': 'n/a',
                'quantity': 0
            }
    
    def check_card_prices(self, card_name: str, store_key: str) -> Dict:
        """Check prices for a single card at a specific store - return one consolidated result"""
        if store_key not in self.stores:
            print(f"Store '{store_key}' not configured!")
            return {
                'card_name': card_name,
                'availability': 'n/a',
                'price': 'n/a',
                'quantity': 0
            }
        
        store = self.stores[store_key]
        print(f"\nChecking prices for '{card_name}' at {store.name}...")
        
        # Step 1: Search for products
        products = store.search_cards(card_name)
        if not products:
            print(f"No products found for '{card_name}'")
            return {
                'card_name': card_name,
                'availability': 'n/a',
                'price': 'n/a',
                'quantity': 0
            }
        
        # Step 2: Get inventory for product IDs
        product_ids = [product['id'] for product in products]
        inventory_data = store.get_inventory(product_ids)
        
        if not inventory_data:
            print(f"No inventory data found for '{card_name}'")
            return {
                'card_name': card_name,
                'availability': 'n/a',
                'price': 'n/a',
                'quantity': 0
            }
        
        # Step 3: Process results
        result = self.process_card_results(card_name, products, inventory_data)
        return result
    
    def check_all_cards(self, input_file: str, store_key: str) -> List[Dict]:
        """Check prices for all cards in the input file - one result per card"""
        card_names = self.load_card_names(input_file)
        all_results = []
        
        for card_name in card_names:
            try:
                result = self.check_card_prices(card_name, store_key)
                all_results.append(result)
            except Exception as e:
                print(f"Error processing '{card_name}': {e}")
                # Still add an n/a result for this card
                all_results.append({
                    'card_name': card_name,
                    'availability': 'n/a',
                    'price': 'n/a',
                    'quantity': 0
                })
                continue
        
        return all_results
    
    def save_results(self, results: List[Dict], output_file: str):
        """Save results to CSV file"""
        if not results:
            print("No results to save!")
            return
        
        fieldnames = ['card_name', 'availability', 'price', 'quantity']
        
        try:
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            print(f"\nResults saved to '{output_file}'")
            print(f"Total cards processed: {len(results)}")
            
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def print_results(self, results: List[Dict]):
        """Print results to console in a formatted table with summary"""
        if not results:
            print("No results to display!")
            return
        
        print("\n" + "="*70)
        print(f"{'Card Name':<30} {'Availability':<12} {'Price':<10} {'Quantity':<8}")
        print("="*70)
        
        total_cards = len(results)
        available_cards = 0
        total_price = 0.0
        
        for result in results:
            card_name = result['card_name'][:29]
            availability = result['availability']
            price = result['price']
            quantity = result['quantity']
            
            # Format price display
            if price == 'n/a':
                price_display = 'n/a'
            else:
                price_display = f"${price:.2f}"
                total_price += price
                available_cards += 1
            
            print(f"{card_name:<30} {availability:<12} {price_display:<10} {quantity:<8}")
        
        print("="*70)
        print("\n📊 SUMMARY:")
        print(f"Total cards: {total_cards}")
        print(f"Available cards: {available_cards}")
        print(f"Unavailable cards: {total_cards - available_cards}")
        print(f"Total price (lowest available): ${total_price:.2f}")
        print("="*70)


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description='Check MTG card availability and prices from configured stores'
    )
    parser.add_argument(
        '--input', '-i',
        default='cards.txt',
        help='Input file with card names (one per line) [default: cards.txt]'
    )
    parser.add_argument(
        '--store', '-s',
        default='elegantoctopus',
        help='Store to check prices at [default: elegantoctopus]'
    )
    parser.add_argument(
        '--output', '-o',
        default='results.csv',
        help='Output CSV file [default: results.csv]'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Configuration file [default: config.json]'
    )
    parser.add_argument(
        '--print-only', '-p',
        action='store_true',
        help='Only print results to console, do not save CSV'
    )
    
    args = parser.parse_args()
    
    # Initialize price checker
    checker = MTGPriceChecker(args.config)
    
    # Check card prices
    print(f"Starting MTG price check...")
    print(f"Input file: {args.input}")
    print(f"Store: {args.store}")
    
    results = checker.check_all_cards(args.input, args.store)
    
    # Output results
    checker.print_results(results)
    
    if not args.print_only:
        checker.save_results(results, args.output)


if __name__ == '__main__':
    main()
