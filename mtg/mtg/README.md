# MTG Card Price and Availability Checker

This Python script checks MTG card availability and prices from configurable MTG store websites. It follows a two-step process: first searching for cards, then retrieving inventory and pricing information.

## Features

- ✅ **Configurable Store Support**: Easily add multiple MTG store APIs via JSON configuration
- ✅ **Multiple Store Types**: Supports TCGPlayer Pro and Conduct Commerce (Laughing Dragon MTG) APIs
- ✅ **Flexible API Patterns**: Handles both two-step (search + inventory) and single-endpoint workflows
- ✅ **Batch Processing**: Process multiple cards from a text file
- ✅ **One Row Per Card**: Consolidates all variants into a single result per card
- ✅ **Lowest Price**: Shows the lowest available price across all variants
- ✅ **CSV Output**: Results saved in CSV format with 4 columns: card name, availability, price, quantity
- ✅ **Console Display**: Formatted table output with summary statistics
- ✅ **Unavailable Cards**: Shows "n/a" for cards not found or out of stock
- ✅ **Summary Statistics**: Total cards, available cards, and total price
- ✅ **Error Handling**: Robust error handling for API failures

## Files Structure

```
mtg/
├── mtg_price_checker.py    # Main script
├── config.json             # Store configuration
├── cards.txt               # Input file (card names, one per line)
├── results.csv             # Output file (generated)
└── README.md               # This documentation
```

## Configuration

The `config.json` file defines store configurations and output settings:

```json
{
  "stores": {
    "tcgplayer_pro": {
      "name": "TCGPlayer Pro",
      "search_url": "https://elegantoctopus.tcgplayerpro.com/api/catalog/search",
      "inventory_url": "https://elegantoctopus.tcgplayerpro.com/api/inventory/skus",
      "headers": {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      "search_payload": {
        "query": "{card_name}",
        "context": null,
        "filters": {},
        "from": 0,
        "size": 5,
        "sort": [{"field": "in-stock-price-sort", "order": "asc"}]
      }
    }
  },
  "output_settings": {
    "max_results_per_card": 3,
    "sort_by_price": true,
    "min_condition": "Near Mint"
  }
}
```

### Adding New Stores

#### TCGPlayer Pro Style (Two-Step Process)
```json
"elegantoctopus": {
  "name": "elegantoctopus",
  "search_url": "https://elegantoctopus.tcgplayerpro.com/api/catalog/search",
  "inventory_url": "https://elegantoctopus.tcgplayerpro.com/api/inventory/skus",
  "type": "tcgplayer_pro",
  "headers": {
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "search_payload": {
    "query": "{card_name}",
    "context": null,
    "filters": {},
    "from": 0,
    "size": 5,
    "sort": [{"field": "in-stock-price-sort", "order": "asc"}]
  }
}
```

#### Conduct Commerce Style (Single Endpoint)
```json
"laughingdragonmtg": {
  "name": "Laughing Dragon MTG",
  "search_url": "https://api.conductcommerce.com/v1/advancedSearch",
  "type": "conductcommerce",
  "headers": {
    "Accept": "application/json",
    "Content-Type": "application/json"
  },
  "search_payload": {
    "productTypeID": 1,
    "name": "{card_name}",
    "language": ["English"],
    "host": "laughingdragonmtg.com"
  }
}
```

## Usage

### Multi-Store Mode (Default)

```bash
# Check prices across all configured stores (default behavior)
python3 mtg_price_checker.py

# Use a different input file
python3 mtg_price_checker.py --input my_cards.txt

# Only display results, don't save CSV
python3 mtg_price_checker.py --print-only
```

### Single Store Mode (Backward Compatibility)

```bash
# Check prices at a specific store
python3 mtg_price_checker.py --store elegantoctopus

# Check prices at Laughing Dragon MTG
python3 mtg_price_checker.py --store laughingdragonmtg
```

### Command Line Options

