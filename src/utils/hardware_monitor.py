# OptimusPC Hardware Monitoring Module

import psutil
import time
import threading
import logging
from typing import Dict, List, Callable, Optional
from .system_detector import SystemDetector

# Try to import GPUtil, but make it optional
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    GPUtil = None

class HardwareMonitor:
    """Real-time hardware monitoring and performance metrics"""
    
    def __init__(self, system_detector: SystemDetector):
        self.system_detector = system_detector
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread = None
        self.update_interval = 1.0  # seconds
        self.callbacks = {
            'cpu_update': [],
            'memory_update': [],
            'gpu_update': [],
            'disk_update': [],
            'network_update': [],
            'temperature_update': []
        }
        
    def add_callback(self, event_type: str, callback: Callable):
        """Add a callback for specific hardware events"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def remove_callback(self, event_type: str, callback: Callable):
        """Remove a callback for specific hardware events"""
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
    
    def start_monitoring(self, update_interval: float = 1.0):
        """Start real-time hardware monitoring"""
        if self.monitoring:
            self.logger.warning("Monitoring is already running")
            return
        
        self.update_interval = update_interval
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info(f"Hardware monitoring started with {update_interval}s interval")
    
    def stop_monitoring(self):
        """Stop real-time hardware monitoring"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.logger.info("Hardware monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get current hardware metrics
                metrics = self._get_current_metrics()
                
                # Trigger callbacks for each metric type
                self._trigger_callbacks('cpu_update', metrics.get('cpu', {}))
                self._trigger_callbacks('memory_update', metrics.get('memory', {}))
                self._trigger_callbacks('gpu_update', metrics.get('gpu', {}))
                self._trigger_callbacks('disk_update', metrics.get('disk', {}))
                self._trigger_callbacks('network_update', metrics.get('network', {}))
                self._trigger_callbacks('temperature_update', metrics.get('temperature', {}))
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.update_interval)
    
    def _get_current_metrics(self) -> Dict:
        """Get current hardware metrics"""
        try:
            metrics = {
                'timestamp': time.time(),
                'cpu': self._get_cpu_metrics(),
                'memory': self._get_memory_metrics(),
                'gpu': self._get_gpu_metrics(),
                'disk': self._get_disk_metrics(),
                'network': self._get_network_metrics(),
                'temperature': self._get_temperature_metrics()
            }
            return metrics
        except Exception as e:
            self.logger.error(f"Error getting current metrics: {e}")
            return {}
    
    def _get_cpu_metrics(self) -> Dict:
        """Get current CPU metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            
            return {
                'usage_percent': psutil.cpu_percent(interval=0.1),
                'per_cpu_usage': cpu_percent,
                'current_frequency': cpu_freq.current if cpu_freq else None,
                'min_frequency': cpu_freq.min if cpu_freq else None,
                'max_frequency': cpu_freq.max if cpu_freq else None,
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        except Exception as e:
            self.logger.error(f"Error getting CPU metrics: {e}")
            return {}
    
    def _get_memory_metrics(self) -> Dict:
        """Get current memory metrics"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'cached': memory.cached if hasattr(memory, 'cached') else None,
                'buffers': memory.buffers if hasattr(memory, 'buffers') else None,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent
            }
        except Exception as e:
            self.logger.error(f"Error getting memory metrics: {e}")
            return {}
    
    def _get_gpu_metrics(self) -> List[Dict]:
        """Get current GPU metrics"""
        try:
            gpus = []
            
            # Try to get GPU info using GPUtil - only if available
            if GPU_AVAILABLE and GPUtil is not None:
                try:
                    gpu_list = GPUtil.getGPUs()
                    for gpu in gpu_list:
                        gpu_info = {
                            'id': gpu.id,
                            'name': gpu.name,
                            'memory_total': gpu.memoryTotal,
                            'memory_used': gpu.memoryUsed,
                            'memory_free': gpu.memoryFree,
                            'memory_percent': gpu.memoryUtil * 100,
                            'gpu_percent': gpu.load * 100,
                            'temperature': gpu.temperature,
                            'uuid': gpu.uuid
                        }
                        gpus.append(gpu_info)
                except Exception as e:
                    self.logger.debug(f"Could not get GPU metrics via GPUtil: {e}")
            else:
                self.logger.debug("GPUtil not available for GPU monitoring")
            
            return gpus
        except Exception as e:
            self.logger.error(f"Error getting GPU metrics: {e}")
            return []
    
    def _get_disk_metrics(self) -> List[Dict]:
        """Get current disk metrics"""
        try:
            disks = []
            
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': partition_usage.total,
                        'used': partition_usage.used,
                        'free': partition_usage.free,
                        'percent': (partition_usage.used / partition_usage.total) * 100
                    }
                    disks.append(disk_info)
                except PermissionError:
                    continue
            
            return disks
        except Exception as e:
            self.logger.error(f"Error getting disk metrics: {e}")
            return []
    
    def _get_network_metrics(self) -> Dict:
        """Get current network metrics"""
        try:
            network_io = psutil.net_io_counters()
            
            return {
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv,
                'errin': network_io.errin,
                'errout': network_io.errout,
                'dropin': network_io.dropin,
                'dropout': network_io.dropout
            }
        except Exception as e:
            self.logger.error(f"Error getting network metrics: {e}")
            return {}
    
    def _get_temperature_metrics(self) -> Dict:
        """Get current temperature metrics"""
        try:
            temperatures = {}
            
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                for name, entries in temps.items():
                    temperatures[name] = []
                    for entry in entries:
                        temp_info = {
                            'label': entry.label,
                            'current': entry.current,
                            'high': entry.high,
                            'critical': entry.critical
                        }
                        temperatures[name].append(temp_info)
            
            return temperatures
        except Exception as e:
            self.logger.error(f"Error getting temperature metrics: {e}")
            return {}
    
    def _trigger_callbacks(self, event_type: str, data: any):
        """Trigger callbacks for a specific event type"""
        for callback in self.callbacks[event_type]:
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Error in callback for {event_type}: {e}")
    
    def get_system_performance_score(self) -> Dict:
        """Calculate a system performance score based on current metrics"""
        try:
            metrics = self._get_current_metrics()
            
            # CPU Score (0-100)
            cpu_usage = metrics.get('cpu', {}).get('usage_percent', 0)
            cpu_score = max(0, 100 - cpu_usage)
            
            # Memory Score (0-100)
            memory_percent = metrics.get('memory', {}).get('percent', 0)
            memory_score = max(0, 100 - memory_percent)
            
            # Disk Score (0-100)
            disk_metrics = metrics.get('disk', [])
            if disk_metrics:
                avg_disk_usage = sum(disk.get('percent', 0) for disk in disk_metrics) / len(disk_metrics)
                disk_score = max(0, 100 - avg_disk_usage)
            else:
                disk_score = 50  # Neutral score if no disk info
            
            # Overall Score
            overall_score = (cpu_score + memory_score + disk_score) / 3
            
            return {
                'overall_score': round(overall_score, 1),
                'cpu_score': round(cpu_score, 1),
                'memory_score': round(memory_score, 1),
                'disk_score': round(disk_score, 1),
                'timestamp': metrics.get('timestamp', time.time())
            }
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {e}")
            return {
                'overall_score': 0,
                'cpu_score': 0,
                'memory_score': 0,
                'disk_score': 0,
                'timestamp': time.time()
            }
    
    def get_performance_history(self, duration_minutes: int = 60) -> Dict:
        """Get performance history for the specified duration"""
        # This would typically store historical data
        # For now, return current metrics
        return self._get_current_metrics()
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is currently active"""
        return self.monitoring
