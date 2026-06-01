# TestLink Python Client - GUI Test Application

A comprehensive Python desktop application for testing all TestLink/PFS MES commands against actual PFS servers.

## 🎯 Features

- **40+ PFS Procedures**: Complete implementation of all TestLink commands
- **Professional GUI**: Modern desktop interface built with PyQt5
- **Real-time Monitoring**: Live performance graphs and session tracking
- **Multi-Site Support**: Pre-configured for 20+ global manufacturing sites
- **Security**: TLS 1.2 encryption, no hard-coded credentials
- **Comprehensive Testing**: Unit, integration, and E2E test suites
- **Export Capabilities**: Export results to JSON, CSV, Excel

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd testlink-python-client

# Install dependencies
pip install -r requirements.txt

# Run the application
python gui/main.py
```

### Configuration

Edit `config/example_config.json` with your PFS server details:

```json
{
  "server": {
    "host": "pfs-gw-hjp4.corp.bench.com",
    "port": 50000,
    "timeout": 30
  },
  "database": {
    "name": "PFSHJP4"
  }
}
```

## 📚 Documentation

- [Setup Guide](docs/SETUP.md)
- [User Guide](docs/USER_GUIDE.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [API Reference](docs/API_REFERENCE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🏗️ Architecture

```
testlink-python-client/
├── src/                    # Core library
│   ├── testlink_client.py  # Main client
│   ├── protocol.py         # Protocol handling
│   └── procedures/         # PFS procedures
├── gui/                    # GUI application
│   ├── main.py            # Entry point
│   ├── widgets/           # UI components
│   └── dialogs/           # Dialogs
├── test/                   # Test suites
└── config/                 # Configuration files
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration tests only
pytest test/integration/
```

## 📦 Building Standalone Executable

```bash
# Windows
pyinstaller --onefile --windowed gui/main.py

# The executable will be in dist/
```

## 🔒 Security

- All credentials stored in config files (not in code)
- TLS 1.2 encryption for all communications
- Certificate validation (configurable)
- No plain-text password logging

## 📄 License

Proprietary - Benchmark Electronics, Inc.

## 🤝 Contributing

Internal use only. Contact the MES Integration team for questions.

---

**Version:** 1.0.0  
**Last Updated:** June 1, 2026  
**Supported Sites:** 20+ global manufacturing locations
