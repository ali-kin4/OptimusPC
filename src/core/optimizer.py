# OptimusPC Core Optimizer Module

import psutil
import os
import tempfile
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import time

class OptimusOptimizer:
    """Main optimizer class for PC performance enhancement"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.temp_dirs = [
            tempfile.gettempdir(),
            os.path.expandvars('%TEMP%'),
            os.path.expandvars('%TMP%'),
            os.path.expanduser('~\\AppData\\Local\\Temp'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\INetCache'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\WebCache'),
        ]
        
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_total': memory.total,
                'memory_available': memory.available,
                'memory_percent': memory.percent,
                'disk_total': disk.total,
                'disk_free': disk.free,
                'disk_percent': (disk.used / disk.total) * 100,
                'boot_time': psutil.boot_time()
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
    
    def optimize_memory(self) -> Dict:
        """Optimize RAM usage"""
        try:
            initial_memory = psutil.virtual_memory()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear system cache (Windows specific)
            if os.name == 'nt':
                try:
                    subprocess.run(['rundll32.exe', 'advapi32.dll,ProcessIdleTasks'], 
                                 check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    pass
            
            final_memory = psutil.virtual_memory()
            
            freed_memory = initial_memory.used - final_memory.used
            
            return {
                'success': True,
                'freed_memory_mb': freed_memory / (1024 * 1024),
                'initial_percent': initial_memory.percent,
                'final_percent': final_memory.percent
            }
            
        except Exception as e:
            self.logger.error(f"Memory optimization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def clear_temp_files(self) -> Dict:
        """Clear temporary files from various locations"""
        total_freed = 0
        files_removed = 0
        errors = []
        
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    freed, removed = self._clean_directory(temp_dir)
                    total_freed += freed
                    files_removed += removed
                except Exception as e:
                    errors.append(f"Error cleaning {temp_dir}: {e}")
                    self.logger.error(f"Error cleaning {temp_dir}: {e}")
        
        return {
            'success': len(errors) == 0,
            'freed_space_mb': total_freed / (1024 * 1024),
            'files_removed': files_removed,
            'errors': errors
        }
    
    def _clean_directory(self, directory: str) -> Tuple[int, int]:
        """Clean files from a specific directory"""
        freed_space = 0
        files_removed = 0
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        if os.path.exists(file_path):
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            freed_space += file_size
                            files_removed += 1
                    except (OSError, PermissionError):
                        # Skip files that can't be deleted
                        continue
                        
                # Remove empty directories
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if os.path.exists(dir_path) and not os.listdir(dir_path):
                            os.rmdir(dir_path)
                    except (OSError, PermissionError):
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error cleaning directory {directory}: {e}")
            
        return freed_space, files_removed
    
    def clear_browser_cache(self) -> Dict:
        """Clear browser cache files"""
        browsers = {
            'Chrome': [
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache'),
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Code Cache'),
            ],
            'Firefox': [
                os.path.expanduser('~\\AppData\\Local\\Mozilla\\Firefox\\Profiles'),
            ],
            'Edge': [
                os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache'),
            ]
        }
        
        total_freed = 0
        files_removed = 0
        results = {}
        
        for browser, paths in browsers.items():
            browser_freed = 0
            browser_files = 0
            
            for path in paths:
                if os.path.exists(path):
                    try:
                        freed, removed = self._clean_directory(path)
                        browser_freed += freed
                        browser_files += removed
                    except Exception as e:
                        self.logger.error(f"Error cleaning {browser} cache: {e}")
            
            results[browser] = {
                'freed_mb': browser_freed / (1024 * 1024),
                'files_removed': browser_files
            }
            total_freed += browser_freed
            files_removed += browser_files
        
        return {
            'success': True,
            'total_freed_mb': total_freed / (1024 * 1024),
            'total_files_removed': files_removed,
            'browsers': results
        }
    
    def optimize_startup_programs(self) -> Dict:
        """Analyze and suggest startup program optimizations"""
        try:
            # Get startup programs from registry
            startup_programs = []
            
            if os.name == 'nt':
                import winreg
                
                # Common startup registry keys
                startup_keys = [
                    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
                    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
                ]
                
                for hkey, subkey in startup_keys:
                    try:
                        with winreg.OpenKey(hkey, subkey) as key:
                            i = 0
                            while True:
                                try:
                                    name, value, _ = winreg.EnumValue(key, i)
                                    startup_programs.append({
                                        'name': name,
                                        'path': value,
                                        'location': f"{hkey}\\{subkey}"
                                    })
                                    i += 1
                                except OSError:
                                    break
                    except FileNotFoundError:
                        continue
            
            return {
                'success': True,
                'startup_programs': startup_programs,
                'count': len(startup_programs)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing startup programs: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_full_optimization(self) -> Dict:
        """Run complete system optimization"""
        results = {
            'timestamp': time.time(),
            'memory_optimization': self.optimize_memory(),
            'temp_cleanup': self.clear_temp_files(),
            'browser_cache': self.clear_browser_cache(),
            'startup_analysis': self.optimize_startup_programs(),
            'system_info': self.get_system_info()
        }
        
        # Calculate total space freed
        total_freed = 0
        if results['temp_cleanup']['success']:
            total_freed += results['temp_cleanup']['freed_space_mb']
        if results['browser_cache']['success']:
            total_freed += results['browser_cache']['total_freed_mb']
        
        results['total_freed_mb'] = total_freed
        
        return results
