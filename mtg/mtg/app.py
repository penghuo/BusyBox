#!/usr/bin/env python3
"""
MTG Card Price Checker Web Application

Flask web server that provides a web interface for the MTG price checker.
Reuses the existing mtg_price_checker.py functionality.
"""

from flask import Flask, render_template, request, jsonify
from mtg_price_checker import MTGPriceChecker
import json
import traceback
from typing import List, Dict, Any

app = Flask(__name__)

# Initialize the MTG price checker
price_checker = MTGPriceChecker()

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/stores')
def get_stores():
    """Get available stores from configuration"""
    try:
        stores = []
        for store_key, store_config in price_checker.stores.items():
            stores.append({
                'key': store_key,
                'name': store_config.name,
                'type': store_config.store_type
            })
        return jsonify({
            'success': True,
            'stores': stores
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/check-prices', methods=['POST'])
def check_prices():
    """Check prices for submitted cards"""
    try:
        data = request.get_json()
        
        # Get card list from request
        card_text = data.get('cards', '').strip()
        if not card_text:
            return jsonify({
                'success': False,
                'error': 'No cards provided'
            }), 400
        
        # Parse card names (one per line)
        card_names = [line.strip() for line in card_text.split('\n') if line.strip()]
        if not card_names:
            return jsonify({
                'success': False,
                'error': 'No valid card names found'
            }), 400
        
        # Get selected stores from request
        selected_stores = data.get('stores', [])
        if not selected_stores:
            return jsonify({
                'success': False,
                'error': 'No stores selected'
            }), 400
        
        # Validate selected stores
        available_stores = set(price_checker.stores.keys())
        invalid_stores = set(selected_stores) - available_stores
        if invalid_stores:
            return jsonify({
                'success': False,
                'error': f'Invalid stores: {", ".join(invalid_stores)}'
            }), 400
        
        # Process cards
        results = []
        store_stats = {store: {'available': 0, 'total_price': 0.0} for store in selected_stores}
        overall_lowest_total = 0.0
        
        for card_name in card_names:
            try:
                if len(selected_stores) == 1:
                    # Single store mode
                    store_key = selected_stores[0]
                    result = price_checker.check_card_prices(card_name, store_key)
                    
                    # Convert to multi-store format for consistency
                    multi_result = {'card_name': card_name}
                    for store in available_stores:
                        if store == store_key:
                            multi_result[f'{store}_price'] = result.get('price', 'n/a')
                            multi_result[f'{store}_availability'] = result.get('availability', 'n/a')
                        else:
                            multi_result[f'{store}_price'] = 'n/a'
                            multi_result[f'{store}_availability'] = 'n/a'
                    
                    price = result.get('price', 'n/a')
                    if price != 'n/a':
                        multi_result['lowest_price'] = price
                        multi_result['lowest_price_store'] = store_key
                    else:
                        multi_result['lowest_price'] = 'n/a'
                        multi_result['lowest_price_store'] = 'n/a'
                    
                    results.append(multi_result)
                    
                else:
                    # Multi-store mode - but only for selected stores
                    result = {'card_name': card_name}
                    store_prices = {}
                    
                    # Query each selected store
                    for store_key in selected_stores:
                        store_result = price_checker.check_card_prices(card_name, store_key)
                        price = store_result.get('price', 'n/a')
                        availability = store_result.get('availability', 'n/a')
                        
                        result[f'{store_key}_price'] = price
                        result[f'{store_key}_availability'] = availability
                        
                        # Track valid prices for lowest price calculation
                        if price != 'n/a' and isinstance(price, (int, float)):
                            store_prices[store_key] = price
                    
                    # Add n/a for unselected stores
                    for store_key in available_stores:
                        if store_key not in selected_stores:
                            result[f'{store_key}_price'] = 'n/a'
                            result[f'{store_key}_availability'] = 'n/a'
                    
                    # Find lowest price among selected stores
                    if store_prices:
                        lowest_store = min(store_prices.keys(), key=lambda k: store_prices[k])
                        result['lowest_price'] = store_prices[lowest_store]
                        result['lowest_price_store'] = lowest_store
                    else:
                        result['lowest_price'] = 'n/a'
                        result['lowest_price_store'] = 'n/a'
                    
                    results.append(result)
                
                # Update statistics for selected stores
                for store_key in selected_stores:
                    price = results[-1].get(f'{store_key}_price', 'n/a')
                    availability = results[-1].get(f'{store_key}_availability', 'n/a')
                    
                    if price != 'n/a' and availability == 'Available':
                        store_stats[store_key]['available'] += 1
                        store_stats[store_key]['total_price'] += price
                
                # Update overall lowest total
                lowest_price = results[-1].get('lowest_price', 'n/a')
                if lowest_price != 'n/a':
                    overall_lowest_total += lowest_price
                    
            except Exception as e:
                print(f"Error processing card '{card_name}': {e}")
                # Add error result
                error_result = {'card_name': card_name}
                for store_key in available_stores:
                    error_result[f'{store_key}_price'] = 'n/a'
                    error_result[f'{store_key}_availability'] = 'n/a'
                error_result['lowest_price'] = 'n/a'
                error_result['lowest_price_store'] = 'n/a'
                results.append(error_result)
        
        # Prepare summary
        summary = {
            'total_cards': len(card_names),
            'store_stats': {},
            'overall_lowest_total': overall_lowest_total
        }
        
        for store_key in selected_stores:
            store_name = price_checker.stores[store_key].name
            summary['store_stats'][store_key] = {
                'name': store_name,
                'available': store_stats[store_key]['available'],
                'total_price': store_stats[store_key]['total_price']
            }
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': summary,
            'selected_stores': selected_stores
        })
        
    except Exception as e:
        print(f"Error in check_prices: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'stores_configured': len(price_checker.stores)
    })

if __name__ == '__main__':
    print("Starting MTG Price Checker Web Application...")
    print("Available at: http://localhost")
    print(f"Configured stores: {list(price_checker.stores.keys())}")
    app.run(host='0.0.0.0', port=80, debug=True)
