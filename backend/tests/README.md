# Park Place API Testing with Schemathesis

## Overview
This directory contains comprehensive API tests using Schemathesis, a property-based testing tool that automatically generates test cases from your OpenAPI schema.

## Test Files

- `test_schemathesis.py` - Main test suite with property-based tests
- `test_cli_schemathesis.py` - CLI runner for advanced Schemathesis features
- `conftest.py` - Pytest fixtures and test configuration

## Running Tests

### Prerequisites
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the API server:
```bash
uvicorn backend.main:app --reload
```

### Run Tests

#### Using pytest (recommended for CI/CD):
```bash
# Run all tests
pytest backend/tests/

# Run only Schemathesis tests
pytest backend/tests/test_schemathesis.py -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html
```

#### Using Schemathesis CLI (for detailed analysis):
```bash
# Basic schema validation
schemathesis run http://localhost:8000/openapi.json --checks all

# Stateful testing (tests API workflows)
schemathesis run http://localhost:8000/openapi.json --stateful links

# Negative testing
schemathesis run http://localhost:8000/openapi.json --checks negative_data_rejection

# Or run the CLI test script
python backend/tests/test_cli_schemathesis.py
```

## Test Coverage

### Property-Based Tests
- **Schema Compliance**: Validates all endpoints against OpenAPI schema
- **Edge Cases**: Tests with extreme/unusual inputs
- **Stateful Testing**: Tests complex workflows (register → login → create space → book)

### Test Categories
1. **Basic Endpoint Tests**: Verify all endpoints respond correctly
2. **Authentication Tests**: User registration, login, token validation
3. **CRUD Operations**: Create, read, update, delete for all resources
4. **Business Logic**: Booking conflicts, authorization, pricing calculations
5. **Negative Tests**: Invalid inputs, unauthorized access, resource conflicts

## Key Features

### Hypothesis Settings
- `max_examples`: Number of test cases per endpoint (default: 10-50)
- `deadline`: Maximum time per test case (milliseconds)
- `suppress_health_check`: Disabled slow test warnings for API tests

### Authentication Handling
Tests automatically handle authentication for protected endpoints using fixtures that:
1. Register a test user
2. Login to get JWT token
3. Include token in request headers

### Database Reset
Each test starts with a clean database state to ensure test isolation.

## Debugging Failed Tests

### View detailed error traces:
```bash
pytest backend/tests/test_schemathesis.py -v --tb=long
```

### Run with Schemathesis replay:
```bash
# Save failing examples
schemathesis run http://localhost:8000/openapi.json --cassette-path=failures.yaml

# Replay failures
schemathesis replay failures.yaml
```

### Check specific endpoint:
```bash
schemathesis run http://localhost:8000/openapi.json --endpoint=/spaces
```

## CI/CD Integration

### GitHub Actions example:
```yaml
- name: Start API server
  run: |
    uvicorn backend.main:app &
    sleep 5  # Wait for server to start

- name: Run Schemathesis tests
  run: pytest backend/tests/test_schemathesis.py
```

## Common Issues

### Server not running
Error: `Connection refused`
Solution: Start the API server with `uvicorn backend.main:app`

### Import errors
Error: `ModuleNotFoundError: No module named 'backend'`
Solution: Run tests from project root directory

### Slow tests
Solution: Reduce `max_examples` in test settings or increase `deadline`

## Advanced Usage

### Custom test strategies:
```python
from hypothesis import strategies as st

@schema.parametrize()
@settings(max_examples=100)
@given(price=st.floats(min_value=0.01, max_value=1000))
def test_price_boundaries(case, price):
    case.body["price_per_hour"] = price
    response = case.call_asgi(app=app)
    case.validate_response(response)
```

### Add custom checks:
```python
def check_response_time(response, case):
    assert response.elapsed.total_seconds() < 1.0

schema.add_check(check_response_time)
```