# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Machine learning optimization
- Multi-timeframe analysis
- Portfolio management
- Mobile app (React Native)
- Cloud deployment
- Advanced risk management

## [1.0.0] - 2024-12-15

### Added
- **Core Strategy**: 9-15 EMA crossover with confirmations
- **Multi-Broker Support**:
  - Angel One integration for stocks
  - Zerodha integration for stocks
  - Mudrex integration for crypto
- **Trading Modes**:
  - Live trading (stocks & crypto)
  - Paper trading simulator
  - Backtesting engine
- **Web Dashboard**: Streamlit-based interface
- **Database System**: SQLite for trade tracking
- **Risk Management**:
  - Auto position sizing
  - Stop-loss management
  - Risk-reward ratio (1:2)
- **Analytics**:
  - Performance metrics
  - Equity curves
  - Drawdown charts
  - Win rate tracking
- **Documentation**:
  - Setup guide
  - Git workflow guide
  - Claude Code integration guide
  - Contributing guide
- **DevOps**:
  - Docker support
  - Docker Compose
  - GitHub Actions CI/CD
  - Automated setup scripts

### Technical Indicators
- Exponential Moving Averages (9, 15)
- Relative Strength Index (14)
- MACD (12, 26, 9)
- Volume analysis
- Support/Resistance detection

### Features
- Real-time trade execution
- Historical data analysis
- Trade logging
- Performance tracking
- Multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d)
- Configurable parameters
- Email notifications (optional)
- Telegram notifications (optional)

### Security
- API key encryption
- Secure configuration management
- .gitignore for sensitive data
- Config template system

## [0.9.0] - 2024-12-10 (Beta)

### Added
- Basic EMA strategy implementation
- Angel One integration
- Simple backtesting
- Command-line interface

### Fixed
- Position sizing calculation
- Stop-loss placement

## [0.5.0] - 2024-12-01 (Alpha)

### Added
- Initial project setup
- Core strategy logic
- Basic data handling

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2024-12-15 | Full production release |
| 0.9.0 | 2024-12-10 | Beta release |
| 0.5.0 | 2024-12-01 | Alpha release |

---

## How to Update This File

When making changes, add them to the [Unreleased] section at the top using these categories:

### Categories
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes

### Example Entry

```markdown
## [Unreleased]

### Added
- New feature X
- Support for broker Y

### Fixed
- Bug in position sizing
- Error handling in API calls
```

### On Release

1. Move [Unreleased] items to new version section
2. Add release date
3. Create git tag: `git tag -a v1.1.0 -m "Release v1.1.0"`
4. Push tag: `git push --tags`

---

**Note**: For detailed changes, see the [commit history](https://github.com/YOUR_USERNAME/ema-trading-bot/commits/main).
