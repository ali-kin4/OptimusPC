#!/usr/bin/env python3
"""
Test script to verify live system information updates work
"""

import sys
import os
import time


def main() -> None:
    """Run a simple live update demonstration when executed directly."""

    # Add src directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

    try:
        from src.core.optimizer import OptimusOptimizer
        from src.config.settings import Config

        print("Testing OptimusPC Live System Information Updates...")
        print("=" * 60)

        # Load configuration
        config = Config()
        print("✓ Configuration loaded")

        # Initialize optimizer
        optimizer = OptimusOptimizer(config)
        print("✓ Optimizer initialized")

        print("\nTesting live updates (will run for 10 seconds)...")
        print("Watch the CPU usage change in real-time:")
        print("-" * 60)

        for i in range(5):
            # Get system info
            info = optimizer.get_system_info()

            if info and 'error' not in info:
                # Display key live metrics
                cpu_percent = info.get('cpu_percent', 0)
                memory_info = info.get('memory', {})
                memory_percent = memory_info.get('percent', 0) if memory_info else info.get('memory_percent', 0)

                # Get current time
                current_time = time.strftime('%H:%M:%S')

                print(f"[{current_time}] CPU: {cpu_percent:.1f}% | Memory: {memory_percent:.1f}%")

                # Simulate some CPU load to see changes
                if i == 2:
                    print("  → Simulating CPU load...")
                    # Do some work to change CPU usage
                    for _ in range(1000000):
                        pass

            else:
                current_time = time.strftime('%H:%M:%S')
                print(f"[{current_time}] Error loading system info")

            time.sleep(2)  # Wait 2 seconds between updates

        print("\n" + "=" * 60)
        print("✅ Live update test completed!")
        print("The Detailed System Information window will now update automatically.")
        print("You can change the update interval and toggle live updates on/off.")

    except Exception as e:  # pragma: no cover - manual smoke script
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

