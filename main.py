# OptimusPC - Main Application Entry Point

import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.optimizer import OptimusOptimizer
from src.gui.main_window import OptimusGUI
from src.utils.logger import setup_logger
from src.config.settings import Config

def main():
    """Main application entry point"""
    
    # Setup logging
    logger = setup_logger()
    logger.info("Starting OptimusPC...")
    
    try:
        # Load configuration
        config = Config()
        
        # Initialize optimizer
        optimizer = OptimusOptimizer(config)
        
        # Check if running in GUI mode or CLI mode
        if len(sys.argv) > 1 and sys.argv[1] == '--cli':
            # CLI mode
            from src.cli.main import run_cli
            run_cli(optimizer)
        else:
            # GUI mode (default)
            app = OptimusGUI(optimizer)
            app.run()
            
    except Exception as e:
        logger.error(f"Failed to start OptimusPC: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
