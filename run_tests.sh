#!/bin/bash

# Terminal colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display help message
show_help() {
    echo -e "${BLUE}Document Search & Q&A Platform Test Runner${NC}"
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help             Show this help message"
    echo "  -a, --all              Run all tests"
    echo "  -u, --unit             Run unit tests"
    echo "  -e, --e2e              Run end-to-end tests"
    echo "  -l, --load             Run load tests"
    echo "  -s, --stress           Run stress tests"
    echo "  -p, --performance      Run performance benchmarks"
    echo "  -c, --coverage         Generate coverage report"
    echo "  -v, --verbose          Increase verbosity"
    echo
    echo "Examples:"
    echo "  $0 --all               Run all tests and generate coverage report"
    echo "  $0 --e2e --verbose     Run end-to-end tests with verbose output"
    echo "  $0 --load              Run load tests only"
}

# Default options
RUN_UNIT=false
RUN_E2E=false
RUN_LOAD=false
RUN_STRESS=false
RUN_PERF=false
GENERATE_COVERAGE=false
VERBOSE=false

# Parse command line arguments
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -a|--all)
            RUN_UNIT=true
            RUN_E2E=true
            RUN_LOAD=true
            RUN_STRESS=true
            RUN_PERF=true
            GENERATE_COVERAGE=true
            shift
            ;;
        -u|--unit)
            RUN_UNIT=true
            shift
            ;;
        -e|--e2e)
            RUN_E2E=true
            shift
            ;;
        -l|--load)
            RUN_LOAD=true
            shift
            ;;
        -s|--stress)
            RUN_STRESS=true
            shift
            ;;
        -p|--performance)
            RUN_PERF=true
            shift
            ;;
        -c|--coverage)
            GENERATE_COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Setup virtual environment and install dependencies if not already done
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Setting up virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Ensure test directories exist
mkdir -p data/uploads
mkdir -p data/chroma_db

# Add MongoDB check and fallback if needed
echo -e "${YELLOW}Checking MongoDB connection...${NC}"
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000); client.admin.command('ping')" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}MongoDB not detected. Tests will use mocked database.${NC}"
    # Set an environment variable to indicate mock mode
    export USE_MOCK_DB=true
fi

