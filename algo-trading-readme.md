# Automated Options Trading Bot Using TD Sequential Strategy

## Overview
This project implements an automated options trading bot that uses a modified version of Tom DeMark's TD Sequential strategy. The bot interfaces with the Shoonya broker platform to execute trades automatically in the Indian markets, specifically focusing on NIFTY options.

## Key Features
- Real-time market data processing using Fyers API
- Three distinct trading strategies based on TD Sequential:
  - TD Support & Resistance (TDSR)
  - TD Breakout (TDBO)
  - TD Reversal (TDR)
- Automated options contract selection
- Dynamic stop-loss and target management
- Break-even protection mechanism
- Risk management with adjustable parameters
- Comprehensive logging system

## Technology Stack
- Python 3.x
- Fyers API v3 for market data
- Shoonya API for order execution
- Pandas for data manipulation
- Custom technical analysis modules

## Architecture
The project is structured around the `TradingStrategy` class which manages:
1. Market data processing
2. Strategy execution
3. Order management
4. Position tracking
5. Risk management

### Core Components
- **TD Setup**: Base TD Sequential calculations
- **TD Breakout**: Breakout detection and signal generation
- **TD Reversal**: Reversal pattern identification
- **TD Support/Resistance**: Dynamic level calculation
- **Order Management**: Integration with Shoonya broker
- **Risk Management**: Stop-loss and position sizing

## Configuration Parameters
```python
self.MULTIPLAYER = 0.8        # Risk multiplier
self.RISK_TO_REWARD = 10      # Risk:Reward ratio
self.BREAK_EVEN_POINT = 0.3   # Break-even trigger point
self.LOT_SIZE = 25           # Standard lot size
self.MAX_LOSS_CAP = 10       # Maximum loss limit
```

## Features
### Automated Trade Management
- Dynamic strike price selection
- Automatic stop-loss adjustment
- Break-even protection
- Target booking
- Position tracking

### Risk Management
- ATR-based stop-loss calculation
- Maximum loss caps
- Break-even triggers
- Multiple take-profit levels
- Position sizing rules

### Market Analysis
- Real-time data processing
- Multiple timeframe analysis
- Support/Resistance identification
- Trend direction confirmation
- Volume analysis

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/td-sequential-trading-bot.git
cd td-sequential-trading-bot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure API credentials
```bash
# Create credentials file
cp config.example.py config.py
# Edit with your broker credentials
vim config.py
```

## Usage

1. Set up your broker credentials in the configuration file
2. Adjust risk parameters if needed
3. Run the main script:
```bash
python main.py
```

## Strategy Details

### TD Support & Resistance (TDSR)
- Identifies key support and resistance levels using TD Sequential
- Generates trade signals on level breaks
- Incorporates momentum confirmation

### TD Breakout (TDBO)
- Detects breakout patterns in price action
- Uses volume confirmation
- Implements time-based filters

### TD Reversal (TDR)
- Identifies potential reversal points
- Uses TD Sequential setup counts
- Incorporates price action confirmation

## Safety Features
- Automatic session disconnection at market close
- Error handling and reconnection logic
- Position verification system
- Order execution confirmation
- Risk limit enforcement

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
This software is for educational purposes only. Use at your own risk. The author and contributors are not responsible for any financial losses incurred through the use of this software.

## Contact
For internship inquiries or questions about the project, please reach out through:
- LinkedIn: [Your LinkedIn]
- Email: [Your Email]
- GitHub: [Your GitHub]

