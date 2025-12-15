# OptimusPC System Detection Module

import platform
import subprocess
import json
import re
import os
import logging
from importlib.util import find_spec
from typing import Dict, List, Optional, Tuple
from pathlib import Path

if platform.system() == "Windows" and find_spec("wmi"):
    import wmi  # type: ignore[import-not-found]
else:
    class _WMIStub:  # pragma: no cover - used in non-Windows or missing dependency
        def __getattr__(self, name):
            raise RuntimeError("WMI is not available on this platform")

    wmi = _WMIStub()

from .psutil_safe import psutil

# Try to import GPUtil, but make it optional
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    GPUtil = None

class SystemDetector:
    """Comprehensive system detection and hardware information gathering"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.wmi_conn = None
        self._init_wmi()
        
    def _init_wmi(self):
        """Initialize WMI connection for Windows-specific queries"""
        try:
            if platform.system() == "Windows":
                self.wmi_conn = wmi.WMI()
        except Exception as e:
            self.logger.warning(f"Could not initialize WMI: {e}")
    
    def get_windows_version(self) -> Dict[str, str]:
        """Get detailed Windows version information"""
        try:
            version_info = {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'platform': platform.platform(),
                'win32_edition': None,
                'build_number': None,
                'display_version': None,
                'is_server': False
            }
            
            if platform.system() == "Windows":
                try:
                    # Get Windows edition and build info
                    result = subprocess.run(['systeminfo'], capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        output = result.stdout
                        
                        # Extract OS Name
                        os_name_match = re.search(r'OS Name:\s*(.+)', output)
                        if os_name_match:
                            version_info['os_name'] = os_name_match.group(1).strip()
                        
                        # Extract OS Version
                        os_version_match = re.search(r'OS Version:\s*(.+)', output)
                        if os_version_match:
                            version_info['os_version'] = os_version_match.group(1).strip()
                        
                        # Extract Build Number
                        build_match = re.search(r'Build Number:\s*(.+)', output)
                        if build_match:
                            version_info['build_number'] = build_match.group(1).strip()
                        
                        # Check if it's a server edition
                        if 'Server' in version_info.get('os_name', ''):
                            version_info['is_server'] = True
                    
                    # Get Windows 10/11 specific info
                    try:
                        result = subprocess.run(['powershell', '-Command', 
                                               'Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, WindowsBuildLabEx | ConvertTo-Json'], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            win_info = json.loads(result.stdout)
                            version_info['product_name'] = win_info.get('WindowsProductName', '')
                            version_info['display_version'] = win_info.get('WindowsVersion', '')
                            version_info['build_lab'] = win_info.get('WindowsBuildLabEx', '')
                    except:
                        pass
                        
                except Exception as e:
                    self.logger.warning(f"Could not get detailed Windows info: {e}")
            
            return version_info
            
        except Exception as e:
            self.logger.error(f"Error getting Windows version: {e}")
            return {'error': str(e)}
    
    def get_cpu_info(self) -> Dict[str, any]:
        """Get comprehensive CPU information"""
        try:
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'total_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
                'min_frequency': psutil.cpu_freq().min if psutil.cpu_freq() else None,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                'cpu_percent': psutil.cpu_percent(interval=1),
                'per_cpu_percent': psutil.cpu_percent(interval=1, percpu=True),
                'cpu_times': psutil.cpu_times(),
                'per_cpu_times': psutil.cpu_times(percpu=True),
                'brand': None,
                'name': None,
                'family': None,
                'model': None,
                'stepping': None,
                'microcode': None,
                'cache_size': None,
                'flags': None,
                'vendor_id': None,
                'hz_advertised': None,
                'hz_actual': None,
                'hz_advertised_raw': None,
                'hz_actual_raw': None
            }
            
            # Get detailed CPU info using WMI (Windows)
            if self.wmi_conn:
                try:
                    for processor in self.wmi_conn.Win32_Processor():
                        cpu_info.update({
                            'brand': processor.Manufacturer,
                            'name': processor.Name,
                            'family': processor.Family,
                            'model': processor.Model,
                            'stepping': processor.Stepping,
                            'microcode': processor.MicrocodeVersion,
                            'cache_size': processor.L3CacheSize,
                            'flags': processor.Characteristics,
                            'vendor_id': processor.VendorId,
                            'hz_advertised': processor.MaxClockSpeed,
                            'hz_actual': processor.CurrentClockSpeed,
                            'hz_advertised_raw': processor.MaxClockSpeed,
                            'hz_actual_raw': processor.CurrentClockSpeed
                        })
                        break  # Get first processor info
                except Exception as e:
                    self.logger.warning(f"Could not get detailed CPU info via WMI: {e}")
            
            # Fallback to platform info
            if not cpu_info['name']:
                cpu_info['name'] = platform.processor()
            
            return cpu_info
            
        except Exception as e:
            self.logger.error(f"Error getting CPU info: {e}")
            return {'error': str(e)}
    
    def get_memory_info(self) -> Dict[str, any]:
        """Get comprehensive memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_info = {
                'total': memory.total or 0,
                'available': memory.available or 0,
                'used': memory.used or 0,
                'free': memory.free or 0,
                'percent': memory.percent or 0,
                'cached': memory.cached if hasattr(memory, 'cached') and memory.cached is not None else 0,
                'buffers': memory.buffers if hasattr(memory, 'buffers') and memory.buffers is not None else 0,
                'swap_total': swap.total or 0,
                'swap_used': swap.used or 0,
                'swap_free': swap.free or 0,
                'swap_percent': swap.percent or 0,
                'memory_slots': None,
                'memory_modules': [],
                'memory_speed': None,
                'memory_type': None
            }
            
            # Get detailed memory info using WMI (Windows)
            if self.wmi_conn:
                try:
                    # Get physical memory info
                    for mem in self.wmi_conn.Win32_PhysicalMemory():
                        memory_module = {
                            'capacity': mem.Capacity or 0,
                            'speed': mem.Speed or 0,
                            'manufacturer': mem.Manufacturer or 'Unknown',
                            'part_number': mem.PartNumber or 'Unknown',
                            'serial_number': mem.SerialNumber or 'Unknown',
                            'memory_type': mem.MemoryType or 0,
                            'form_factor': mem.FormFactor or 0,
                            'bank_label': mem.BankLabel or 'Unknown',
                            'device_locator': mem.DeviceLocator or 'Unknown',
                            'tag': mem.Tag or 'Unknown'
                        }
                        memory_info['memory_modules'].append(memory_module)
                    
                    # Get memory array info
                    for mem_array in self.wmi_conn.Win32_PhysicalMemoryArray():
                        memory_info['memory_slots'] = mem_array.MemoryDevices
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Could not get detailed memory info via WMI: {e}")
            
            return memory_info
            
        except Exception as e:
            self.logger.error(f"Error getting memory info: {e}")
            return {'error': str(e)}
    
    def get_gpu_info(self) -> List[Dict[str, any]]:
        """Get comprehensive GPU information"""
        try:
            gpus = []
            
            # Try to get GPU info using GPUtil (NVIDIA GPUs) - only if available
            if GPU_AVAILABLE and GPUtil is not None:
                try:
                    gpu_list = GPUtil.getGPUs()
                    for gpu in gpu_list:
                        gpu_info = {
                            'id': gpu.id or 0,
                            'name': gpu.name or 'Unknown GPU',
                            'driver': gpu.driver or 'Unknown',
                            'memory_total': gpu.memoryTotal or 0,
                            'memory_used': gpu.memoryUsed or 0,
                            'memory_free': gpu.memoryFree or 0,
                            'memory_percent': (gpu.memoryUtil or 0) * 100,
                            'gpu_percent': (gpu.load or 0) * 100,
                            'temperature': gpu.temperature or 0,
                            'uuid': gpu.uuid or 'Unknown',
                            'vendor': 'NVIDIA'
                        }
                        gpus.append(gpu_info)
                except Exception as e:
                    self.logger.warning(f"Could not get GPU info via GPUtil: {e}")
            else:
                self.logger.info("GPUtil not available, using WMI for GPU detection")
            
            # Get GPU info using WMI (Windows)
            if self.wmi_conn:
                try:
                    for gpu in self.wmi_conn.Win32_VideoController():
                        if gpu.Name and gpu.Name != "Microsoft Basic Display Adapter":
                            gpu_info = {
                                'name': gpu.Name or 'Unknown GPU',
                                'driver_version': gpu.DriverVersion or 'Unknown',
                                'driver_date': gpu.DriverDate or 'Unknown',
                                'video_memory': gpu.VideoMemoryType or 0,
                                'video_processor': gpu.VideoProcessor or 'Unknown',
                                'video_architecture': gpu.VideoArchitecture or 0,
                                'video_memory_type': gpu.VideoMemoryType or 0,
                                'adapter_ram': gpu.AdapterRAM or 0,
                                'adapter_dac_type': gpu.AdapterDACType or 'Unknown',
                                'monitor_manufacturer': gpu.MonitorManufacturerName or 'Unknown',
                                'monitor_type': gpu.MonitorType or 'Unknown',
                                'pnp_device_id': gpu.PNPDeviceID or 'Unknown',
                                'status': gpu.Status or 'Unknown',
                                'availability': gpu.Availability or 'Unknown',
                                'vendor': self._get_gpu_vendor(gpu.Name or 'Unknown')
                            }
                            gpus.append(gpu_info)
                except Exception as e:
                    self.logger.warning(f"Could not get GPU info via WMI: {e}")
            
            # Remove duplicates based on name
            unique_gpus = []
            seen_names = set()
            for gpu in gpus:
                if gpu['name'] not in seen_names:
                    unique_gpus.append(gpu)
                    seen_names.add(gpu['name'])
            
            return unique_gpus
            
        except Exception as e:
            self.logger.error(f"Error getting GPU info: {e}")
            return []
    
    def _get_gpu_vendor(self, gpu_name: str) -> str:
        """Determine GPU vendor from name"""
        gpu_name_lower = gpu_name.lower()
        if 'nvidia' in gpu_name_lower or 'geforce' in gpu_name_lower or 'quadro' in gpu_name_lower:
            return 'NVIDIA'
        elif 'amd' in gpu_name_lower or 'radeon' in gpu_name_lower:
            return 'AMD'
        elif 'intel' in gpu_name_lower or 'iris' in gpu_name_lower or 'uhd' in gpu_name_lower:
            return 'Intel'
        else:
            return 'Unknown'
    
    def get_disk_info(self) -> List[Dict[str, any]]:
        """Get comprehensive disk information"""
        try:
            disks = []
            
            # Get basic disk info using psutil
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'total': partition_usage.total,
                        'used': partition_usage.used,
                        'free': partition_usage.free,
                        'percent': (partition_usage.used / partition_usage.total) * 100,
                        'serial_number': None,
                        'model': None,
                        'size': None,
                        'interface_type': None,
                        'firmware_version': None,
                        'health_status': None,
                        'temperature': None
                    }
                    disks.append(disk_info)
                except PermissionError:
                    continue
            
            # Get detailed disk info using WMI (Windows)
            if self.wmi_conn:
                try:
                    for disk in self.wmi_conn.Win32_DiskDrive():
                        # Find matching partition
                        for disk_info in disks:
                            if disk.DeviceID.replace('\\', '') in disk_info['device']:
                                disk_info.update({
                                    'serial_number': disk.SerialNumber,
                                    'model': disk.Model,
                                    'size': disk.Size,
                                    'interface_type': disk.InterfaceType,
                                    'firmware_version': disk.FirmwareRevision,
                                    'status': disk.Status,
                                    'availability': disk.Availability,
                                    'media_type': disk.MediaType,
                                    'partitions': disk.Partitions,
                                    'scsi_target_id': disk.SCSITargetId,
                                    'scsi_logical_unit': disk.SCSILogicalUnit,
                                    'scsi_port': disk.SCSIPort,
                                    'scsi_bus': disk.SCSIBus
                                })
                                break
                except Exception as e:
                    self.logger.warning(f"Could not get detailed disk info via WMI: {e}")
            
            return disks
            
        except Exception as e:
            self.logger.error(f"Error getting disk info: {e}")
            return []
    
    def get_network_info(self) -> Dict[str, any]:
        """Get comprehensive network information"""
        try:
            network_info = {
                'interfaces': [],
                'connections': [],
                'dns_servers': [],
                'gateway': None,
                'ip_address': None,
                'mac_address': None
            }
            
            # Get network interfaces
            for interface_name, interface_addresses in psutil.net_if_addrs().items():
                interface_info = {
                    'name': interface_name,
                    'addresses': []
                }
                
                for address in interface_addresses:
                    addr_info = {
                        'family': str(address.family),
                        'address': address.address,
                        'netmask': address.netmask,
                        'broadcast': address.broadcast,
                        'ptp': address.ptp
                    }
                    interface_info['addresses'].append(addr_info)
                
                network_info['interfaces'].append(interface_info)
            
            # Get network connections
            for conn in psutil.net_connections(kind='inet'):
                conn_info = {
                    'fd': conn.fd,
                    'family': str(conn.family),
                    'type': str(conn.type),
                    'laddr': conn.laddr,
                    'raddr': conn.raddr,
                    'status': conn.status,
                    'pid': conn.pid
                }
                network_info['connections'].append(conn_info)
            
            # Get DNS and gateway info using WMI (Windows)
            if self.wmi_conn:
                try:
                    # Get DNS servers
                    for adapter in self.wmi_conn.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                        if adapter.DNSServerSearchOrder:
                            network_info['dns_servers'].extend(adapter.DNSServerSearchOrder)
                        if adapter.DefaultIPGateway:
                            network_info['gateway'] = adapter.DefaultIPGateway[0]
                        if adapter.IPAddress:
                            network_info['ip_address'] = adapter.IPAddress[0]
                        if adapter.MACAddress:
                            network_info['mac_address'] = adapter.MACAddress
                        break
                except Exception as e:
                    self.logger.warning(f"Could not get network info via WMI: {e}")
            
            return network_info
            
        except Exception as e:
            self.logger.error(f"Error getting network info: {e}")
            return {'error': str(e)}
    
    def get_system_summary(self) -> Dict[str, any]:
        """Get a comprehensive system summary"""
        try:
            summary = {
                'timestamp': psutil.boot_time(),
                'uptime': psutil.boot_time(),
                'windows_version': self.get_windows_version(),
                'cpu': self.get_cpu_info(),
                'memory': self.get_memory_info(),
                'gpu': self.get_gpu_info(),
                'disk': self.get_disk_info(),
                'network': self.get_network_info(),
                'processes': len(psutil.pids()),
                'users': len(psutil.users()),
                'boot_time': psutil.boot_time()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting system summary: {e}")
            return {'error': str(e)}
    
    def get_windows_compatibility_info(self) -> Dict[str, any]:
        """Get Windows version compatibility information for optimization commands"""
        try:
            windows_info = self.get_windows_version()
            compatibility = {
                'version': windows_info.get('release', 'Unknown'),
                'build': windows_info.get('build_number', 'Unknown'),
                'is_server': windows_info.get('is_server', False),
                'supports_powershell': True,
                'supports_wsl': False,
                'supports_hyper_v': False,
                'supports_windows_defender': True,
                'supports_windows_update': True,
                'supports_system_restore': True,
                'recommended_commands': []
            }
            
            # Determine compatibility based on Windows version
            version = windows_info.get('release', '')
            build = windows_info.get('build_number', '')
            
            if version in ['10', '11']:
                compatibility['supports_wsl'] = True
                compatibility['supports_hyper_v'] = True
                compatibility['recommended_commands'].extend([
                    'Get-ComputerInfo',
                    'Get-PhysicalDisk',
                    'Get-Disk',
                    'Get-Partition',
                    'Get-Volume',
                    'Get-WmiObject',
                    'Get-CimInstance'
                ])
            elif version in ['7', '8', '8.1']:
                compatibility['recommended_commands'].extend([
                    'wmic',
                    'systeminfo',
                    'defrag',
                    'sfc /scannow',
                    'chkdsk'
                ])
            
            # Add Windows Server specific commands
            if compatibility['is_server']:
                compatibility['recommended_commands'].extend([
                    'Get-WindowsFeature',
                    'Get-Service',
                    'Get-WmiObject -Class Win32_Service'
                ])
            
            return compatibility
            
        except Exception as e:
            self.logger.error(f"Error getting Windows compatibility info: {e}")
            return {'error': str(e)}
    
    def format_memory_size(self, bytes_value: int) -> str:
        """Format memory size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def format_frequency(self, hz_value: int) -> str:
        """Format frequency in human readable format"""
        if hz_value is None:
            return "Unknown"
        
        if hz_value >= 1000000000:  # GHz
            return f"{hz_value / 1000000000:.2f} GHz"
        elif hz_value >= 1000000:  # MHz
            return f"{hz_value / 1000000:.2f} MHz"
        else:  # Hz
            return f"{hz_value} Hz"
