# Contributing to EMA Trading Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

---

## 🤝 How to Contribute

### 1. Fork the Repository

Click the "Fork" button at the top of this repository.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/ema-trading-bot.git
cd ema-trading-bot
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Make Your Changes

- Write clean, documented code
- Follow the existing code style
- Add tests if applicable
- Update documentation

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: Add your feature description"
```

Use semantic commit messages:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code restructuring
- `perf:` Performance improvements

### 6. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 7. Create Pull Request

1. Go to the original repository
2. Click "New Pull Request"
3. Select your branch
4. Describe your changes
5. Submit!

---

## 📋 Contribution Guidelines

### Code Style

- **Python**: Follow PEP 8
- **Line length**: Max 100 characters
- **Docstrings**: Use Google style
- **Type hints**: Preferred but not required

Example:
```python
def calculate_position_size(entry_price: float, stop_loss: float) -> int:
    """
    Calculate position size based on risk management rules.
    
    Args:
        entry_price: Entry price for the trade
        stop_loss: Stop loss price
        
    Returns:
        Quantity to trade
    """
    # Implementation
    pass
```

### Testing

- Add tests for new features
- Ensure existing tests pass
- Run tests before submitting PR

```bash
python -m pytest
```

### Documentation

- Update README.md if needed
- Add docstrings to new functions
- Update SETUP_GUIDE.md for setup changes
- Include code examples

---

## 🐛 Reporting Bugs

### Before Reporting

- Search existing issues
- Check if it's already fixed
- Try with latest version

### Bug Report Template

```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable.

**Environment:**
- OS: [e.g. Ubuntu 22.04]
- Python version: [e.g. 3.10]
- Bot version: [e.g. v1.0.0]

**Additional context**
Any other information.
```

---

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature.

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should it work?

**Alternatives**
Other solutions you considered.

**Additional Context**
Screenshots, examples, etc.
```

---

## 🎯 Priority Areas

We especially welcome contributions in these areas:

### High Priority
- [ ] Unit tests for all modules
- [ ] Machine learning integration
- [ ] More broker integrations
- [ ] Mobile app (React Native)
- [ ] Advanced risk management

### Medium Priority
- [ ] Multi-timeframe analysis
- [ ] Sentiment analysis integration
- [ ] Advanced order types
- [ ] Portfolio management
- [ ] Performance optimizations

### Low Priority
- [ ] UI/UX improvements
- [ ] More indicators
- [ ] Notification channels
- [ ] Documentation translations
- [ ] Code refactoring

---

## 🏗️ Architecture

### Project Structure

```
trading-bot/
├── main.py                 # Application entry point
├── dashboard.py            # Streamlit dashboard
├── ema_algo_trading.py     # Core strategy
├── angel_one_live_trading.py   # Angel One integration
├── mudrex_crypto_trading.py    # Mudrex integration
├── paper_trading.py        # Paper trading simulator
├── backtest_engine.py      # Backtesting system
└── database_handler.py     # Database operations
```

### Adding New Broker

1. Create `broker_name_trading.py`
2. Implement these methods:
   - `__init__(api_key, api_secret)`
   - `login()`
   - `fetch_historical_data()`
   - `place_order()`
   - `cancel_order()`
   - `get_positions()`
3. Update `main.py` to include new broker
4. Add configuration to `config.ini.example`
5. Update documentation

### Adding New Indicator

1. Add method to `EMAStrategy` class
2. Integrate into `generate_signal()` method
3. Add configuration parameters
4. Update documentation
5. Add tests

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_strategy.py

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

### Writing Tests

```python
import pytest
from ema_algo_trading import EMAStrategy

def test_position_sizing():
    strategy = EMAStrategy(capital=10000, risk_per_trade=0.02)
    quantity = strategy.calculate_position_size(
        entry_price=100,
        stop_loss_price=98
    )
    assert quantity > 0
    assert quantity <= 100  # Max possible with 10k capital
```

---

## 📝 Code Review Process

### What We Look For

1. **Functionality**: Does it work as intended?
2. **Code Quality**: Is it clean and readable?
3. **Tests**: Are there adequate tests?
4. **Documentation**: Is it well documented?
5. **Performance**: Is it efficient?
6. **Security**: Are there security concerns?

### Review Timeline

- Initial review: Within 2-3 days
- Follow-up: As needed
- Merge: After approval and tests pass

---

## 🚀 Release Process

### Version Numbering

We use Semantic Versioning (semver):

- **Major** (v2.0.0): Breaking changes
- **Minor** (v1.1.0): New features, backward compatible
- **Patch** (v1.0.1): Bug fixes

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number bumped
- [ ] Git tag created
- [ ] Release notes written

---

## 🎓 Learning Resources

### For Beginners

- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

### For Trading

- [Technical Analysis](https://www.investopedia.com/technical-analysis-4689657)
- [Risk Management](https://www.investopedia.com/terms/r/riskmanagement.asp)
- [Algorithmic Trading](https://www.investopedia.com/terms/a/algorithmictrading.asp)

### For Python

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 💬 Communication

### Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code contributions

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

---

## ❓ Questions?

If you have questions:

1. Check existing documentation
2. Search closed issues
3. Open a new issue
4. Tag with `question` label

---

**Thank you for contributing!** 🎉

Every contribution, no matter how small, helps make this project better for everyone.
