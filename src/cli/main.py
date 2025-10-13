# OptimusPC CLI Interface

import argparse
import sys
import json
from typing import Dict, Any

def run_cli(optimizer):
    """Run OptimusPC in command-line mode"""
    parser = argparse.ArgumentParser(description="OptimusPC - PC Optimization Tool")
    
    parser.add_argument('--memory', action='store_true', 
                      help='Optimize memory usage')
    parser.add_argument('--temp', action='store_true', 
                      help='Clear temporary files')
    parser.add_argument('--cache', action='store_true', 
                      help='Clear browser cache')
    parser.add_argument('--startup', action='store_true', 
                      help='Analyze startup programs')
    parser.add_argument('--full', action='store_true', 
                      help='Run full optimization')
    parser.add_argument('--info', action='store_true', 
                      help='Show system information')
    parser.add_argument('--output', '-o', type=str, 
                      help='Output results to JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', 
                      help='Verbose output')
    
    args = parser.parse_args()
    
    # If no specific options, show help
    if not any([args.memory, args.temp, args.cache, args.startup, args.full, args.info]):
        parser.print_help()
        return
    
    results = {}
    
    try:
        if args.info:
            print("=== System Information ===")
            info = optimizer.get_system_info()
            if info:
                print(f"CPU: {info.get('cpu_count', 'N/A')} cores, {info.get('cpu_percent', 0):.1f}% usage")
                print(f"Memory: {info.get('memory_percent', 0):.1f}% used ({info.get('memory_available', 0) / (1024**3):.1f} GB available)")
                print(f"Disk: {info.get('disk_percent', 0):.1f}% used ({info.get('disk_free', 0) / (1024**3):.1f} GB free)")
            results['system_info'] = info
        
        if args.full or args.memory:
            print("Optimizing memory...")
            results['memory'] = optimizer.optimize_memory()
            if args.verbose:
                mem_result = results['memory']
                if mem_result.get('success'):
                    print(f"  Freed: {mem_result.get('freed_memory_mb', 0):.2f} MB")
                    print(f"  Usage: {mem_result.get('initial_percent', 0):.1f}% → {mem_result.get('final_percent', 0):.1f}%")
        
        if args.full or args.temp:
            print("Clearing temporary files...")
            results['temp'] = optimizer.clear_temp_files()
            if args.verbose:
                temp_result = results['temp']
                if temp_result.get('success'):
                    print(f"  Freed: {temp_result.get('freed_space_mb', 0):.2f} MB")
                    print(f"  Files removed: {temp_result.get('files_removed', 0)}")
        
        if args.full or args.cache:
            print("Clearing browser cache...")
            results['cache'] = optimizer.clear_browser_cache()
            if args.verbose:
                cache_result = results['cache']
                if cache_result.get('success'):
                    print(f"  Total freed: {cache_result.get('total_freed_mb', 0):.2f} MB")
                    print(f"  Files removed: {cache_result.get('total_files_removed', 0)}")
        
        if args.full or args.startup:
            print("Analyzing startup programs...")
            results['startup'] = optimizer.optimize_startup_programs()
            if args.verbose:
                startup_result = results['startup']
                if startup_result.get('success'):
                    print(f"  Found {startup_result.get('count', 0)} startup programs")
        
        # Calculate total freed space
        total_freed = 0
        if 'memory' in results and results['memory'].get('success'):
            total_freed += results['memory'].get('freed_memory_mb', 0)
        if 'temp' in results and results['temp'].get('success'):
            total_freed += results['temp'].get('freed_space_mb', 0)
        if 'cache' in results and results['cache'].get('success'):
            total_freed += results['cache'].get('total_freed_mb', 0)
        
        print(f"\n=== Summary ===")
        print(f"Total space freed: {total_freed:.2f} MB")
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to: {args.output}")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
