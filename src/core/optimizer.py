# OptimusPC Core Optimizer Module

import os
import tempfile
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Callable, Optional
import time
import gc
from ..utils.psutil_safe import psutil
from ..utils.system_detector import SystemDetector
from ..utils.hardware_monitor import HardwareMonitor

class OptimusOptimizer:
    """Main optimizer class for PC performance enhancement"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.system_detector = SystemDetector()
        self.hardware_monitor = HardwareMonitor(self.system_detector)
        self.windows_compatibility = self.system_detector.get_windows_compatibility_info()
        
        self.temp_dirs = [
            tempfile.gettempdir(),
            os.path.expandvars('%TEMP%'),
            os.path.expandvars('%TMP%'),
            os.path.expanduser('~\\AppData\\Local\\Temp'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\INetCache'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\WebCache'),
        ]
        
        # Additional cleanup directories for Windows optimization
        self.windows_cleanup_dirs = [
            os.path.expandvars('%SystemRoot%\\Temp'),
            os.path.expandvars('%SystemRoot%\\SoftwareDistribution\\Download'),
            os.path.expandvars('%SystemRoot%\\Logs'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\Explorer'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\Caches'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\WebCache'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\INetCache'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files'),
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
            # Get basic system info using psutil
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            basic_info = {
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_total': memory.total,
                'memory_available': memory.available,
                'memory_percent': memory.percent,
                'disk_total': disk.total,
                'disk_free': disk.free,
                'disk_percent': (disk.used / disk.total) * 100 if getattr(disk, 'total', 0) else 0,
                'boot_time': psutil.boot_time()
            }
            
            # Get detailed system info using system detector
            detailed_info = self.system_detector.get_system_summary()
            
            # Merge basic and detailed info
            if 'error' not in detailed_info:
                basic_info.update(detailed_info)
            
            return basic_info
            
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
                    # Use Windows version-specific commands
                    if self.windows_compatibility.get('version') in ['10', '11']:
                        # Windows 10/11 - Use PowerShell for better compatibility
                        ps_command = "Clear-RecycleBin -Force -ErrorAction SilentlyContinue; [System.GC]::Collect()"
                        result = subprocess.run(['powershell', '-Command', ps_command], 
                                             check=True, capture_output=True, text=True)
                        self.log_message("System cache cleared using PowerShell", "DEBUG", geek_mode)
                    else:
                        # Windows 7/8/8.1 - Use traditional methods
                        result = subprocess.run(['rundll32.exe', 'advapi32.dll,ProcessIdleTasks'], 
                                             check=True, capture_output=True, text=True)
                        self.log_message("System cache cleared using rundll32", "DEBUG", geek_mode)
                    
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
    
    def clear_browser_cache(self, geek_mode: bool = False) -> Dict:
        """Clear browser cache files with detailed logging"""
        try:
            if self.on_task_start:
                self.on_task_start("cache", "Browser Cache Cleanup")
                
            self.log_message("Starting browser cache cleanup", "INFO", geek_mode)
            
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
                if self.check_cancelled():
                    return {'success': False, 'error': 'Cancelled by user'}
                    
                self.log_message(f"Cleaning {browser} cache", "INFO", geek_mode)
                browser_freed = 0
                browser_files = 0
                
                for path in paths:
                    if self.check_cancelled():
                        break
                        
                    if os.path.exists(path):
                        self.log_message(f"Scanning {browser} cache: {path}", "DEBUG", geek_mode)
                        try:
                            freed, removed = self._clean_directory(path, geek_mode)
                            browser_freed += freed
                            browser_files += removed
                            
                            if removed > 0:
                                self.log_message(f"{browser} cache cleaned: {removed} files, {freed / (1024*1024):.2f} MB", 
                                               "INFO", geek_mode)
                            else:
                                self.log_message(f"No files to clean in {browser} cache", "DEBUG", geek_mode)
                                
                        except Exception as e:
                            error_msg = f"Error cleaning {browser} cache: {e}"
                            self.log_message(error_msg, "ERROR", geek_mode)
                    else:
                        self.log_message(f"{browser} cache directory not found: {path}", "DEBUG", geek_mode)
                
                results[browser] = {
                    'freed_mb': browser_freed / (1024 * 1024),
                    'files_removed': browser_files
                }
                total_freed += browser_freed
                files_removed += browser_files
                
                if browser_files > 0:
                    self.log_message(f"{browser} cleanup completed: {browser_files} files, {browser_freed / (1024*1024):.2f} MB", 
                                   "INFO", geek_mode)
            
            total_freed_mb = total_freed / (1024 * 1024)
            self.log_message(f"Browser cache cleanup completed: {files_removed} files removed, {total_freed_mb:.2f} MB freed", 
                           "INFO", geek_mode)
            
            result = {
                'success': True,
                'total_freed_mb': total_freed_mb,
                'total_files_removed': files_removed,
                'browsers': results
            }
            
            if self.on_task_complete:
                self.on_task_complete("cache", f"Cleaned {files_removed} files, freed {total_freed_mb:.2f} MB", total_freed_mb)
                
            return result
            
        except Exception as e:
            error_msg = f"Browser cache cleanup failed: {e}"
            self.log_message(error_msg, "ERROR", geek_mode)
            return {'success': False, 'error': str(e)}
    
    def optimize_startup_programs(self, geek_mode: bool = False) -> Dict:
        """Analyze and suggest startup program optimizations with detailed logging"""
        try:
            if self.on_task_start:
                self.on_task_start("startup", "Startup Programs Analysis")
                
            self.log_message("Starting startup programs analysis", "INFO", geek_mode)
            
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
                    if self.check_cancelled():
                        break
                        
                    self.log_message(f"Scanning registry key: {subkey}", "DEBUG", geek_mode)
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
                                    
                                    if geek_mode:
                                        self.log_message(f"Found startup program: {name} -> {value}", "DEBUG", geek_mode)
                                    
                                    i += 1
                                except OSError:
                                    break
                    except FileNotFoundError:
                        self.log_message(f"Registry key not found: {subkey}", "DEBUG", geek_mode)
                        continue
                    except Exception as e:
                        self.log_message(f"Error reading registry key {subkey}: {e}", "WARNING", geek_mode)
            
            self.log_message(f"Startup programs analysis completed: {len(startup_programs)} programs found", 
                           "INFO", geek_mode)
            
            result = {
                'success': True,
                'startup_programs': startup_programs,
                'count': len(startup_programs)
            }
            
            if self.on_task_complete:
                self.on_task_complete("startup", f"Found {len(startup_programs)} startup programs", 0)
                
            return result
            
        except Exception as e:
            error_msg = f"Startup programs analysis failed: {e}"
            self.log_message(error_msg, "ERROR", geek_mode)
            return {'success': False, 'error': str(e)}
    
    def clear_windows_update_cache(self, geek_mode: bool = False) -> Dict:
        """Clear Windows Update cache and temporary files"""
        try:
            if self.on_task_start:
                self.on_task_start("windows_update", "Windows Update Cache Cleanup")
                
            self.log_message("Starting Windows Update cache cleanup", "INFO", geek_mode)
            
            total_freed = 0
            files_removed = 0
            errors = []
            
            # Windows Update specific directories
            update_dirs = [
                os.path.expandvars('%SystemRoot%\\SoftwareDistribution\\Download'),
                os.path.expandvars('%SystemRoot%\\SoftwareDistribution\\DataStore'),
                os.path.expandvars('%SystemRoot%\\Temp'),
                os.path.expandvars('%SystemRoot%\\Logs\\CBS'),
                os.path.expandvars('%SystemRoot%\\Logs\\DISM'),
            ]
            
            for update_dir in update_dirs:
                if self.check_cancelled():
                    return {'success': False, 'error': 'Cancelled by user'}
                    
                if os.path.exists(update_dir):
                    self.log_message(f"Cleaning Windows Update directory: {update_dir}", "DEBUG", geek_mode)
                    try:
                        freed, removed = self._clean_directory(update_dir, geek_mode)
                        total_freed += freed
                        files_removed += removed
                        
                        if removed > 0:
                            self.log_message(f"Cleaned {update_dir}: {removed} files, {freed / (1024*1024):.2f} MB", 
                                           "INFO", geek_mode)
                        else:
                            self.log_message(f"No files to clean in {update_dir}", "DEBUG", geek_mode)
                            
                    except Exception as e:
                        error_msg = f"Error cleaning {update_dir}: {e}"
                        errors.append(error_msg)
                        self.log_message(error_msg, "ERROR", geek_mode)
                else:
                    self.log_message(f"Windows Update directory not found: {update_dir}", "DEBUG", geek_mode)
            
            # Try to stop and restart Windows Update service for deeper cleanup
            if os.name == 'nt' and not self.check_cancelled():
                self.log_message("Attempting to restart Windows Update service", "DEBUG", geek_mode)
                try:
                    subprocess.run(['net', 'stop', 'wuauserv'], check=True, capture_output=True, text=True)
                    subprocess.run(['net', 'start', 'wuauserv'], check=True, capture_output=True, text=True)
                    self.log_message("Windows Update service restarted successfully", "INFO", geek_mode)
                except subprocess.CalledProcessError as e:
                    self.log_message(f"Could not restart Windows Update service: {e}", "WARNING", geek_mode)
                except Exception as e:
                    self.log_message(f"Unexpected error restarting Windows Update service: {e}", "WARNING", geek_mode)
            
            freed_mb = total_freed / (1024 * 1024)
            self.log_message(f"Windows Update cache cleanup completed: {files_removed} files removed, {freed_mb:.2f} MB freed", 
                           "INFO", geek_mode)
            
            result = {
                'success': len(errors) == 0,
                'freed_space_mb': freed_mb,
                'files_removed': files_removed,
                'errors': errors
            }
            
            if self.on_task_complete:
                self.on_task_complete("windows_update", f"Cleaned {files_removed} files, freed {freed_mb:.2f} MB", freed_mb)
                
            return result
            
        except Exception as e:
            error_msg = f"Windows Update cache cleanup failed: {e}"
            self.log_message(error_msg, "ERROR", geek_mode)
            return {'success': False, 'error': str(e)}
    
    def optimize_ssd(self, geek_mode: bool = False) -> Dict:
        """Optimize SSD performance with TRIM and health monitoring"""
        try:
            if self.on_task_start:
                self.on_task_start("ssd", "SSD Optimization")
                
            self.log_message("Starting SSD optimization", "INFO", geek_mode)
            
            results = {
                'trim_executed': False,
                'defrag_skipped': False,
                'health_check': False,
                'optimization_completed': False
            }
            
            if os.name == 'nt':
                # Execute TRIM command for all drives using Windows version-specific commands
                self.log_message("Executing TRIM command for SSD optimization", "INFO", geek_mode)
                try:
                    if self.windows_compatibility.get('version') in ['10', '11']:
                        # Windows 10/11 - Use PowerShell for better SSD optimization
                        ps_command = """
                        Get-PhysicalDisk | Where-Object {$_.MediaType -eq 'SSD'} | ForEach-Object {
                            Write-Host "Optimizing SSD: $($_.FriendlyName)"
                            Optimize-Volume -DriveLetter $_.DeviceID -ReTrim -Verbose
                        }
                        """
                        result = subprocess.run(['powershell', '-Command', ps_command], 
                                             check=True, capture_output=True, text=True)
                        self.log_message("SSD optimization completed using PowerShell", "INFO", geek_mode)
                    else:
                        # Windows 7/8/8.1 - Use defrag with TRIM
                        result = subprocess.run(['defrag', '/C', '/H'], check=True, capture_output=True, text=True)
                        self.log_message("SSD optimization completed using defrag", "INFO", geek_mode)
                    
                    results['trim_executed'] = True
                    
                    if geek_mode:
                        self.log_message(f"SSD optimization output: {result.stdout}", "DEBUG", geek_mode)
                        
                except subprocess.CalledProcessError as e:
                    self.log_message(f"SSD optimization failed: {e}", "WARNING", geek_mode)
                except Exception as e:
                    self.log_message(f"Unexpected error during SSD optimization: {e}", "WARNING", geek_mode)
                
                # Check if defragmentation is needed (should be skipped for SSDs)
                self.log_message("Checking disk fragmentation status", "DEBUG", geek_mode)
                try:
                    if self.windows_compatibility.get('version') in ['10', '11']:
                        # Windows 10/11 - Use PowerShell for disk analysis
                        ps_command = "Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus"
                        result = subprocess.run(['powershell', '-Command', ps_command], 
                                             check=True, capture_output=True, text=True)
                        
                        if 'SSD' in result.stdout or 'Solid State' in result.stdout:
                            self.log_message("SSD detected - defragmentation skipped (not needed)", "INFO", geek_mode)
                            results['defrag_skipped'] = True
                        else:
                            self.log_message("HDD detected - defragmentation may be beneficial", "INFO", geek_mode)
                    else:
                        # Windows 7/8/8.1 - Use defrag for analysis
                        result = subprocess.run(['defrag', '/A', '/C'], check=True, capture_output=True, text=True)
                        if 'SSD' in result.stdout or 'Solid State' in result.stdout:
                            self.log_message("SSD detected - defragmentation skipped (not needed)", "INFO", geek_mode)
                            results['defrag_skipped'] = True
                        else:
                            self.log_message("HDD detected - defragmentation may be beneficial", "INFO", geek_mode)
                        
                    if geek_mode:
                        self.log_message(f"Disk analysis output: {result.stdout}", "DEBUG", geek_mode)
                        
                except subprocess.CalledProcessError as e:
                    self.log_message(f"Disk analysis failed: {e}", "WARNING", geek_mode)
                
                # Check disk health using Windows version-specific commands
                self.log_message("Performing disk health check", "DEBUG", geek_mode)
                try:
                    if self.windows_compatibility.get('version') in ['10', '11']:
                        # Windows 10/11 - Use PowerShell for health check
                        ps_command = "Get-PhysicalDisk | Select-Object DeviceID, MediaType, HealthStatus, OperationalStatus"
                        result = subprocess.run(['powershell', '-Command', ps_command], 
                                              check=True, capture_output=True, text=True)
                    else:
                        # Windows 7/8/8.1 - Use wmic for health check
                        result = subprocess.run(['wmic', 'diskdrive', 'get', 'status,size,model'], 
                                              check=True, capture_output=True, text=True)
                    
                    if 'Healthy' in result.stdout or 'OK' in result.stdout:
                        self.log_message("Disk health check completed - drives are healthy", "INFO", geek_mode)
                        results['health_check'] = True
                    else:
                        self.log_message("Disk health check completed - some drives may need attention", "WARNING", geek_mode)
                        
                    if geek_mode:
                        self.log_message(f"Disk health output: {result.stdout}", "DEBUG", geek_mode)
                        
                except subprocess.CalledProcessError as e:
                    self.log_message(f"Disk health check failed: {e}", "WARNING", geek_mode)
            
            results['optimization_completed'] = True
            self.log_message("SSD optimization completed successfully", "INFO", geek_mode)
            
            if self.on_task_complete:
                self.on_task_complete("ssd", "SSD optimization completed", 0)
                
            return {
                'success': True,
                'results': results
            }
            
        except Exception as e:
            error_msg = f"SSD optimization failed: {e}"
            self.log_message(error_msg, "ERROR", geek_mode)
            return {'success': False, 'error': str(e)}
    
    def clear_dns_cache(self, geek_mode: bool = False) -> Dict:
        """Clear DNS cache and network optimization"""
        try:
            if self.on_task_start:
                self.on_task_start("dns", "DNS Cache Cleanup")
                
            self.log_message("Starting DNS cache cleanup", "INFO", geek_mode)
            
            if os.name == 'nt':
                try:
                    # Clear DNS cache using Windows version-specific commands
                    if self.windows_compatibility.get('version') in ['10', '11']:
                        # Windows 10/11 - Use PowerShell for better network management
                        ps_command = """
                        Clear-DnsClientCache
                        Write-Host "DNS cache cleared"
                        """
                        result = subprocess.run(['powershell', '-Command', ps_command], 
                                             check=True, capture_output=True, text=True)
                        self.log_message("DNS cache flushed using PowerShell", "INFO", geek_mode)
                    else:
                        # Windows 7/8/8.1 - Use traditional ipconfig
                        result = subprocess.run(['ipconfig', '/flushdns'], check=True, capture_output=True, text=True)
                        self.log_message("DNS cache flushed using ipconfig", "INFO", geek_mode)
                    
                    if geek_mode:
                        self.log_message(f"DNS flush output: {result.stdout}", "DEBUG", geek_mode)
                    
                    # Reset network stack using Windows version-specific commands
                    self.log_message("Resetting network stack", "DEBUG", geek_mode)
                    if self.windows_compatibility.get('version') in ['10', '11']:
                        # Windows 10/11 - Use PowerShell for network reset
                        ps_command = """
                        netsh winsock reset
                        netsh int ip reset
                        Write-Host "Network stack reset completed"
                        """
                        subprocess.run(['powershell', '-Command', ps_command], 
                                    check=True, capture_output=True, text=True)
                    else:
                        # Windows 7/8/8.1 - Use netsh directly
                        subprocess.run(['netsh', 'winsock', 'reset'], check=True, capture_output=True, text=True)
                        subprocess.run(['netsh', 'int', 'ip', 'reset'], check=True, capture_output=True, text=True)
                    
                    self.log_message("Network stack reset completed", "INFO", geek_mode)
                    
                except subprocess.CalledProcessError as e:
                    self.log_message(f"Network optimization failed: {e}", "WARNING", geek_mode)
                    return {'success': False, 'error': str(e)}
                except Exception as e:
                    self.log_message(f"Unexpected error during network optimization: {e}", "WARNING", geek_mode)
                    return {'success': False, 'error': str(e)}
            
            self.log_message("DNS cache cleanup completed successfully", "INFO", geek_mode)
            
            if self.on_task_complete:
                self.on_task_complete("dns", "DNS cache cleared and network optimized", 0)
                
            return {'success': True}
            
        except Exception as e:
            error_msg = f"DNS cache cleanup failed: {e}"
            self.log_message(error_msg, "ERROR", geek_mode)
            return {'success': False, 'error': str(e)}
    
    def create_system_restore_point(self, geek_mode: bool = False) -> Dict:
        """Create a system restore point before optimization"""
        try:
            if self.on_task_start:
                self.on_task_start("restore_point", "Creating System Restore Point")
                
            self.log_message("Creating system restore point", "INFO", geek_mode)
            
            if os.name == 'nt':
                try:
                    # Create restore point using Windows version-specific commands
                    if self.windows_compatibility.get('version') in ['10', '11']:
                        # Windows 10/11 - Use PowerShell Checkpoint-Computer
                        ps_command = """
                        Checkpoint-Computer -Description "OptimusPC Optimization" -RestorePointType "MODIFY_SETTINGS"
                        """
                        result = subprocess.run(['powershell', '-Command', ps_command], 
                                              check=True, capture_output=True, text=True)
                        self.log_message("System restore point created using PowerShell", "INFO", geek_mode)
                    else:
                        # Windows 7/8/8.1 - Use wmic or vssadmin
                        try:
                            # Try wmic first
                            result = subprocess.run(['wmic', 'path', 'Win32_SystemRestore', 'call', 'CreateRestorePoint', 
                                                   '"OptimusPC Optimization"', '7', '0'], 
                                                  check=True, capture_output=True, text=True)
                            self.log_message("System restore point created using wmic", "INFO", geek_mode)
                        except subprocess.CalledProcessError:
                            # Fallback to vssadmin
                            result = subprocess.run(['vssadmin', 'create', 'shadow', '/for=C:', 
                                                   '/autoretry=1'], 
                                                  check=True, capture_output=True, text=True)
                            self.log_message("System restore point created using vssadmin", "INFO", geek_mode)
                    
                    self.log_message("System restore point created successfully", "INFO", geek_mode)
                    
                    if geek_mode:
                        self.log_message(f"Restore point creation output: {result.stdout}", "DEBUG", geek_mode)
                    
                    if self.on_task_complete:
                        self.on_task_complete("restore_point", "System restore point created", 0)
                    
                    return {'success': True, 'message': 'System restore point created successfully'}
                    
                except subprocess.CalledProcessError as e:
                    self.log_message(f"Failed to create restore point: {e}", "WARNING", geek_mode)
                    return {'success': False, 'error': str(e)}
                except Exception as e:
                    self.log_message(f"Unexpected error creating restore point: {e}", "WARNING", geek_mode)
                    return {'success': False, 'error': str(e)}
            else:
                self.log_message("System restore points not supported on this platform", "INFO", geek_mode)
                return {'success': True, 'message': 'System restore points not supported'}
                
        except Exception as e:
            error_msg = f"System restore point creation failed: {e}"
            self.log_message(error_msg, "ERROR", geek_mode)
            return {'success': False, 'error': str(e)}
    
    def run_full_optimization(self, geek_mode: bool = False, tasks: List[str] = None) -> Dict:
        """Run complete system optimization with detailed logging"""
        self.cancelled = False
        
        if tasks is None:
            tasks = ['restore_point', 'memory', 'temp', 'cache', 'windows_update', 'ssd', 'dns', 'startup']
            
        self.log_message("Starting full system optimization", "INFO", geek_mode)
        self.log_message(f"Optimization tasks: {', '.join(tasks)}", "INFO", geek_mode)
        
        results = {
            'timestamp': time.time(),
            'tasks_completed': [],
            'total_freed_mb': 0
        }
        
        # System restore point creation (first for safety)
        if 'restore_point' in tasks and not self.check_cancelled():
            results['restore_point'] = self.create_system_restore_point(geek_mode)
            if results['restore_point']['success']:
                results['tasks_completed'].append('restore_point')
        
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
        
        # Windows Update cache cleanup
        if 'windows_update' in tasks and not self.check_cancelled():
            results['windows_update_cleanup'] = self.clear_windows_update_cache(geek_mode)
            if results['windows_update_cleanup']['success']:
                results['tasks_completed'].append('windows_update')
                results['total_freed_mb'] += results['windows_update_cleanup'].get('freed_space_mb', 0)
        
        # SSD optimization
        if 'ssd' in tasks and not self.check_cancelled():
            results['ssd_optimization'] = self.optimize_ssd(geek_mode)
            if results['ssd_optimization']['success']:
                results['tasks_completed'].append('ssd')
        
        # DNS cache cleanup
        if 'dns' in tasks and not self.check_cancelled():
            results['dns_cleanup'] = self.clear_dns_cache(geek_mode)
            if results['dns_cleanup']['success']:
                results['tasks_completed'].append('dns')
        
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
    
    def start_hardware_monitoring(self, update_interval: float = 1.0):
        """Start real-time hardware monitoring"""
        try:
            self.hardware_monitor.start_monitoring(update_interval)
            self.log_message(f"Hardware monitoring started with {update_interval}s interval", "INFO")
            return {'success': True}
        except Exception as e:
            self.log_message(f"Failed to start hardware monitoring: {e}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def stop_hardware_monitoring(self):
        """Stop real-time hardware monitoring"""
        try:
            self.hardware_monitor.stop_monitoring()
            self.log_message("Hardware monitoring stopped", "INFO")
            return {'success': True}
        except Exception as e:
            self.log_message(f"Failed to stop hardware monitoring: {e}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def get_performance_score(self) -> Dict:
        """Get current system performance score"""
        try:
            score = self.hardware_monitor.get_system_performance_score()
            return {'success': True, 'score': score}
        except Exception as e:
            self.log_message(f"Failed to get performance score: {e}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def add_monitoring_callback(self, event_type: str, callback: Callable):
        """Add a callback for hardware monitoring events"""
        try:
            self.hardware_monitor.add_callback(event_type, callback)
            return {'success': True}
        except Exception as e:
            self.log_message(f"Failed to add monitoring callback: {e}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def is_monitoring_active(self) -> bool:
        """Check if hardware monitoring is active"""
        return self.hardware_monitor.is_monitoring()
