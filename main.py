# OptimusPC - Main Application Entry Point

import argparse
import sys
import os
import logging

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.optimizer import OptimusOptimizer
from src.gui.main_window import OptimusGUI
from src.utils.logger import setup_logger
from src.config.settings import Config

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OptimusPC entry point")
    parser.add_argument("--cli", action="store_true", help="Launch the CLI instead of the GUI")
    parser.add_argument("--modern-ui", action="store_true", help="Launch the PySide6 modern dashboard")
    return parser


def main():
    """Main application entry point"""

    logger = setup_logger()
    logger.info("Starting OptimusPC...")
    args = build_parser().parse_args()

    try:
        config = Config()
        optimizer = OptimusOptimizer(config)

        if args.cli:
            from src.cli.main import run_cli

            run_cli(optimizer)
        elif args.modern_ui:
            from src.gui.pyside_dashboard import launch_modern_dashboard

            launch_modern_dashboard(optimizer)
        else:
            app = OptimusGUI(optimizer)
            app.run()

    except Exception as e:
        logger.error(f"Failed to start OptimusPC: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
