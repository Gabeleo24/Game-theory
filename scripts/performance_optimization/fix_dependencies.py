#!/usr/bin/env python3
"""
Dependency Fix Script for ADS599 Capstone Soccer Intelligence System
Fixes common dependency issues including Keras/TensorFlow compatibility.
"""

import subprocess
import sys
import logging
from pathlib import Path


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def run_command(command, description):
    """Run a command and log the result."""
    logger = logging.getLogger(__name__)
    logger.info(f"Running: {description}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ {description} failed: {e}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        return False


def fix_keras_tensorflow_issue():
    """Fix Keras/TensorFlow compatibility issue."""
    logger = logging.getLogger(__name__)
    logger.info("Fixing Keras/TensorFlow compatibility issue...")
    
    commands = [
        ("pip uninstall -y keras tensorflow", "Uninstalling conflicting Keras/TensorFlow"),
        ("pip install tensorflow==2.13.0", "Installing compatible TensorFlow"),
        ("pip install tf-keras", "Installing tf-keras for compatibility"),
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
    
    return success


def update_requirements():
    """Update requirements.txt with compatible versions."""
    logger = logging.getLogger(__name__)
    logger.info("Updating requirements.txt with compatible versions...")
    
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / 'requirements.txt'
    
    # Read current requirements
    try:
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        logger.error("requirements.txt not found")
        return False
    
    # Update problematic packages
    updated_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('tensorflow'):
            updated_lines.append('tensorflow==2.13.0\n')
        elif line.startswith('keras'):
            updated_lines.append('tf-keras>=2.13.0\n')
        elif line.startswith('transformers'):
            updated_lines.append('transformers>=4.21.0,<4.30.0\n')
        elif line.startswith('sentence-transformers'):
            updated_lines.append('sentence-transformers>=2.2.0,<2.3.0\n')
        else:
            updated_lines.append(line + '\n' if not line.endswith('\n') else line)
    
    # Write updated requirements
    try:
        with open(requirements_file, 'w') as f:
            f.writelines(updated_lines)
        logger.info("✓ requirements.txt updated with compatible versions")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to update requirements.txt: {e}")
        return False


def install_performance_dependencies():
    """Install additional performance dependencies."""
    logger = logging.getLogger(__name__)
    logger.info("Installing performance dependencies...")
    
    performance_packages = [
        "numba>=0.57.0",
        "psutil>=5.9.0",
        "lz4>=4.0.0",
        "joblib>=1.3.0",
        "redis>=4.5.0",
        "docker>=6.0.0",
    ]
    
    success = True
    for package in performance_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            success = False
    
    return success


def create_minimal_requirements():
    """Create minimal requirements file for performance optimization."""
    logger = logging.getLogger(__name__)
    logger.info("Creating minimal requirements for performance optimization...")
    
    project_root = Path(__file__).parent.parent
    minimal_requirements_file = project_root / 'requirements_minimal.txt'
    
    minimal_requirements = """# Minimal requirements for performance optimization
# Core dependencies
pandas>=1.5.0
numpy>=1.24.0
scikit-learn>=1.3.0

# Performance dependencies
numba>=0.57.0
psutil>=5.9.0
lz4>=4.0.0
joblib>=1.3.0

# Caching and database
redis>=4.5.0

# Docker integration
docker>=6.0.0

# Configuration and utilities
python-dotenv>=1.0.0
pyyaml>=6.0
tqdm>=4.65.0

# Compatible ML/AI packages (optional)
tensorflow==2.13.0
tf-keras>=2.13.0
transformers>=4.21.0,<4.30.0
sentence-transformers>=2.2.0,<2.3.0
"""
    
    try:
        with open(minimal_requirements_file, 'w') as f:
            f.write(minimal_requirements)
        logger.info(f"✓ Minimal requirements created: {minimal_requirements_file}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to create minimal requirements: {e}")
        return False


def main():
    """Main function to fix dependencies."""
    logger = setup_logging()
    logger.info("Starting dependency fix process...")
    
    steps = [
        ("Fixing Keras/TensorFlow compatibility", fix_keras_tensorflow_issue),
        ("Updating requirements.txt", update_requirements),
        ("Installing performance dependencies", install_performance_dependencies),
        ("Creating minimal requirements", create_minimal_requirements),
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        try:
            if step_function():
                logger.info(f"✓ {step_name} completed")
            else:
                failed_steps.append(step_name)
                logger.error(f"✗ {step_name} failed")
        except Exception as e:
            failed_steps.append(step_name)
            logger.error(f"✗ {step_name} failed with exception: {e}")
    
    if failed_steps:
        logger.warning(f"Some steps failed: {', '.join(failed_steps)}")
        logger.info("You can try running the performance optimization with minimal dependencies")
        logger.info("Use: pip install -r requirements_minimal.txt")
    else:
        logger.info("✓ All dependency fixes completed successfully")
        logger.info("You can now run the performance optimization script")
    
    # Provide next steps
    logger.info("\nNext steps:")
    logger.info("1. Start Docker Desktop if not already running")
    logger.info("2. Run: python scripts/setup_performance_optimization.py")
    logger.info("3. Or manually start containers: docker-compose --profile production up -d")
    
    return len(failed_steps) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