# Function to run a command and check its status
run_command() {
    echo -e "${YELLOW}Running: $1${NC}"
    if [ "$VERBOSE" = true ]; then
        eval $1
    else
        eval $1 > /dev/null 2>&1
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Passed${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        return 1
    fi
}

# Run unit tests
if [ "$RUN_UNIT" = true ]; then
    echo -e "\n${BLUE}=== Running Unit Tests ===${NC}"
    if [ "$GENERATE_COVERAGE" = true ]; then
        UNIT_CMD="python -m pytest app/tests/test_unit.py -v --cov=app --cov-report=term"
    else
        UNIT_CMD="python -m pytest app/tests/test_unit.py -v"
    fi
    run_command "$UNIT_CMD"
    UNIT_STATUS=$?
fi

# Run end-to-end tests
if [ "$RUN_E2E" = true ]; then
    echo -e "\n${BLUE}=== Running End-to-End Tests ===${NC}"
    if [ "$GENERATE_COVERAGE" = true ]; then
        E2E_CMD="python -m pytest app/tests/test_api.py -v --cov=app --cov-report=term --cov-append"
    else
        E2E_CMD="python -m pytest app/tests/test_api.py -v"
    fi
    run_command "$E2E_CMD"
    E2E_STATUS=$?
fi

# Run load tests
if [ "$RUN_LOAD" = true ]; then
    echo -e "\n${BLUE}=== Running Load Tests ===${NC}"
    
    # Start the application server in the background
    echo -e "${YELLOW}Starting application server...${NC}"
    python -m app.main > /dev/null 2>&1 &
    APP_PID=$!
    
    # Wait for the server to start
    echo -e "${YELLOW}Waiting for server to start...${NC}"
    sleep 5
    
    # Run Locust load tests in headless mode
    echo -e "${YELLOW}Running load tests...${NC}"
    LOCUST_CMD="locust -f app/tests/locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 2 --run-time 30s --headless --only-summary"
    run_command "$LOCUST_CMD"
    LOAD_STATUS=$?
    
    # Stop the application server
    echo -e "${YELLOW}Stopping application server...${NC}"
    kill $APP_PID
    wait $APP_PID 2>/dev/null
fi

# Run stress tests
if [ "$RUN_STRESS" = true ]; then
    echo -e "\n${BLUE}=== Running Stress Tests ===${NC}"
    
    # Start the application server in the background
    echo -e "${YELLOW}Starting application server...${NC}"
    python -m app.main > /dev/null 2>&1 &
    APP_PID=$!
    
    # Wait for the server to start
    echo -e "${YELLOW}Waiting for server to start...${NC}"
    sleep 5
    
    # Run Locust stress tests with custom shape
    echo -e "${YELLOW}Running stress tests...${NC}"
    STRESS_CMD="locust -f app/tests/locustfile.py --host=http://localhost:8000 --headless --run-time 1m --only-summary -u 50 -r 10 --class-picker StressTest"
    run_command "$STRESS_CMD"
    STRESS_STATUS=$?
    
    # Run Locust spike tests with custom shape
    echo -e "${YELLOW}Running spike tests...${NC}"
    SPIKE_CMD="locust -f app/tests/locustfile.py --host=http://localhost:8000 --headless --run-time 1m --only-summary -u 50 -r 10 --class-picker SpikeTest"
    run_command "$SPIKE_CMD"
    SPIKE_STATUS=$?
    
    # Stop the application server
    echo -e "${YELLOW}Stopping application server...${NC}"
    kill $APP_PID
    wait $APP_PID 2>/dev/null
fi

# Run performance benchmarks
if [ "$RUN_PERF" = true ]; then
    echo -e "\n${BLUE}=== Running Performance Benchmarks ===${NC}"
    
    # Start the application server in the background
    echo -e "${YELLOW}Starting application server...${NC}"
    python -m app.main > /dev/null 2>&1 &
    APP_PID=$!
    
    # Wait for the server to start
    echo -e "${YELLOW}Waiting for server to start...${NC}"
    sleep 5
    
    # Run performance benchmarks using wrk or similar tool if available
    if command -v wrk &> /dev/null; then
        echo -e "${YELLOW}Running HTTP performance benchmarks...${NC}"
        
        # Test health check endpoint (should be fastest)
        echo -e "${YELLOW}Testing health endpoint...${NC}"
        run_command "wrk -t2 -c10 -d10s http://localhost:8000/"
        
        # Test documents list endpoint
        echo -e "${YELLOW}Testing documents endpoint...${NC}"
        run_command "wrk -t2 -c10 -d10s http://localhost:8000/api/documents"
        
        # Test metrics endpoint
        echo -e "${YELLOW}Testing metrics endpoint...${NC}"
        run_command "wrk -t2 -c10 -d10s http://localhost:8000/api/metrics/summary"
    else
        echo -e "${YELLOW}wrk not found, skipping HTTP benchmarks${NC}"
    fi
    
    # Stop the application server
    echo -e "${YELLOW}Stopping application server...${NC}"
    kill $APP_PID
    wait $APP_PID 2>/dev/null
fi

# Generate coverage report if needed
if [ "$GENERATE_COVERAGE" = true ]; then
    echo -e "\n${BLUE}=== Generating Coverage Report ===${NC}"
    
    # Generate HTML coverage report
    run_command "coverage html"
    
    # Report location
    echo -e "${GREEN}Coverage report generated at: htmlcov/index.html${NC}"
fi

# Final summary
echo -e "\n${BLUE}=== Test Summary ===${NC}"

if [ "$RUN_UNIT" = true ]; then
    if [ $UNIT_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ Unit Tests: PASSED${NC}"
    else
        echo -e "${RED}✗ Unit Tests: FAILED${NC}"
    fi
fi

if [ "$RUN_E2E" = true ]; then
    if [ $E2E_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ End-to-End Tests: PASSED${NC}"
    else
        echo -e "${RED}✗ End-to-End Tests: FAILED${NC}"
    fi
fi

if [ "$RUN_LOAD" = true ]; then
    if [ $LOAD_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ Load Tests: PASSED${NC}"
    else
        echo -e "${RED}✗ Load Tests: FAILED${NC}"
    fi
fi

if [ "$RUN_STRESS" = true ]; then
    if [ $STRESS_STATUS -eq 0 ] && [ $SPIKE_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ Stress Tests: PASSED${NC}"
    else
        echo -e "${RED}✗ Stress Tests: FAILED${NC}"
    fi
fi

# Display overall result
if [ "$RUN_UNIT" = true ] || [ "$RUN_E2E" = true ] || [ "$RUN_LOAD" = true ] || [ "$RUN_STRESS" = true ]; then
    if [ "$RUN_UNIT" = true ] && [ $UNIT_STATUS -ne 0 ]; then
        echo -e "\n${RED}Some tests failed.${NC}"
        exit 1
    elif [ "$RUN_E2E" = true ] && [ $E2E_STATUS -ne 0 ]; then
        echo -e "\n${RED}Some tests failed.${NC}"
        exit 1
    elif [ "$RUN_LOAD" = true ] && [ $LOAD_STATUS -ne 0 ]; then
        echo -e "\n${RED}Some tests failed.${NC}"
        exit 1
    elif [ "$RUN_STRESS" = true ] && ([ $STRESS_STATUS -ne 0 ] || [ $SPIKE_STATUS -ne 0 ]); then
        echo -e "\n${RED}Some tests failed.${NC}"
        exit 1
    else
        echo -e "\n${GREEN}All tests passed successfully!${NC}"
        exit 0
    fi
else
    echo -e "\n${YELLOW}No tests were run.${NC}"
    exit 0
fi
