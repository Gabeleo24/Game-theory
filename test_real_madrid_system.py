#!/usr/bin/env python3
"""
Real Madrid KPI System Test Script
Quick verification of system components and configuration
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_docker_availability():
    """Test if Docker is available and running."""
    logger.info("🐳 Testing Docker availability...")
    
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Docker available: {result.stdout.strip()}")
            return True
        else:
            logger.error("❌ Docker not available")
            return False
    except Exception as e:
        logger.error(f"❌ Docker test failed: {e}")
        return False

def test_docker_compose():
    """Test if Docker Compose is available."""
    logger.info("🔧 Testing Docker Compose availability...")

    # Try Docker Compose v2 first
    try:
        result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Docker Compose v2 available: {result.stdout.strip()}")
            return True
    except Exception:
        pass

    # Try legacy Docker Compose
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Docker Compose (legacy) available: {result.stdout.strip()}")
            return True
        else:
            logger.error("❌ Docker Compose not available")
            return False
    except Exception as e:
        logger.error(f"❌ Docker Compose test failed: {e}")
        return False

def test_configuration_files():
    """Test if configuration files exist and are valid."""
    logger.info("📋 Testing configuration files...")
    
    config_files = [
        'docker-compose.yml',
        'config/api_keys.yaml',
        'scripts/analysis/real_madrid_kpi_analyzer.py',
        'scripts/algorithms/kpi_algorithm_optimizer.py'
    ]
    
    all_valid = True
    
    for config_file in config_files:
        if os.path.exists(config_file):
            logger.info(f"✅ Found: {config_file}")
        else:
            logger.error(f"❌ Missing: {config_file}")
            all_valid = False
    
    return all_valid

def test_directory_structure():
    """Test if required directories exist."""
    logger.info("📁 Testing directory structure...")
    
    required_dirs = [
        'data/focused',
        'data/real_madrid',
        'data/kpi',
        'data/algorithms',
        'logs/kpi',
        'logs/algorithms',
        'scripts/analysis',
        'scripts/algorithms',
        'config',
        'services'
    ]
    
    all_exist = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            logger.info(f"✅ Directory exists: {directory}")
        else:
            logger.warning(f"⚠️ Creating directory: {directory}")
            os.makedirs(directory, exist_ok=True)
    
    return all_exist

def test_docker_compose_syntax():
    """Test Docker Compose file syntax."""
    logger.info("🔍 Testing Docker Compose syntax...")

    # Try Docker Compose v2 first
    try:
        result = subprocess.run(['docker', 'compose', 'config'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ Docker Compose v2 syntax valid")
            return True
    except Exception:
        pass

    # Try legacy Docker Compose
    try:
        result = subprocess.run(['docker-compose', 'config'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ Docker Compose (legacy) syntax valid")
            return True
        else:
            logger.error(f"❌ Docker Compose syntax error: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Docker Compose syntax test failed: {e}")
        return False

def generate_test_report():
    """Generate a comprehensive test report."""
    logger.info("📊 Generating test report...")
    
    report = {
        'test_timestamp': datetime.now().isoformat(),
        'system_info': {
            'python_version': sys.version,
            'platform': sys.platform
        },
        'tests': {
            'docker_available': test_docker_availability(),
            'docker_compose_available': test_docker_compose(),
            'configuration_files_valid': test_configuration_files(),
            'directory_structure_complete': test_directory_structure(),
            'docker_compose_syntax_valid': test_docker_compose_syntax()
        }
    }
    
    # Calculate overall status
    all_tests_passed = all(report['tests'].values())
    report['overall_status'] = 'PASS' if all_tests_passed else 'FAIL'
    
    # Save report
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"📋 Test report saved: {report_file}")
    
    return report

def main():
    """Main test function."""
    print("\n" + "="*80)
    print("REAL MADRID KPI SYSTEM - SYSTEM TEST")
    print("="*80)
    
    report = generate_test_report()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"Overall Status: {'✅ PASS' if report['overall_status'] == 'PASS' else '❌ FAIL'}")
    
    print(f"\nDetailed Results:")
    for test_name, result in report['tests'].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if report['overall_status'] == 'PASS':
        print(f"\n🚀 System ready! You can now run:")
        print(f"   python start_real_madrid_kpi_system.py start")
        print(f"   python start_real_madrid_kpi_system.py full-analysis")
    else:
        print(f"\n⚠️ Please fix the failing tests before proceeding.")
    
    print("\n" + "="*80)
    
    return 0 if report['overall_status'] == 'PASS' else 1

if __name__ == "__main__":
    sys.exit(main())
