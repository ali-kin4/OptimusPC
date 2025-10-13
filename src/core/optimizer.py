# OptimusPC Core Optimizer Module

import psutil
import os
import tempfile
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Callable, Optional
import time
import gc

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
        
        # Progress callbacks
        self.on_progress_update: Optional[Callable] = None
        self.on_task_start: Optional[Callable] = None
        self.on_task_complete: Optional[Callable] = None
        self.on_log_message: Optional[Callable] = None
        self.cancelled = False
        
    def log_message(self, message: str, level: str = "INFO", geek_mode: bool = False):
        """Log a message with optional geek mode detail"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Log to file
        if level == "DEBUG":
            self.logger.debug(message)
        elif level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
            
        # Send to GUI if callback is set
        if self.on_log_message:
            self.on_log_message(formatted_message, level, geek_mode)
            
    def check_cancelled(self):
        """Check if optimization was cancelled"""
        return self.cancelled
        
    def cancel_optimization(self):
        """Cancel the current optimization"""
        self.cancelled = True
        self.log_message("Optimization cancelled by user", "WARNING")
        
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
    
    def optimize_memory(self, geek_mode: bool = False) -> Dict:
        """Optimize RAM usage with detailed logging"""
        try:
            if self.on_task_start:
                self.on_task_start("memory", "Memory Optimization")
                
            self.log_message("Starting memory optimization", "INFO", geek_mode)
            
            initial_memory = psutil.virtual_memory()
            self.log_message(f"Initial memory usage: {initial_memory.percent:.1f}% ({initial_memory.used / (1024**3):.1f} GB used)", 
                           "INFO", geek_mode)
            
            if self.check_cancelled():
                return {'success': False, 'error': 'Cancelled by user'}
            
            # Force garbage collection
            self.log_message("Running garbage collection", "DEBUG", geek_mode)
            collected_objects = gc.collect()
            self.log_message(f"Garbage collection completed: {collected_objects} objects collected", 
                           "DEBUG", geek_mode)
            
            if self.check_cancelled():
                return {'success': False, 'error': 'Cancelled by user'}
            
            # Clear system cache (Windows specific)
            if os.name == 'nt':
                self.log_message("Clearing system cache (Windows)", "DEBUG", geek_mode)
                try:
                    result = subprocess.run(['rundll32.exe', 'advapi32.dll,ProcessIdleTasks'], 
                                         check=True, capture_output=True, text=True)
                    self.log_message("System cache cleared successfully", "DEBUG", geek_mode)
                except subprocess.CalledProcessError as e:
                    self.log_message(f"System cache clear failed: {e}", "WARNING", geek_mode)
                except Exception as e:
                    self.log_message(f"Unexpected error during cache clear: {e}", "WARNING", geek_mode)
            
            if self.check_cancelled():
                return {'success': False, 'error': 'Cancelled by user'}
            
            final_memory = psutil.virtual_memory()
            freed_memory = initial_memory.used - final_memory.used
            freed_mb = freed_memory / (1024 * 1024)
            
            self.log_message(f"Memory optimization completed", "INFO", geek_mode)
            self.log_message(f"Final memory usage: {final_memory.percent:.1f}% ({final_memory.used / (1024**3):.1f} GB used)", 
                           "INFO", geek_mode)
            self.log_message(f"Memory freed: {freed_mb:.2f} MB", "INFO", geek_mode)
            
            result = {
                'success': True,
                'freed_memory_mb': freed_mb,
                'initial_percent': initial_memory.percent,
                'final_percent': final_memory.percent,
                'collected_objects': collected_objects
            }
            
            if self.on_task_complete:
                self.on_task_complete("memory", f"Freed {freed_mb:.2f} MB", freed_mb)
                
            return result
            
        except Exception as e:
            error_msg = f"Memory optimization failed: {e}"
            self.log_message(error_msg, "ERROR", geek_mode)
            return {'success': False, 'error': str(e)}
    
    def clear_temp_files(self, geek_mode: bool = False) -> Dict:
        """Clear temporary files from various locations with detailed logging"""
        try:
            if self.on_task_start:
                self.on_task_start("temp", "Temporary Files Cleanup")
                
            self.log_message("Starting temporary files cleanup", "INFO", geek_mode)
            
            total_freed = 0
            files_removed = 0
            errors = []
            
            for i, temp_dir in enumerate(self.temp_dirs):
                if self.check_cancelled():
                    return {'success': False, 'error': 'Cancelled by user'}
                    
                if os.path.exists(temp_dir):
                    self.log_message(f"Scanning directory: {temp_dir}", "DEBUG", geek_mode)
                    try:
                        freed, removed = self._clean_directory(temp_dir, geek_mode)
                        total_freed += freed
                        files_removed += removed
                        
                        if removed > 0:
                            self.log_message(f"Cleaned {temp_dir}: {removed} files, {freed / (1024*1024):.2f} MB", 
                                           "INFO", geek_mode)
                        else:
                            self.log_message(f"No files to clean in {temp_dir}", "DEBUG", geek_mode)
                            
                    except Exception as e:
                        error_msg = f"Error cleaning {temp_dir}: {e}"
                        errors.append(error_msg)
                        self.log_message(error_msg, "ERROR", geek_mode)
                else:
                    self.log_message(f"Directory not found: {temp_dir}", "DEBUG", geek_mode)
            
            freed_mb = total_freed / (1024 * 1024)
            self.log_message(f"Temporary files cleanup completed: {files_removed} files removed, {freed_mb:.2f} MB freed", 
                           "INFO", geek_mode)
            
            result = {
                'success': len(errors) == 0,
                'freed_space_mb': freed_mb,
                'files_removed': files_removed,
                'errors': errors
            }
            
            if self.on_task_complete:
                self.on_task_complete("temp", f"Removed {files_removed} files, freed {freed_mb:.2f} MB", freed_mb)
                
            return result
            
        except Exception as e:
            error_msg = f"Temporary files cleanup failed: {e}"
            self.log_message(error_msg, "ERROR", geek_mode)
            return {'success': False, 'error': str(e)}
    
    def _clean_directory(self, directory: str, geek_mode: bool = False) -> Tuple[int, int]:
        """Clean files from a specific directory with detailed logging"""
        freed_space = 0
        files_removed = 0
        
        try:
            for root, dirs, files in os.walk(directory):
                if self.check_cancelled():
                    break
                    
                if geek_mode and files:
                    self.log_message(f"Processing {len(files)} files in {root}", "DEBUG", geek_mode)
                
                for file in files:
                    if self.check_cancelled():
                        break
                        
                    file_path = os.path.join(root, file)
                    try:
                        if os.path.exists(file_path):
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            freed_space += file_size
                            files_removed += 1
                            
                            if geek_mode:
                                self.log_message(f"Deleted: {file} ({file_size / 1024:.1f} KB)", "DEBUG", geek_mode)
                                
                    except (OSError, PermissionError) as e:
                        if geek_mode:
                            self.log_message(f"Could not delete {file}: {e}", "DEBUG", geek_mode)
                        continue
                        
                # Remove empty directories
                for dir_name in dirs:
                    if self.check_cancelled():
                        break
                        
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if os.path.exists(dir_path) and not os.listdir(dir_path):
                            os.rmdir(dir_path)
                            if geek_mode:
                                self.log_message(f"Removed empty directory: {dir_name}", "DEBUG", geek_mode)
                    except (OSError, PermissionError):
                        continue
                        
        except Exception as e:
            self.log_message(f"Error cleaning directory {directory}: {e}", "ERROR", geek_mode)
            
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
    
    def run_full_optimization(self, geek_mode: bool = False, tasks: List[str] = None) -> Dict:
        """Run complete system optimization with detailed logging"""
        self.cancelled = False
        
        if tasks is None:
            tasks = ['memory', 'temp', 'cache', 'startup']
            
        self.log_message("Starting full system optimization", "INFO", geek_mode)
        self.log_message(f"Optimization tasks: {', '.join(tasks)}", "INFO", geek_mode)
        
        results = {
            'timestamp': time.time(),
            'tasks_completed': [],
            'total_freed_mb': 0
        }
        
        # Memory optimization
        if 'memory' in tasks and not self.check_cancelled():
            results['memory_optimization'] = self.optimize_memory(geek_mode)
            if results['memory_optimization']['success']:
                results['tasks_completed'].append('memory')
                results['total_freed_mb'] += results['memory_optimization'].get('freed_memory_mb', 0)
        
        # Temp file cleanup
        if 'temp' in tasks and not self.check_cancelled():
            results['temp_cleanup'] = self.clear_temp_files(geek_mode)
            if results['temp_cleanup']['success']:
                results['tasks_completed'].append('temp')
                results['total_freed_mb'] += results['temp_cleanup'].get('freed_space_mb', 0)
        
        # Browser cache cleanup
        if 'cache' in tasks and not self.check_cancelled():
            results['browser_cache'] = self.clear_browser_cache(geek_mode)
            if results['browser_cache']['success']:
                results['tasks_completed'].append('cache')
                results['total_freed_mb'] += results['browser_cache'].get('total_freed_mb', 0)
        
        # Startup analysis
        if 'startup' in tasks and not self.check_cancelled():
            results['startup_analysis'] = self.optimize_startup_programs(geek_mode)
            if results['startup_analysis']['success']:
                results['tasks_completed'].append('startup')
        
        # System info
        results['system_info'] = self.get_system_info()
        
        if self.check_cancelled():
            self.log_message("Optimization cancelled by user", "WARNING", geek_mode)
            results['cancelled'] = True
        else:
            self.log_message(f"Optimization completed successfully", "INFO", geek_mode)
            self.log_message(f"Total space freed: {results['total_freed_mb']:.2f} MB", "INFO", geek_mode)
            self.log_message(f"Tasks completed: {len(results['tasks_completed'])}/{len(tasks)}", "INFO", geek_mode)
        
        return results
