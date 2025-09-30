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
        self.inventory_url = store_config.get('inventory_url')  # Optional for some stores
        self.headers = store_config.get('headers', {})
        self.search_payload_template = store_config['search_payload']
        self.store_type = store_config.get('type', 'tcgplayer_pro')  # Default to original type
    
    def search_cards(self, card_name: str) -> List[Dict[str, Any]]:
        """Search for cards and return product information"""
        try:
            # Prepare search payload based on store type
            payload = self.search_payload_template.copy()
            
            if self.store_type == 'tcgplayer_pro':
                payload['query'] = card_name
            elif self.store_type == 'conductcommerce':
                payload['name'] = card_name
            
            # Make search request
            response = requests.post(
                self.search_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different response formats
            if self.store_type == 'tcgplayer_pro':
                products = data.get('products', {}).get('items', [])
            elif self.store_type == 'conductcommerce':
                products = data.get('result', {}).get('listings', [])
            else:
                products = []
            
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
    
    def process_tcgplayer_results(self, card_name: str, products: List[Dict], inventory_data: List[Dict]) -> Dict:
        """Process TCGPlayer Pro style search and inventory results"""
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
    
    def process_conductcommerce_results(self, card_name: str, listings: List[Dict]) -> Dict:
        """Process ConductCommerce style results (Laughing Dragon MTG)"""
        all_variants = []
        
        # Collect all available variants across all listings
        for listing in listings:
            variants = listing.get('variants', [])
            
            for variant in variants:
                quantity = variant.get('quantity', 0)
                price = variant.get('price', 0.0)
                
                # Only include variants with quantity > 0
                if quantity > 0:
                    all_variants.append({
                        'price': price,
                        'quantity': quantity
                    })
        
        # Consolidate results for this card
        if all_variants:
            # Sort by price to get lowest price
            all_variants.sort(key=lambda x: x['price'])
            lowest_price = all_variants[0]['price']
            total_quantity = sum(variant['quantity'] for variant in all_variants)
            
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
        
        # Handle different store types
        if store.store_type == 'conductcommerce':
            # For ConductCommerce (Laughing Dragon), all data is in the search response
            result = self.process_conductcommerce_results(card_name, products)
            return result
        else:
            # For TCGPlayer Pro, need separate inventory call
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
            result = self.process_tcgplayer_results(card_name, products, inventory_data)
            return result
    
    def check_card_across_stores(self, card_name: str) -> Dict:
        """Check prices for a single card across all configured stores"""
        print(f"\nChecking prices for '{card_name}' across all stores...")
        
        # Initialize result with card name
        result = {'card_name': card_name}
        store_prices = {}
        
        # Query each store
        for store_key in self.stores.keys():
            try:
                store_result = self.check_card_prices(card_name, store_key)
                price = store_result.get('price', 'n/a')
                availability = store_result.get('availability', 'n/a')
                
                # Add store-specific columns
                result[f'{store_key}_price'] = price
                result[f'{store_key}_availability'] = availability
                
                # Track valid prices for lowest price calculation
                if price != 'n/a' and isinstance(price, (int, float)):
                    store_prices[store_key] = price
                    
            except Exception as e:
                print(f"Error querying {store_key} for '{card_name}': {e}")
                result[f'{store_key}_price'] = 'n/a'
                result[f'{store_key}_availability'] = 'n/a'
        
        # Find lowest price and corresponding store
        if store_prices:
            lowest_store = min(store_prices.keys(), key=lambda k: store_prices[k])
            result['lowest_price'] = store_prices[lowest_store]
            result['lowest_price_store'] = lowest_store
        else:
            result['lowest_price'] = 'n/a'
            result['lowest_price_store'] = 'n/a'
        
        return result
    
    def check_all_cards(self, input_file: str, store_key: str = None) -> List[Dict]:
        """Check prices for all cards in the input file - multi-store results per card"""
        card_names = self.load_card_names(input_file)
        all_results = []
        
        for card_name in card_names:
            try:
                if store_key:
                    # Single store mode (backward compatibility)
                    result = self.check_card_prices(card_name, store_key)
                    all_results.append(result)
                else:
                    # Multi-store mode (default)
                    result = self.check_card_across_stores(card_name)
                    all_results.append(result)
            except Exception as e:
                print(f"Error processing '{card_name}': {e}")
                # Still add an n/a result for this card
                if store_key:
                    # Single store error result
                    all_results.append({
                        'card_name': card_name,
                        'availability': 'n/a',
                        'price': 'n/a',
                        'quantity': 0
                    })
                else:
                    # Multi-store error result
                    error_result = {'card_name': card_name}
                    for store in self.stores.keys():
                        error_result[f'{store}_price'] = 'n/a'
                        error_result[f'{store}_availability'] = 'n/a'
                    error_result['lowest_price'] = 'n/a'
                    error_result['lowest_price_store'] = 'n/a'
                    all_results.append(error_result)
                continue
        
        return all_results
    
    def save_results(self, results: List[Dict], output_file: str):
        """Save results to CSV file"""
        if not results:
            print("No results to save!")
            return
        
        # Dynamically determine fieldnames based on result structure
        if results and 'lowest_price' in results[0]:
            # Multi-store format
            fieldnames = ['card_name']
            # Add store-specific columns
            for store_key in self.stores.keys():
                fieldnames.extend([f'{store_key}_price', f'{store_key}_availability'])
            fieldnames.extend(['lowest_price', 'lowest_price_store'])
        else:
            # Single store format (backward compatibility)
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
        
        # Check if multi-store or single-store format
        if results and 'lowest_price' in results[0]:
            self._print_multi_store_results(results)
        else:
            self._print_single_store_results(results)
    
    def _print_single_store_results(self, results: List[Dict]):
        """Print single-store format results (backward compatibility)"""
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
    
    def _print_multi_store_results(self, results: List[Dict]):
        """Print multi-store format results"""
        # Calculate column widths
        store_keys = list(self.stores.keys())
        card_width = 20
        price_width = 12
        
        # Build header
        header_parts = [f"{'Card Name':<{card_width}}"]
        for store_key in store_keys:
            header_parts.append(f"{store_key:<{price_width}}")
        header_parts.extend([f"{'Lowest Price':<{price_width}}", f"{'Best Store':<{price_width}}"])
        
        total_width = sum([card_width, len(store_keys) * price_width, price_width * 2]) + len(header_parts) - 1
        
        print("\n" + "="*total_width)
        print(" | ".join(header_parts))
        print("="*total_width)
        
        # Track statistics
        total_cards = len(results)
        store_stats = {store: {'available': 0, 'total_price': 0.0} for store in store_keys}
        overall_lowest_total = 0.0
        
        for result in results:
            card_name = result['card_name'][:card_width-1]
            row_parts = [f"{card_name:<{card_width}}"]
            
            # Add store prices
            for store_key in store_keys:
                price = result.get(f'{store_key}_price', 'n/a')
                availability = result.get(f'{store_key}_availability', 'n/a')
                
                if price == 'n/a':
                    price_display = 'n/a'
                else:
                    price_display = f"${price:.2f}"
                    if availability == 'Available':
                        store_stats[store_key]['available'] += 1
                        store_stats[store_key]['total_price'] += price
                
                row_parts.append(f"{price_display:<{price_width}}")
            
            # Add lowest price and store
            lowest_price = result.get('lowest_price', 'n/a')
            lowest_store = result.get('lowest_price_store', 'n/a')
            
            if lowest_price == 'n/a':
                lowest_display = 'n/a'
            else:
                lowest_display = f"${lowest_price:.2f}"
                overall_lowest_total += lowest_price
            
            row_parts.extend([f"{lowest_display:<{price_width}}", f"{lowest_store:<{price_width}}"])
            
            print(" | ".join(row_parts))
        
        print("="*total_width)
        
        # Print summary
        print("\n📊 MULTI-STORE SUMMARY:")
        print(f"Total cards: {total_cards}")
        print("\nPer-Store Statistics:")
        for store_key in store_keys:
            store_name = self.stores[store_key].name
            available = store_stats[store_key]['available']
            total_price = store_stats[store_key]['total_price']
            print(f"  {store_name}: {available} available, ${total_price:.2f} total")
        
        print(f"\nOverall lowest total: ${overall_lowest_total:.2f}")
        print("="*total_width)


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
        default=None,
        help='Store to check prices at (if not specified, queries all configured stores)'
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
    
    if args.store:
        print(f"Store: {args.store}")
    else:
        print("Mode: All configured stores")
        print(f"Configured stores: {', '.join(checker.stores.keys())}")
    
    results = checker.check_all_cards(args.input, args.store)
    
    # Output results
    checker.print_results(results)
    
    if not args.print_only:
        checker.save_results(results, args.output)


if __name__ == '__main__':
    main()
