# Exchange Logos

This directory contains the logos for different cryptocurrency exchanges used in receipt generation.

## Requirements
- All logos should be in PNG format
- Recommended size: 200x200 pixels
- Transparent background preferred
- File naming: `logo.png` in each exchange's directory

## Directory Structure
```
exchanges/
├── binance/
│   └── logo.png
├── coinbase/
│   └── logo.png
└── kraken/
    └── logo.png
```

## Adding New Exchanges
1. Create a new directory with the exchange name in lowercase
2. Add a `logo.png` file following the requirements above
3. Create corresponding receipt templates in `templates/receipts/exchanges/[exchange_name]/`
