#!/usr/bin/env python3
"""
Development setup script for SQLite-based sales call analytics app.
This script initializes the database and runs migrations.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def main():
    """Main setup function."""
    # Ensure we're in the right directory
    if not Path("app").exists() or not Path("alembic").exists():
        print("Error: This script should be run from the project root directory.")
        sys.exit(1)
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✓ Data directory created/verified: {data_dir.absolute()}")
    
    # Check if conda environment is activated
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if not conda_prefix or not conda_prefix.endswith('conda_env'):
        print("Please activate the conda environment first:")
        print("  conda activate ./conda_env")
        sys.exit(1)
    
    # Install dependencies (should already be installed if using conda setup)
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    print("✓ Dependencies installed")
    
    # Initialize Alembic if not already done
    if not Path("alembic/versions").exists():
        if not run_command("alembic init alembic", "Initializing Alembic"):
            print("Failed to initialize Alembic.")
            sys.exit(1)
        print("✓ Alembic initialized")
    
    # Create initial migration
    if not run_command("alembic revision --autogenerate -m 'Initial migration'", "Creating initial migration"):
        print("Failed to create initial migration.")
        sys.exit(1)
    
    print("✓ Initial migration created")
    
    # Run migrations
    if not run_command("alembic upgrade head", "Running database migrations"):
        print("Failed to run migrations.")
        sys.exit(1)
    
    print("✓ Database migrations completed")
    
    print("\n🎉 Development environment setup complete!")
    print("\nTo start the development server, run:")
    print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nDatabase file location: ./data/sales_analytics.db")


if __name__ == "__main__":
    main()
