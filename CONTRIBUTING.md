# Contributing to TestLink Python Client

## Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd testlink-python-client
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run foundation tests:
```bash
python test_foundation.py
```

## Development Workflow

### Branch Strategy
- `master` - Production-ready code
- `develop` - Active development
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `release/*` - Release preparation

### Commit Messages
Follow the format:
```
<type>: <subject>

<body>

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `chore`: Build/tooling changes

### Code Standards
- Follow PEP 8 style guide
- Use type hints where applicable
- Add docstrings to all public functions/classes
- Keep functions focused and small
- Write tests for new features

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest test/unit/
pytest test/integration/
pytest test/e2e/
```

## Adding New PFS Procedures

1. Add method to `src/testlink_client.py` or `src/procedures/`
2. Follow naming convention: `pfs_<procedure_name>`
3. Add docstring with parameters and examples
4. Add unit tests in `test/unit/`
5. Add integration test in `test/integration/`
6. Update API reference documentation

Example:
```python
def pfs_get_defect_codes(
    self,
    user_id: str,
    password: str,
    production_order: Optional[str] = None,
    operation_code: Optional[str] = None
) -> Tuple[ResponseStatus, str, List[str]]:
    """
    Get valid defect codes for current context.
    
    Args:
        user_id: PFS user ID
        password: PFS password
        production_order: Production order (optional)
        operation_code: Operation code (optional)
    
    Returns:
        Tuple of (status, message, defect_codes)
    """
    params = {
        'USER_ID': user_id,
        'PASSWORD': password
    }
    if production_order:
        params['PRODUCTION_ORDER'] = production_order
    if operation_code:
        params['OPERATION_CODE'] = operation_code
    
    return self.send_command('PfsGetDefectCodes', params)
```

## Pull Request Process

1. Create feature branch from `develop`
2. Make changes with tests
3. Ensure all tests pass
4. Update documentation
5. Create pull request with description
6. Address review comments
7. Squash and merge when approved

## Questions?

Contact the MES Integration team.
