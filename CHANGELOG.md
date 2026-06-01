# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Implement all 40+ PFS procedures
- PyQt5 GUI application
- Comprehensive test suite
- Documentation with screenshots
- Standalone executables

## [0.1.0] - 2026-06-01

### Added
- Initial project structure
- Core library foundation
  - `TestLinkClient` with TLS 1.2 support
  - `RequestBuilder` for proper message formatting
  - `ResponseParser` for all response types (OK/Warning/Failure/Error)
  - `ConfigManager` with JSON and environment variable support
  - Exception hierarchy for error handling
  - Logging with sensitive data masking
- Multi-site configuration support (Huntsville, Austin, Ayuthaya)
- Foundation tests (all passing)
- Documentation
  - README.md
  - CONTRIBUTING.md
  - Development plan
- Python dependencies manifest (requirements.txt)
- Git repository with .gitignore

### Features
- ✅ TLS 1.2 secure communication
- ✅ Proper CRLF + blank line formatting per PFS protocol
- ✅ Response parsing for all status types
- ✅ Connection retry logic (configurable)
- ✅ Configuration management (JSON files + env vars)
- ✅ Multi-site support with pre-configured sites
- ✅ Comprehensive logging (passwords masked)
- ✅ Full exception handling

### Technical Details
- Python 3.8+ compatible
- Uses `socket` and `ssl` for TLS 1.2 connections
- Pydantic for configuration validation
- Type hints throughout
- Follows PEP 8 style guide

### Tested
- Request building with proper formatting
- Response parsing for all statuses
- Configuration loading from files and dicts
- Site-specific configuration loading
- Client initialization and connection setup

---

## Version History

- **v0.1.0** - Foundation complete (Phase 1)
- **v0.2.0** - All procedures implemented (Phase 2) - *Planned*
- **v0.3.0** - Test suite complete (Phase 3) - *Planned*
- **v0.4.0** - GUI application (Phase 4) - *Planned*
- **v1.0.0** - Production release (Phase 5) - *Planned*
