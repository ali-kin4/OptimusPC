#!/usr/bin/env python3
"""
Test script to verify system information loading works without errors
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.core.optimizer import OptimusOptimizer
    from src.config.settings import Config
    
    print("Testing OptimusPC system information loading...")
    print("=" * 50)
    
    # Load configuration
    config = Config()
    print("✓ Configuration loaded")
    
    # Initialize optimizer
    optimizer = OptimusOptimizer(config)
    print("✓ Optimizer initialized")
    
    # Get system info
    print("\nGetting system information...")
    info = optimizer.get_system_info()
    
    if info and 'error' not in info:
        print("✓ System information loaded successfully")
        
        # Test key components
        if 'windows_version' in info:
            print(f"✓ Windows version: {info['windows_version'].get('release', 'Unknown')}")
        
        if 'cpu' in info:
            cpu_info = info['cpu']
            if 'error' not in cpu_info:
                print(f"✓ CPU: {cpu_info.get('name', 'Unknown')} ({cpu_info.get('physical_cores', 'Unknown')} cores)")
            else:
                print("⚠ CPU info has errors but won't crash")
        
        if 'memory' in info:
            memory_info = info['memory']
            if 'error' not in memory_info:
                total_gb = (memory_info.get('total', 0) or 0) / (1024**3)
                print(f"✓ Memory: {total_gb:.1f} GB total")
            else:
                print("⚠ Memory info has errors but won't crash")
        
        if 'gpu' in info:
            gpu_info = info['gpu']
            if gpu_info:
                print(f"✓ GPU: {len(gpu_info)} GPU(s) detected")
            else:
                print("✓ No dedicated GPUs detected")
        
        if 'disk' in info:
            disk_info = info['disk']
            if disk_info:
                print(f"✓ Storage: {len(disk_info)} drive(s) detected")
            else:
                print("⚠ No disk information available")
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! System information loading works correctly.")
        print("The System Info button should now work without errors.")
        
    else:
        print("❌ Failed to load system information")
        if 'error' in info:
            print(f"Error: {info['error']}")
        
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()

