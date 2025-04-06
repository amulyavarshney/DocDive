# Test Suite for Document Search & Q&A Platform

This directory contains various tests for the backend API:

- **E2E Tests**: End-to-end tests that verify the API functionality
- **Load Tests**: Performance tests using Locust to simulate user load

## Prerequisites

All dependencies are already included in the main `requirements.txt` file:

- pytest (for E2E tests)
- httpx (for HTTP requests in tests)
- locust (for load testing)
- reportlab (optional, for generating test PDF documents)

## Running Tests

You can use the provided `run_tests.py` script to execute both E2E and load tests:

### E2E Tests

Run the end-to-end tests to verify API functionality:

```bash
python tests/run_tests.py e2e
```

To generate a coverage report:

```bash
python tests/run_tests.py e2e --coverage
```

### Load Tests

Run load tests using Locust:

```bash
python tests/run_tests.py load
```

This will start the Locust web UI at http://localhost:8089, where you can configure and run the load test.

To run load tests in headless mode:

```bash
python tests/run_tests.py load --headless --users 50 --spawn-rate 10 --run-time 1m
```

### Run All Tests

Run both E2E and load tests in sequence:

```bash
python tests/run_tests.py all
```

By default, load tests will only run if E2E tests pass. To force load tests to run regardless of E2E test results:

```bash
python tests/run_tests.py all --force
```

## Test Structure

### E2E Tests

The E2E tests verify:

1. Document upload, retrieval, and deletion
2. Query execution and retrieval
3. Metrics endpoints functionality
4. System diagnostics and health checks

### Load Tests

The load tests simulate:

1. **DocumentSearchUser**: A user who uploads documents, makes queries, and browses the system
2. **HighVolumeQueryUser**: A user who only makes queries in rapid succession to stress test the query endpoint

## Configuration

You can customize test execution with the following options:

- `--host`: Host to test (default: localhost)
- `--port`: Port to test (default: 8000)
- `--users`: Number of users to simulate in load tests (default: 50)
- `--spawn-rate`: Rate of user spawning in load tests (default: 10)
- `--run-time`: Test duration for headless mode (default: 1m)

## Adding New Tests

- Add new E2E tests to the `tests/e2e/` directory
- Add new load test user classes to `tests/load_tests/locustfile.py` 