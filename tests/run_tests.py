#!/usr/bin/env python
"""
Test runner script to help debug test failures
Run with: python run_tests.py
"""

import sys
import subprocess
import os
import pytest
import coverage
from datetime import datetime

def run_tests(args=None):
    """Run tests with coverage reporting."""
    # Start coverage
    cov = coverage.Coverage(
        branch=True,
        source=['models', 'utils', 'routes'],
        omit=['*/tests/*', '*/migrations/*']
    )
    cov.start()
    
    # Default arguments if none provided
    if args is None:
        args = [
            '--verbose',
            '--capture=no',
            '--tb=short'
        ]
    
    # Add timestamp to test output
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'test_output_{timestamp}.log'
    
    # Run tests
    try:
        result = pytest.main(args)
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        # Generate coverage reports
        print("\nGenerating coverage reports...")
        cov.html_report(directory='htmlcov')
        cov.xml_report(outfile='coverage.xml')
        
        # Print summary
        print("\nCoverage Summary:")
        cov.report()
        
        return result
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        return 1

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required = ['pytest', 'flask', 'flask_sqlalchemy', 'pymysql']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def setup_test_db():
    """Setup test database."""
    print("\n🗄️  Setting up test database...")
    
    try:
        from app import get_app
        from extensions import db
        from tests.conftest import TestConfig
        
        app = get_app(config=TestConfig)
        
        with app.app_context():
            db.create_all()
            print("✅ Test database created")
            return True
            
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    # Parse command line arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else None
    
    # Add common options if not specified
    if args is None:
        args = [
            '--verbose',
            '--capture=no',
            '--tb=short',
            'tests/'
        ]
    
    # Run tests
    sys.exit(run_tests(args))