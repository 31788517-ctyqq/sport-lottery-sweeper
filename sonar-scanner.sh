#!/bin/bash
# SonarScanner wrapper script for local development
# SonarQube扫描器本地开发包装脚本

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SONAR_SCANNER_VERSION="4.8.0.2856"
SONAR_SCANNER_DIR=".sonar/scanner"
SONAR_PROJECT_PROPERTIES="sonar-project.properties"

print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗ $1${NC}"
}

# Check if SonarScanner is installed
check_sonar_scanner() {
    if command -v sonar-scanner &> /dev/null; then
        print_success "SonarScanner is already installed"
        sonar-scanner --version
        return 0
    fi
    return 1
}

# Install SonarScanner
install_sonar_scanner() {
    print_status "Installing SonarScanner..."
    
    # Create directory
    mkdir -p $SONAR_SCANNER_DIR
    cd $SONAR_SCANNER_DIR
    
    # Download and extract
    ARCHIVE_NAME="sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip"
    DOWNLOAD_URL="https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/${ARCHIVE_NAME}"
    
    if command -v wget &> /dev/null; then
        wget -O $ARCHIVE_NAME $DOWNLOAD_URL
    elif command -v curl &> /dev/null; then
        curl -o $ARCHIVE_NAME $DOWNLOAD_URL
    else
        print_error "Neither wget nor curl found. Please install one of them."
        exit 1
    fi
    
    # Extract
    if command -v unzip &> /dev/null; then
        unzip $ARCHIVE_NAME
        mv sonar-scanner-${SONAR_SCANNER_VERSION}-linux sonar-scanner
        rm $ARCHIVE_NAME
    else
        print_error "unzip not found. Please install unzip."
        exit 1
    fi
    
    cd ..
    print_success "SonarScanner installed successfully"
}

# Setup environment
setup_environment() {
    if [ -d "$SONAR_SCANNER_DIR/sonar-scanner" ]; then
        export PATH="$PWD/$SONAR_SCANNER_DIR/sonar-scanner/bin:$PATH"
        print_success "SonarScanner added to PATH"
    fi
}

# Generate coverage reports
generate_coverage_reports() {
    print_status "Generating coverage reports..."
    
    # Backend coverage (Python)
    if [ -d "backend" ]; then
        print_status "Generating Python coverage report..."
        cd backend
        
        # Install coverage tools if not present
        if ! poetry run python -c "import coverage" &>/dev/null; then
            poetry add --dev coverage[toml]
        fi
        
        # Run tests with coverage
        poetry run coverage run -m pytest tests/ -v
        poetry run coverage xml -o coverage.xml
        poetry run coverage html -d htmlcov
        
        cd ..
        print_success "Python coverage report generated"
    fi
    
    # Frontend coverage (JavaScript/TypeScript)
    if [ -d "frontend" ]; then
        print_status "Generating JavaScript/TypeScript coverage report..."
        cd frontend
        
        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            npm ci
        fi
        
        # Run tests with coverage
        npm run test:unit -- --coverage
        
        cd ..
        print_success "JavaScript/TypeScript coverage report generated"
    fi
}

# Run SonarQube analysis
run_analysis() {
    local mode=$1
    
    print_status "Running SonarQube analysis in $mode mode..."
    
    # Check if properties file exists
    if [ ! -f "$SONAR_PROJECT_PROPERTIES" ]; then
        print_warning "sonar-project.properties not found, using defaults"
    fi
    
    # Set analysis parameters based on mode
    case $mode in
        "preview")
            export SONAR_SCANNER_OPTS="-Dsonar.analysis.mode=preview -Dsonar.dryRun=true"
            ;;
        "issues")
            export SONAR_SCANNER_OPTS="-Dsonar.analysis.mode=issues"
            ;;
        *)
            export SONAR_SCANNER_OPTS=""
            ;;
    esac
    
    # Run analysis
    if sonar-scanner $SONAR_SCANNER_OPTS; then
        print_success "SonarQube analysis completed successfully"
        
        if [ "$mode" = "preview" ]; then
            print_status "Preview results available at: http://localhost:9000/dashboard?id=sport-lottery-sweeper"
        else
            print_status "Analysis results available at: ${SONAR_HOST_URL:-http://localhost:9000}/dashboard?id=sport-lottery-sweeper"
        fi
    else
        print_error "SonarQube analysis failed"
        exit 1
    fi
}

# Display usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  install          Install SonarScanner locally"
    echo "  analyze [MODE]   Run SonarQube analysis (default: normal)"
    echo "                  Modes: normal, preview, issues"
    echo "  coverage         Generate coverage reports"
    echo "  setup            Setup environment and install scanner"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup         # Install and setup SonarScanner"
    echo "  $0 coverage      # Generate coverage reports"
    echo "  $0 analyze       # Run normal analysis"
    echo "  $0 analyze preview # Run preview analysis (dry-run)"
}

# Main execution
main() {
    local command=${1:-help}
    local mode=${2:-normal}
    
    case $command in
        "install")
            if ! check_sonar_scanner; then
                install_sonar_scanner
            fi
            ;;
        "setup")
            setup_environment
            if ! check_sonar_scanner; then
                install_sonar_scanner
                setup_environment
            fi
            ;;
        "coverage")
            generate_coverage_reports
            ;;
        "analyze")
            setup_environment
            
            # Check if scanner is available
            if ! check_sonar_scanner; then
                print_error "SonarScanner not found. Run '$0 setup' first."
                exit 1
            fi
            
            # Generate coverage reports
            generate_coverage_reports
            
            # Run analysis
            run_analysis $mode
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Handle script interruption
trap 'print_warning "Analysis interrupted"; exit 130' INT TERM

# Run main function
main "$@"