```bash
python3 mtg_price_checker.py [options]

Options:
  -i, --input FILE     Input file with card names (default: cards.txt)
  -s, --store STORE    Store to check prices at (default: tcgplayer_pro)
  -o, --output FILE    Output CSV file (default: results.csv)
  -c, --config FILE    Configuration file (default: config.json)
  -p, --print-only     Only print to console, don't save CSV
  -h, --help          Show help message
```

### Input Format

Create a text file with card names, one per line:

```
Blackblade Reforged
Bloodforged Battle-Axe
Sol Ring
Lightning Bolt
```

## Output Format

### Console Output
```
======================================================================
Card Name                      Availability Price      Quantity
======================================================================
Blackblade Reforged            Available    $2.47      6
Bloodforged Battle-Axe         Available    $0.59      1
Brass Squire                   n/a          n/a        0
Fireshrieker                   Available    $0.35      101
======================================================================

📊 SUMMARY:
Total cards: 15
Available cards: 10
Unavailable cards: 5
Total price (lowest available): $15.42
======================================================================
```

### CSV Output
The CSV file contains simplified information (one row per card):

| Column | Description |
|--------|-------------|
| card_name | Original card name from input |
| availability | "Available" or "n/a" |
| price | Lowest price in USD, or "n/a" if not available |
| quantity | Total quantity available across all variants |

## API Workflow

The script follows the exact API workflow you specified:

### Step 1: Search for Cards
```bash
curl -sS -X POST 'https://elegantoctopus.tcgplayerpro.com/api/catalog/search' \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "query": "Sol Ring",
    "context": null,
    "filters": {},
    "from": 0,
    "size": 5,
    "sort": [{"field": "in-stock-price-sort", "order": "asc"}]
  }'
```

### Step 2: Get Inventory and Pricing
```bash
curl 'https://elegantoctopus.tcgplayerpro.com/api/inventory/skus?productIds=539393,624049,236137'
```

### Step 3: Process Results
- Extract product IDs from search results
- Query inventory API with product IDs
- Process availability (quantity > 0 = "Available")
- Extract pricing information
- Show lowest price and total quantity per card
- Display "n/a" for unavailable cards

## Example Run

```bash
$ python3 mtg_price_checker.py --input cards.txt --print-only

Starting MTG price check...
Input file: cards.txt
Store: tcgplayer_pro
Loaded 15 card names from 'cards.txt'

Checking prices for 'Blackblade Reforged' at TCGPlayer Pro...
Found 5 products for 'Blackblade Reforged'
Retrieved inventory for 5 products

[... processing continues ...]

======================================================================
Card Name                      Availability Price      Quantity
======================================================================
Blackblade Reforged            Available    $2.47      6
Bloodforged Battle-Axe         Available    $0.59      1
Fireshrieker                   Available    $0.35      101
======================================================================

📊 SUMMARY:
Total cards: 15
Available cards: 10
Unavailable cards: 5
Total price (lowest available): $15.42
======================================================================
```

## Requirements

- Python 3.6+
- `requests` library (`pip install requests`)

## Error Handling

The script includes comprehensive error handling:
- Network timeouts and connection errors
- Invalid JSON responses
- Missing configuration files
- API rate limiting
- Invalid card names

## Notes

- The script respects API rate limits and includes timeouts
- Results show lowest price per card across all variants
- One row per card with consolidated data
- Unavailable cards marked with "n/a"
- Summary statistics included in output
- All data is real - no mocked data is used

## Troubleshooting

1. **No results for a card**: The card might not be available in the store's inventory
2. **Network errors**: Check your internet connection and API endpoints
3. **SSL warnings**: These are non-critical urllib3 warnings and don't affect functionality
4. **Empty CSV**: Ensure your input file contains valid card names

## Adding More Stores

To add support for additional MTG stores:

1. Add store configuration to `config.json`
2. Ensure the store's API follows a similar pattern (search → inventory)
3. Adjust URL parameters and payload structure as needed
4. Test with a few cards before running large batches

The script is designed to be easily extensible for multiple MTG store APIs.
