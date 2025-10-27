# OptimusPC GUI Main Window

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from typing import Dict, Any
from .progress_window import ProgressWindow

class OptimusGUI:
    """Main GUI application for OptimusPC"""
    
    def __init__(self, optimizer):
        self.optimizer = optimizer
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.running = False
        self.progress_window = None
        self.geek_mode = False
        self.monitoring = False
        self.performance_score = 0
        
        # Setup optimizer callbacks
        self.optimizer.on_task_start = self.on_task_start
        self.optimizer.on_task_complete = self.on_task_complete
        self.optimizer.on_log_message = self.on_log_message
        
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("OptimusPC - PC Optimization Tool")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="OptimusPC", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # System Info Frame
        info_frame = ttk.LabelFrame(main_frame, text="System Information", padding="10")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        self.create_system_info_widgets(info_frame)
        
        # Optimization Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Optimization Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.create_optimization_widgets(options_frame)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.create_progress_widgets(progress_frame)
        
        # Control Buttons Frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        self.create_control_widgets(control_frame)
        
        # Results Frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.create_results_widgets(results_frame)
        
        # Load initial system info
        self.update_system_info()
        
    def create_system_info_widgets(self, parent):
        """Create system information display widgets"""
        # Create a scrollable frame for system info
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Windows Version Info
        ttk.Label(scrollable_frame, text="Windows Version:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.windows_label = ttk.Label(scrollable_frame, text="Loading...", font=("Arial", 9))
        self.windows_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # CPU Info
        ttk.Label(scrollable_frame, text="CPU:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.cpu_label = ttk.Label(scrollable_frame, text="Loading...", font=("Arial", 9))
        self.cpu_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Memory Info
        ttk.Label(scrollable_frame, text="Memory:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.memory_label = ttk.Label(scrollable_frame, text="Loading...", font=("Arial", 9))
        self.memory_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # GPU Info
        ttk.Label(scrollable_frame, text="GPU:", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.gpu_label = ttk.Label(scrollable_frame, text="Loading...", font=("Arial", 9))
        self.gpu_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Disk Info
        ttk.Label(scrollable_frame, text="Storage:", font=("Arial", 9, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.disk_label = ttk.Label(scrollable_frame, text="Loading...", font=("Arial", 9))
        self.disk_label.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Network Info
        ttk.Label(scrollable_frame, text="Network:", font=("Arial", 9, "bold")).grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        self.network_label = ttk.Label(scrollable_frame, text="Loading...", font=("Arial", 9))
        self.network_label.grid(row=5, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Performance Score
        ttk.Label(scrollable_frame, text="Performance Score:", font=("Arial", 9, "bold")).grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        self.performance_label = ttk.Label(scrollable_frame, text="Loading...", font=("Arial", 9))
        self.performance_label.grid(row=6, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # System Status
        ttk.Label(scrollable_frame, text="System Status:", font=("Arial", 9, "bold")).grid(row=7, column=0, sticky=tk.W, pady=(0, 5))
        self.status_label = ttk.Label(scrollable_frame, text="Loading...", font=("Arial", 9))
        self.status_label.grid(row=7, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Control buttons frame
        control_buttons_frame = ttk.Frame(parent)
        control_buttons_frame.pack(pady=(10, 0))
        
        # Refresh button
        refresh_btn = ttk.Button(control_buttons_frame, text="Refresh System Info", command=self.update_system_info)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Monitoring toggle button
        self.monitor_btn = ttk.Button(control_buttons_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.monitor_btn.pack(side=tk.LEFT)
        
    def create_optimization_widgets(self, parent):
        """Create optimization option widgets"""
        # Checkboxes for different optimization types
        self.restore_point_var = tk.BooleanVar(value=True)
        self.memory_var = tk.BooleanVar(value=True)
        self.temp_var = tk.BooleanVar(value=True)
        self.cache_var = tk.BooleanVar(value=True)
        self.windows_update_var = tk.BooleanVar(value=True)
        self.ssd_var = tk.BooleanVar(value=True)
        self.dns_var = tk.BooleanVar(value=True)
        self.startup_var = tk.BooleanVar(value=False)
        self.geek_mode_var = tk.BooleanVar(value=False)
        
        # Basic optimizations
        ttk.Checkbutton(parent, text="Create Restore Point", 
                       variable=self.restore_point_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(parent, text="Memory Optimization", 
                       variable=self.memory_var).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(parent, text="Clear Temporary Files", 
                       variable=self.temp_var).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(parent, text="Clear Browser Cache", 
                       variable=self.cache_var).grid(row=1, column=1, sticky=tk.W)
        
        # Advanced optimizations
        ttk.Checkbutton(parent, text="Windows Update Cleanup", 
                       variable=self.windows_update_var).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(parent, text="SSD Optimization", 
                       variable=self.ssd_var).grid(row=2, column=1, sticky=tk.W)
        ttk.Checkbutton(parent, text="DNS Cache Cleanup", 
                       variable=self.dns_var).grid(row=3, column=0, sticky=tk.W)
        ttk.Checkbutton(parent, text="Analyze Startup Programs", 
                       variable=self.startup_var).grid(row=3, column=1, sticky=tk.W)
        
        # Geek mode toggle
        geek_frame = ttk.Frame(parent)
        geek_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        ttk.Checkbutton(geek_frame, text="Geek Mode (Detailed Logging)", 
                       variable=self.geek_mode_var).pack(side=tk.LEFT)
        
        # Info button for geek mode
        info_btn = ttk.Button(geek_frame, text="?", width=3, 
                            command=self.show_geek_mode_info)
        info_btn.pack(side=tk.LEFT, padx=(5, 0))
        
    def create_progress_widgets(self, parent):
        """Create progress display widgets"""
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(parent, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(parent, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def create_control_widgets(self, parent):
        """Create control button widgets"""
        self.start_btn = ttk.Button(parent, text="Start Optimization", 
                                   command=self.start_optimization)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(parent, text="Stop", 
                                  command=self.stop_optimization, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        settings_btn = ttk.Button(parent, text="Settings", 
                                 command=self.open_settings)
        settings_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        system_info_btn = ttk.Button(parent, text="System Info", 
                                    command=self.show_detailed_system_info)
        system_info_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        about_btn = ttk.Button(parent, text="About", 
                              command=self.show_about)
        about_btn.pack(side=tk.LEFT)
        
    def create_results_widgets(self, parent):
        """Create results display widgets"""
        # Create text widget with scrollbar
        text_frame = ttk.Frame(parent)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.results_text = tk.Text(text_frame, wrap=tk.WORD, height=10)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def update_system_info(self):
        """Update system information display"""
        try:
            info = self.optimizer.get_system_info()
            
            if info and 'error' not in info:
                # Windows Version Info
                windows_info = info.get('windows_version', {})
                windows_text = f"{windows_info.get('os_name', 'Unknown')} {windows_info.get('release', '')} (Build {windows_info.get('build_number', 'Unknown')})"
                self.windows_label.config(text=windows_text)
                
                # CPU Info
                cpu_info = info.get('cpu', {})
                if cpu_info and 'error' not in cpu_info:
                    cpu_name = cpu_info.get('name', 'Unknown CPU')
                    cpu_cores = cpu_info.get('physical_cores', cpu_info.get('cpu_count', 'N/A'))
                    cpu_usage = info.get('cpu_percent', 0)
                    cpu_freq = cpu_info.get('current_frequency', 0)
                    
                    if cpu_freq and cpu_freq > 0:
                        freq_text = f"{cpu_freq / 1000:.1f} GHz" if cpu_freq > 1000 else f"{cpu_freq:.0f} MHz"
                        cpu_text = f"{cpu_name} ({cpu_cores} cores, {freq_text}, {cpu_usage:.1f}% usage)"
                    else:
                        cpu_text = f"{cpu_name} ({cpu_cores} cores, {cpu_usage:.1f}% usage)"
                else:
                    cpu_text = f"{info.get('cpu_count', 'N/A')} cores, {info.get('cpu_percent', 0):.1f}% usage"
                self.cpu_label.config(text=cpu_text)
                
                # Memory Info
                memory_info = info.get('memory', {})
                if memory_info and 'error' not in memory_info:
                    total_mem = memory_info.get('total', 0) or 0
                    available_mem = memory_info.get('available', 0) or 0
                    used_mem = memory_info.get('used', 0) or 0
                    memory_percent = memory_info.get('percent', 0) or 0
                    
                    total_gb = total_mem / (1024**3)
                    available_gb = available_mem / (1024**3)
                    used_gb = used_mem / (1024**3)
                    
                    memory_text = f"{memory_percent:.1f}% used ({used_gb:.1f} GB / {total_gb:.1f} GB, {available_gb:.1f} GB available)"
                else:
                    memory_total = info.get('memory_total', 0) or 0
                    memory_available = info.get('memory_available', 0) or 0
                    memory_percent = info.get('memory_percent', 0) or 0
                    memory_text = f"{memory_percent:.1f}% used ({memory_available / (1024**3):.1f} GB available)"
                self.memory_label.config(text=memory_text)
                
                # GPU Info
                gpu_info = info.get('gpu', [])
                if gpu_info and len(gpu_info) > 0:
                    gpu = gpu_info[0]  # Get first GPU
                    gpu_name = gpu.get('name', 'Unknown GPU')
                    gpu_memory = gpu.get('memory_total', 0) or 0
                    gpu_usage = gpu.get('gpu_percent', 0) or 0
                    gpu_temp = gpu.get('temperature', 0) or 0
                    
                    if gpu_memory > 0:
                        gpu_mem_gb = gpu_memory / 1024
                        gpu_text = f"{gpu_name} ({gpu_mem_gb:.1f} GB"
                    else:
                        gpu_text = f"{gpu_name} ("
                    
                    if gpu_usage > 0:
                        gpu_text += f", {gpu_usage:.1f}% usage"
                    if gpu_temp > 0:
                        gpu_text += f", {gpu_temp}°C"
                    gpu_text += ")"
                else:
                    gpu_text = "No dedicated GPU detected"
                self.gpu_label.config(text=gpu_text)
                
                # Disk Info
                disk_info = info.get('disk', [])
                if disk_info and len(disk_info) > 0:
                    disk_texts = []
                    for disk in disk_info[:3]:  # Show first 3 disks
                        device = disk.get('device', 'Unknown')
                        total = disk.get('total', 0) or 0
                        free = disk.get('free', 0) or 0
                        percent = disk.get('percent', 0) or 0
                        model = disk.get('model', '')
                        
                        if total > 0:
                            total_gb = total / (1024**3)
                            free_gb = free / (1024**3)
                            disk_text = f"{device} ({model}): {percent:.1f}% used ({free_gb:.1f} GB free / {total_gb:.1f} GB)"
                            disk_texts.append(disk_text)
                    
                    if disk_texts:
                        disk_text = " | ".join(disk_texts)
                    else:
                        disk_percent = info.get('disk_percent', 0) or 0
                        disk_free = info.get('disk_free', 0) or 0
                        disk_text = f"{disk_percent:.1f}% used ({disk_free / (1024**3):.1f} GB free)"
                else:
                    disk_percent = info.get('disk_percent', 0) or 0
                    disk_free = info.get('disk_free', 0) or 0
                    disk_text = f"{disk_percent:.1f}% used ({disk_free / (1024**3):.1f} GB free)"
                self.disk_label.config(text=disk_text)
                
                # Network Info
                network_info = info.get('network', {})
                if network_info and 'error' not in network_info:
                    ip_address = network_info.get('ip_address', 'Unknown')
                    mac_address = network_info.get('mac_address', 'Unknown')
                    dns_servers = network_info.get('dns_servers', [])
                    
                    network_text = f"IP: {ip_address}"
                    if dns_servers:
                        network_text += f" | DNS: {', '.join(dns_servers[:2])}"
                else:
                    network_text = "Network info unavailable"
                self.network_label.config(text=network_text)
                
                # System Status
                processes = info.get('processes', 0)
                users = info.get('users', 0)
                boot_time = info.get('boot_time', 0)
                
                if boot_time > 0:
                    import time
                    uptime_seconds = time.time() - boot_time
                    uptime_hours = uptime_seconds / 3600
                    uptime_days = uptime_hours / 24
                    
                    if uptime_days >= 1:
                        uptime_text = f"{uptime_days:.1f} days"
                    else:
                        uptime_text = f"{uptime_hours:.1f} hours"
                else:
                    uptime_text = "Unknown"
                
                status_text = f"Uptime: {uptime_text} | Processes: {processes} | Users: {users}"
                self.status_label.config(text=status_text)
                
                # Performance Score
                try:
                    score_result = self.optimizer.get_performance_score()
                    if score_result.get('success'):
                        score = score_result.get('score', {})
                        overall_score = score.get('overall_score', 0)
                        cpu_score = score.get('cpu_score', 0)
                        memory_score = score.get('memory_score', 0)
                        disk_score = score.get('disk_score', 0)
                        
                        # Color code the performance score
                        if overall_score >= 80:
                            color = "green"
                        elif overall_score >= 60:
                            color = "orange"
                        else:
                            color = "red"
                        
                        performance_text = f"{overall_score:.1f}/100 (CPU: {cpu_score:.1f}, RAM: {memory_score:.1f}, Disk: {disk_score:.1f})"
                        self.performance_label.config(text=performance_text, foreground=color)
                        self.performance_score = overall_score
                    else:
                        self.performance_label.config(text="Score unavailable")
                except Exception as e:
                    self.performance_label.config(text="Error calculating score")
                
            else:
                self.windows_label.config(text="Error loading info")
                self.cpu_label.config(text="Error loading info")
                self.memory_label.config(text="Error loading info")
                self.gpu_label.config(text="Error loading info")
                self.disk_label.config(text="Error loading info")
                self.network_label.config(text="Error loading info")
                self.performance_label.config(text="Error loading info")
                self.status_label.config(text="Error loading info")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load system information: {e}")
            self.windows_label.config(text="Error loading info")
            self.cpu_label.config(text="Error loading info")
            self.memory_label.config(text="Error loading info")
            self.gpu_label.config(text="Error loading info")
            self.disk_label.config(text="Error loading info")
            self.network_label.config(text="Error loading info")
            self.performance_label.config(text="Error loading info")
            self.status_label.config(text="Error loading info")
    
    def toggle_monitoring(self):
        """Toggle real-time hardware monitoring"""
        try:
            if not self.monitoring:
                # Start monitoring
                result = self.optimizer.start_hardware_monitoring(update_interval=2.0)
                if result.get('success'):
                    self.monitoring = True
                    self.monitor_btn.config(text="Stop Monitoring")
                    
                    # Add monitoring callbacks
                    self.optimizer.add_monitoring_callback('cpu_update', self.on_cpu_update)
                    self.optimizer.add_monitoring_callback('memory_update', self.on_memory_update)
                    self.optimizer.add_monitoring_callback('gpu_update', self.on_gpu_update)
                    self.optimizer.add_monitoring_callback('disk_update', self.on_disk_update)
                    
                    messagebox.showinfo("Monitoring", "Real-time monitoring started!")
                else:
                    messagebox.showerror("Error", f"Failed to start monitoring: {result.get('error', 'Unknown error')}")
            else:
                # Stop monitoring
                result = self.optimizer.stop_hardware_monitoring()
                if result.get('success'):
                    self.monitoring = False
                    self.monitor_btn.config(text="Start Monitoring")
                    messagebox.showinfo("Monitoring", "Real-time monitoring stopped!")
                else:
                    messagebox.showerror("Error", f"Failed to stop monitoring: {result.get('error', 'Unknown error')}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle monitoring: {e}")
    
    def on_cpu_update(self, cpu_data):
        """Handle CPU monitoring updates"""
        try:
            if cpu_data:
                usage = cpu_data.get('usage_percent', 0)
                freq = cpu_data.get('current_frequency', 0)
                
                # Update CPU label in real-time
                if freq and freq > 0:
                    freq_text = f"{freq / 1000:.1f} GHz" if freq > 1000 else f"{freq:.0f} MHz"
                    cpu_text = f"CPU: {usage:.1f}% usage, {freq_text}"
                else:
                    cpu_text = f"CPU: {usage:.1f}% usage"
                
                self.root.after(0, lambda: self.cpu_label.config(text=cpu_text))
        except Exception as e:
            self.logger.error(f"Error updating CPU display: {e}")
    
    def on_memory_update(self, memory_data):
        """Handle memory monitoring updates"""
        try:
            if memory_data:
                total = memory_data.get('total', 0)
                used = memory_data.get('used', 0)
                available = memory_data.get('available', 0)
                percent = memory_data.get('percent', 0)
                
                total_gb = total / (1024**3)
                used_gb = used / (1024**3)
                available_gb = available / (1024**3)
                
                memory_text = f"Memory: {percent:.1f}% used ({used_gb:.1f} GB / {total_gb:.1f} GB, {available_gb:.1f} GB available)"
                self.root.after(0, lambda: self.memory_label.config(text=memory_text))
        except Exception as e:
            self.logger.error(f"Error updating memory display: {e}")
    
    def on_gpu_update(self, gpu_data):
        """Handle GPU monitoring updates"""
        try:
            if gpu_data and len(gpu_data) > 0:
                gpu = gpu_data[0]  # Get first GPU
                name = gpu.get('name', 'Unknown GPU')
                usage = gpu.get('gpu_percent', 0)
                memory_usage = gpu.get('memory_percent', 0)
                temp = gpu.get('temperature', 0)
                
                gpu_text = f"GPU: {name} ({usage:.1f}% usage, {memory_usage:.1f}% memory"
                if temp > 0:
                    gpu_text += f", {temp}°C"
                gpu_text += ")"
                
                self.root.after(0, lambda: self.gpu_label.config(text=gpu_text))
        except Exception as e:
            self.logger.error(f"Error updating GPU display: {e}")
    
    def on_disk_update(self, disk_data):
        """Handle disk monitoring updates"""
        try:
            if disk_data and len(disk_data) > 0:
                disk_texts = []
                for disk in disk_data[:3]:  # Show first 3 disks
                    device = disk.get('device', 'Unknown')
                    total = disk.get('total', 0)
                    free = disk.get('free', 0)
                    percent = disk.get('percent', 0)
                    
                    if total > 0:
                        total_gb = total / (1024**3)
                        free_gb = free / (1024**3)
                        disk_text = f"{device}: {percent:.1f}% used ({free_gb:.1f} GB free / {total_gb:.1f} GB)"
                        disk_texts.append(disk_text)
                
                if disk_texts:
                    disk_text = " | ".join(disk_texts)
                    self.root.after(0, lambda: self.disk_label.config(text=disk_text))
        except Exception as e:
            self.logger.error(f"Error updating disk display: {e}")
    
    def start_optimization(self):
        """Start optimization process"""
        if self.running:
            return
            
        # Check if any optimization is selected
        if not any([self.restore_point_var.get(), self.memory_var.get(), self.temp_var.get(), 
                   self.cache_var.get(), self.windows_update_var.get(), self.ssd_var.get(),
                   self.dns_var.get(), self.startup_var.get()]):
            messagebox.showwarning("No Options Selected", 
                                 "Please select at least one optimization option.")
            return
            
        self.running = True
        self.geek_mode = self.geek_mode_var.get()
        
        # Create progress window
        self.progress_window = ProgressWindow(self.root, "Optimization Progress")
        
        # Setup tasks based on selected options
        tasks = []
        if self.restore_point_var.get():
            tasks.append({'id': 'restore_point', 'name': 'Create System Restore Point', 
                         'description': 'Creating restore point for safety before optimization'})
        if self.memory_var.get():
            tasks.append({'id': 'memory', 'name': 'Memory Optimization', 
                         'description': 'Optimizing RAM usage and clearing system cache'})
        if self.temp_var.get():
            tasks.append({'id': 'temp', 'name': 'Temporary Files Cleanup', 
                         'description': 'Removing temporary files from system directories'})
        if self.cache_var.get():
            tasks.append({'id': 'cache', 'name': 'Browser Cache Cleanup', 
                         'description': 'Clearing browser cache files'})
        if self.windows_update_var.get():
            tasks.append({'id': 'windows_update', 'name': 'Windows Update Cleanup', 
                         'description': 'Clearing Windows Update cache and temporary files'})
        if self.ssd_var.get():
            tasks.append({'id': 'ssd', 'name': 'SSD Optimization', 
                         'description': 'Optimizing SSD performance with TRIM and health checks'})
        if self.dns_var.get():
            tasks.append({'id': 'dns', 'name': 'DNS Cache Cleanup', 
                         'description': 'Clearing DNS cache and optimizing network settings'})
        if self.startup_var.get():
            tasks.append({'id': 'startup', 'name': 'Startup Programs Analysis', 
                         'description': 'Analyzing startup programs and services'})
        
        self.progress_window.set_tasks(tasks)
        self.progress_window.on_all_complete = self.on_optimization_complete
        
        # Disable main window controls
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Start optimization in separate thread
        thread = threading.Thread(target=self.run_optimization)
        thread.daemon = True
        thread.start()
    
    def stop_optimization(self):
        """Stop optimization process"""
        self.running = False
        self.optimizer.cancel_optimization()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_var.set("Stopped")
        
        if self.progress_window and not self.progress_window.is_closed():
            self.progress_window.cancel_optimization()
    
    def on_task_start(self, task_id: str, task_name: str):
        """Callback when a task starts"""
        if self.progress_window and not self.progress_window.is_closed():
            self.progress_window.update_task_status(task_id, 'running')
    
    def on_task_complete(self, task_id: str, details: str, freed_space: float):
        """Callback when a task completes"""
        if self.progress_window and not self.progress_window.is_closed():
            self.progress_window.update_task_status(task_id, 'completed', details, freed_space)
    
    def on_log_message(self, message: str, level: str, geek_mode: bool):
        """Callback for log messages"""
        # Only show geek mode messages if geek mode is enabled
        if geek_mode and not self.geek_mode:
            return
            
        # Update results text with log messages
        if level in ['INFO', 'WARNING', 'ERROR']:
            self.root.after(0, lambda: self.add_log_to_results(message, level))
    
    def add_log_to_results(self, message: str, level: str):
        """Add log message to results text"""
        if level == 'ERROR':
            color = 'red'
        elif level == 'WARNING':
            color = 'orange'
        else:
            color = 'black'
            
        self.results_text.insert(tk.END, f"{message}\n")
        
        # Apply color if possible
        try:
            start_line = self.results_text.index(tk.END + "-2l")
            end_line = self.results_text.index(tk.END + "-1l")
            self.results_text.tag_add(level, start_line, end_line)
            self.results_text.tag_config(level, foreground=color)
        except:
            pass
            
        self.results_text.see(tk.END)
    
    def on_optimization_complete(self):
        """Callback when all optimization tasks are complete"""
        self.progress_var.set("Optimization Complete!")
        self.update_system_info()
    
    def run_optimization(self):
        """Run optimization process in background thread"""
        try:
            # Determine which tasks to run
            tasks = []
            if self.restore_point_var.get():
                tasks.append('restore_point')
            if self.memory_var.get():
                tasks.append('memory')
            if self.temp_var.get():
                tasks.append('temp')
            if self.cache_var.get():
                tasks.append('cache')
            if self.windows_update_var.get():
                tasks.append('windows_update')
            if self.ssd_var.get():
                tasks.append('ssd')
            if self.dns_var.get():
                tasks.append('dns')
            if self.startup_var.get():
                tasks.append('startup')
            
            # Run optimization
            results = self.optimizer.run_full_optimization(self.geek_mode, tasks)
            
            if self.running:
                self.root.after(0, lambda: self.display_results(results))
            
        except Exception as e:
            error_msg = f"Optimization error: {e}"
            self.root.after(0, lambda: messagebox.showerror("Optimization Error", error_msg))
        finally:
            self.running = False
            self.root.after(0, self.stop_optimization)
    
    def display_results(self, results: Dict[str, Any]):
        """Display optimization results"""
        self.results_text.delete(1.0, tk.END)
        
        output = "=== OptimusPC Optimization Results ===\n\n"
        
        total_freed = results.get('total_freed_mb', 0)
        tasks_completed = results.get('tasks_completed', [])
        
        # Memory results
        if 'memory_optimization' in results:
            mem_result = results['memory_optimization']
            if mem_result.get('success'):
                freed_mb = mem_result.get('freed_memory_mb', 0)
                output += f"✅ Memory Optimization:\n"
                output += f"  - Freed: {freed_mb:.2f} MB\n"
                output += f"  - Usage: {mem_result.get('initial_percent', 0):.1f}% → {mem_result.get('final_percent', 0):.1f}%\n"
                if 'collected_objects' in mem_result:
                    output += f"  - Objects collected: {mem_result['collected_objects']}\n"
                output += "\n"
            else:
                output += f"❌ Memory Optimization: Failed - {mem_result.get('error', 'Unknown error')}\n\n"
        
        # Temp file results
        if 'temp_cleanup' in results:
            temp_result = results['temp_cleanup']
            if temp_result.get('success'):
                freed_mb = temp_result.get('freed_space_mb', 0)
                output += f"✅ Temporary Files Cleanup:\n"
                output += f"  - Freed: {freed_mb:.2f} MB\n"
                output += f"  - Files removed: {temp_result.get('files_removed', 0)}\n\n"
            else:
                output += f"❌ Temporary Files Cleanup: Failed\n\n"
        
        # Browser cache results
        if 'browser_cache' in results:
            cache_result = results['browser_cache']
            if cache_result.get('success'):
                freed_mb = cache_result.get('total_freed_mb', 0)
                output += f"✅ Browser Cache Cleanup:\n"
                output += f"  - Total freed: {freed_mb:.2f} MB\n"
                output += f"  - Files removed: {cache_result.get('total_files_removed', 0)}\n\n"
            else:
                output += f"❌ Browser Cache Cleanup: Failed\n\n"
        
        # Startup analysis results
        if 'startup_analysis' in results:
            startup_result = results['startup_analysis']
            if startup_result.get('success'):
                count = startup_result.get('count', 0)
                output += f"✅ Startup Programs Analysis:\n"
                output += f"  - Found {count} startup programs\n"
                output += f"  - Consider disabling unnecessary programs for faster boot\n\n"
            else:
                output += f"❌ Startup Analysis: Failed - {startup_result.get('error', 'Unknown error')}\n\n"
        
        # Windows Update cleanup results
        if 'windows_update_cleanup' in results:
            update_result = results['windows_update_cleanup']
            if update_result.get('success'):
                freed_mb = update_result.get('freed_space_mb', 0)
                output += f"✅ Windows Update Cleanup:\n"
                output += f"  - Freed: {freed_mb:.2f} MB\n"
                output += f"  - Files removed: {update_result.get('files_removed', 0)}\n\n"
            else:
                output += f"❌ Windows Update Cleanup: Failed\n\n"
        
        # SSD optimization results
        if 'ssd_optimization' in results:
            ssd_result = results['ssd_optimization']
            if ssd_result.get('success'):
                ssd_details = ssd_result.get('results', {})
                output += f"✅ SSD Optimization:\n"
                if ssd_details.get('trim_executed'):
                    output += f"  - TRIM command executed\n"
                if ssd_details.get('defrag_skipped'):
                    output += f"  - Defragmentation skipped (SSD detected)\n"
                if ssd_details.get('health_check'):
                    output += f"  - Disk health check completed\n"
                output += "\n"
            else:
                output += f"❌ SSD Optimization: Failed - {ssd_result.get('error', 'Unknown error')}\n\n"
        
        # DNS cache cleanup results
        if 'dns_cleanup' in results:
            dns_result = results['dns_cleanup']
            if dns_result.get('success'):
                output += f"✅ DNS Cache Cleanup:\n"
                output += f"  - DNS cache flushed\n"
                output += f"  - Network stack reset\n\n"
            else:
                output += f"❌ DNS Cache Cleanup: Failed - {dns_result.get('error', 'Unknown error')}\n\n"
        
        # System restore point results
        if 'restore_point' in results:
            restore_result = results['restore_point']
            if restore_result.get('success'):
                output += f"✅ System Restore Point:\n"
                output += f"  - {restore_result.get('message', 'Created successfully')}\n\n"
            else:
                output += f"❌ System Restore Point: Failed - {restore_result.get('error', 'Unknown error')}\n\n"
        
        output += f"=== Summary ===\n"
        output += f"Total space freed: {total_freed:.2f} MB\n"
        output += f"Tasks completed: {len(tasks_completed)}/{len(results.get('tasks_completed', []))}\n"
        output += f"Optimization completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if results.get('cancelled'):
            output += f"⚠️ Optimization was cancelled by user\n"
        
        self.results_text.insert(tk.END, output)
        
        # Update system info after optimization
        self.root.after(1000, self.update_system_info)
    
    def show_geek_mode_info(self):
        """Show information about geek mode"""
        info_text = """Geek Mode - Detailed Logging

When enabled, Geek Mode provides:
• Detailed process information
• File-by-file deletion logs
• System call details
• Debug information
• Real-time operation tracking

This mode is useful for:
• Troubleshooting issues
• Understanding what OptimusPC is doing
• Technical analysis
• Educational purposes

Note: Geek Mode may generate more log output."""
        
        messagebox.showinfo("Geek Mode Information", info_text)
    
    def open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog will be implemented in future version.")
    
    def show_detailed_system_info(self):
        """Show detailed system information dialog"""
        try:
            # Create new window for detailed system info
            self.info_window = tk.Toplevel(self.root)
            self.info_window.title("Detailed System Information - Live")
            self.info_window.geometry("900x700")
            self.info_window.resizable(True, True)
            
            # Add close handler
            self.info_window.protocol("WM_DELETE_WINDOW", self.close_detailed_system_info)
            
            # Initialize live update variables
            self.live_update_active = True
            self.update_interval = 2000  # 2 seconds
            
            # Create the initial content
            self.create_detailed_system_info_content()
            
            # Start live updates
            self.update_detailed_system_info()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load detailed system information: {e}")
    
    def close_detailed_system_info(self):
        """Close the detailed system info window and stop live updates"""
        self.live_update_active = False
        if hasattr(self, 'info_window') and self.info_window:
            self.info_window.destroy()
    
    def create_detailed_system_info_content(self):
        """Create the content for detailed system information window"""
        try:
            info = self.optimizer.get_system_info()
            
            if not info or 'error' in info:
                messagebox.showerror("Error", "Failed to load system information")
                return
            
            # Create notebook for tabs
            self.notebook = ttk.Notebook(self.info_window)
            self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create control frame for live update controls
            control_frame = ttk.Frame(self.info_window)
            control_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
            
            # Live update toggle
            self.live_update_var = tk.BooleanVar(value=True)
            live_check = ttk.Checkbutton(control_frame, text="Live Updates", 
                                       variable=self.live_update_var)
            live_check.pack(side=tk.LEFT, padx=(0, 10))
            
            # Update interval control
            ttk.Label(control_frame, text="Update Interval:").pack(side=tk.LEFT, padx=(0, 5))
            self.interval_var = tk.StringVar(value="2")
            interval_combo = ttk.Combobox(control_frame, textvariable=self.interval_var, 
                                        values=["1", "2", "3", "5", "10"], width=5, state="readonly")
            interval_combo.pack(side=tk.LEFT, padx=(0, 10))
            interval_combo.bind("<<ComboboxSelected>>", self.on_interval_changed)
            
            # Refresh button
            refresh_btn = ttk.Button(control_frame, text="Refresh Now", 
                                   command=self.refresh_detailed_system_info)
            refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # Status label
            self.status_label = ttk.Label(control_frame, text="Live updates active")
            self.status_label.pack(side=tk.RIGHT)
            
            # Store the current info for updates
            self.current_info = info
            
            # Windows Information Tab
            self.windows_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.windows_frame, text="Windows")
            
            self.windows_text = tk.Text(self.windows_frame, wrap=tk.WORD, font=("Consolas", 9))
            self.windows_scrollbar = ttk.Scrollbar(self.windows_frame, orient=tk.VERTICAL, command=self.windows_text.yview)
            self.windows_text.configure(yscrollcommand=self.windows_scrollbar.set)
            
            self.windows_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.windows_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Windows info content
            windows_info = info.get('windows_version', {})
            windows_content = f"""Windows Version Information:
{'='*50}

Operating System: {windows_info.get('os_name', 'Unknown')}
Version: {windows_info.get('release', 'Unknown')}
Build Number: {windows_info.get('build_number', 'Unknown')}
Architecture: {windows_info.get('architecture', 'Unknown')}
Platform: {windows_info.get('platform', 'Unknown')}
Is Server: {windows_info.get('is_server', False)}
Display Version: {windows_info.get('display_version', 'Unknown')}
Product Name: {windows_info.get('product_name', 'Unknown')}
Build Lab: {windows_info.get('build_lab', 'Unknown')}

Compatibility Information:
{'='*50}

Version: {self.optimizer.windows_compatibility.get('version', 'Unknown')}
Build: {self.optimizer.windows_compatibility.get('build', 'Unknown')}
Supports PowerShell: {self.optimizer.windows_compatibility.get('supports_powershell', False)}
Supports WSL: {self.optimizer.windows_compatibility.get('supports_wsl', False)}
Supports Hyper-V: {self.optimizer.windows_compatibility.get('supports_hyper_v', False)}
Supports Windows Defender: {self.optimizer.windows_compatibility.get('supports_windows_defender', False)}
Supports Windows Update: {self.optimizer.windows_compatibility.get('supports_windows_update', False)}
Supports System Restore: {self.optimizer.windows_compatibility.get('supports_system_restore', False)}

Recommended Commands:
{', '.join(self.optimizer.windows_compatibility.get('recommended_commands', []))}
"""
            self.windows_text.insert(tk.END, windows_content)
            self.windows_text.config(state=tk.DISABLED)
            
            # CPU Information Tab
            self.cpu_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.cpu_frame, text="CPU")
            
            self.cpu_text = tk.Text(self.cpu_frame, wrap=tk.WORD, font=("Consolas", 9))
            self.cpu_scrollbar = ttk.Scrollbar(self.cpu_frame, orient=tk.VERTICAL, command=self.cpu_text.yview)
            self.cpu_text.configure(yscrollcommand=self.cpu_scrollbar.set)
            
            self.cpu_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.cpu_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # CPU info content
            cpu_info = info.get('cpu', {})
            if cpu_info and 'error' not in cpu_info:
                cpu_content = f"""CPU Information:
{'='*50}

Name: {cpu_info.get('name', 'Unknown')}
Brand: {cpu_info.get('brand', 'Unknown')}
Physical Cores: {cpu_info.get('physical_cores', 'Unknown')}
Total Cores: {cpu_info.get('total_cores', 'Unknown')}
Current Usage: {info.get('cpu_percent', 0):.1f}%
Current Frequency: {cpu_info.get('current_frequency', 0):.0f} MHz
Max Frequency: {cpu_info.get('max_frequency', 0):.0f} MHz
Min Frequency: {cpu_info.get('min_frequency', 0):.0f} MHz
Family: {cpu_info.get('family', 'Unknown')}
Model: {cpu_info.get('model', 'Unknown')}
Stepping: {cpu_info.get('stepping', 'Unknown')}
Microcode: {cpu_info.get('microcode', 'Unknown')}
Cache Size: {cpu_info.get('cache_size', 'Unknown')} KB
Vendor ID: {cpu_info.get('vendor_id', 'Unknown')}
"""
            else:
                cpu_content = f"""CPU Information:
{'='*50}

Basic Info:
Cores: {info.get('cpu_count', 'Unknown')}
Usage: {info.get('cpu_percent', 0):.1f}%

Detailed information not available.
"""
            self.cpu_text.insert(tk.END, cpu_content)
            self.cpu_text.config(state=tk.DISABLED)
            
            # Memory Information Tab
            self.memory_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.memory_frame, text="Memory")
            
            self.memory_text = tk.Text(self.memory_frame, wrap=tk.WORD, font=("Consolas", 9))
            self.memory_scrollbar = ttk.Scrollbar(self.memory_frame, orient=tk.VERTICAL, command=self.memory_text.yview)
            self.memory_text.configure(yscrollcommand=self.memory_scrollbar.set)
            
            self.memory_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.memory_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Memory info content
            memory_info = info.get('memory', {})
            if memory_info and 'error' not in memory_info:
                total_mem = memory_info.get('total', 0) or 0
                used_mem = memory_info.get('used', 0) or 0
                available_mem = memory_info.get('available', 0) or 0
                swap_total = memory_info.get('swap_total', 0) or 0
                swap_used = memory_info.get('swap_used', 0) or 0
                cached = memory_info.get('cached', 0) or 0
                buffers = memory_info.get('buffers', 0) or 0
                
                memory_content = f"""Memory Information:
{'='*50}

Total RAM: {total_mem / (1024**3):.2f} GB
Used RAM: {used_mem / (1024**3):.2f} GB
Available RAM: {available_mem / (1024**3):.2f} GB
RAM Usage: {memory_info.get('percent', 0):.1f}%
Cached: {cached / (1024**3):.2f} GB
Buffers: {buffers / (1024**3):.2f} GB

Swap Information:
Total Swap: {swap_total / (1024**3):.2f} GB
Used Swap: {swap_used / (1024**3):.2f} GB
Swap Usage: {memory_info.get('swap_percent', 0):.1f}%

Memory Modules:
{'='*50}
"""
                
                memory_modules = memory_info.get('memory_modules', [])
                if memory_modules:
                    for i, module in enumerate(memory_modules):
                        capacity = module.get('capacity', 0) or 0
                        speed = module.get('speed', 0) or 0
                        manufacturer = module.get('manufacturer', 'Unknown')
                        part_number = module.get('part_number', 'Unknown')
                        
                        memory_content += f"""
Module {i+1}:
  Capacity: {capacity / (1024**3):.2f} GB
  Speed: {speed} MHz
  Manufacturer: {manufacturer}
  Part Number: {part_number}
  Bank Label: {module.get('bank_label', 'Unknown')}
  Device Locator: {module.get('device_locator', 'Unknown')}
"""
                else:
                    memory_content += "No detailed memory module information available.\n"
            else:
                memory_total = info.get('memory_total', 0) or 0
                memory_available = info.get('memory_available', 0) or 0
                memory_percent = info.get('memory_percent', 0) or 0
                
                memory_content = f"""Memory Information:
{'='*50}

Basic Info:
Total: {memory_total / (1024**3):.2f} GB
Available: {memory_available / (1024**3):.2f} GB
Usage: {memory_percent:.1f}%

Detailed information not available.
"""
            self.memory_text.insert(tk.END, memory_content)
            self.memory_text.config(state=tk.DISABLED)
            
            # GPU Information Tab
            self.gpu_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.gpu_frame, text="GPU")
            
            self.gpu_text = tk.Text(self.gpu_frame, wrap=tk.WORD, font=("Consolas", 9))
            self.gpu_scrollbar = ttk.Scrollbar(self.gpu_frame, orient=tk.VERTICAL, command=self.gpu_text.yview)
            self.gpu_text.configure(yscrollcommand=self.gpu_scrollbar.set)
            
            self.gpu_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.gpu_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # GPU info content
            gpu_info = info.get('gpu', [])
            if gpu_info:
                gpu_content = f"""GPU Information:
{'='*50}

"""
                for i, gpu in enumerate(gpu_info):
                    memory_total = gpu.get('memory_total', 0) or 0
                    memory_used = gpu.get('memory_used', 0) or 0
                    memory_free = gpu.get('memory_free', 0) or 0
                    memory_percent = gpu.get('memory_percent', 0) or 0
                    gpu_percent = gpu.get('gpu_percent', 0) or 0
                    temperature = gpu.get('temperature', 0) or 0
                    
                    gpu_content += f"""GPU {i+1}:
  Name: {gpu.get('name', 'Unknown')}
  Vendor: {gpu.get('vendor', 'Unknown')}
  Driver Version: {gpu.get('driver_version', 'Unknown')}
  Memory Total: {memory_total / 1024:.1f} GB
  Memory Used: {memory_used / 1024:.1f} GB
  Memory Free: {memory_free / 1024:.1f} GB
  Memory Usage: {memory_percent:.1f}%
  GPU Usage: {gpu_percent:.1f}%
  Temperature: {temperature}°C
  UUID: {gpu.get('uuid', 'Unknown')}
  PNP Device ID: {gpu.get('pnp_device_id', 'Unknown')}
  Status: {gpu.get('status', 'Unknown')}
  Availability: {gpu.get('availability', 'Unknown')}

"""
            else:
                gpu_content = "No GPU information available.\n"
            
            self.gpu_text.insert(tk.END, gpu_content)
            self.gpu_text.config(state=tk.DISABLED)
            
            # Storage Information Tab
            self.storage_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.storage_frame, text="Storage")
            
            self.storage_text = tk.Text(self.storage_frame, wrap=tk.WORD, font=("Consolas", 9))
            self.storage_scrollbar = ttk.Scrollbar(self.storage_frame, orient=tk.VERTICAL, command=self.storage_text.yview)
            self.storage_text.configure(yscrollcommand=self.storage_scrollbar.set)
            
            self.storage_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.storage_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Storage info content
            disk_info = info.get('disk', [])
            if disk_info:
                storage_content = f"""Storage Information:
{'='*50}

"""
                for i, disk in enumerate(disk_info):
                    total = disk.get('total', 0) or 0
                    used = disk.get('used', 0) or 0
                    free = disk.get('free', 0) or 0
                    percent = disk.get('percent', 0) or 0
                    
                    storage_content += f"""Drive {i+1}:
  Device: {disk.get('device', 'Unknown')}
  Mount Point: {disk.get('mountpoint', 'Unknown')}
  File System: {disk.get('fstype', 'Unknown')}
  Model: {disk.get('model', 'Unknown')}
  Serial Number: {disk.get('serial_number', 'Unknown')}
  Size: {total / (1024**3):.2f} GB
  Used: {used / (1024**3):.2f} GB
  Free: {free / (1024**3):.2f} GB
  Usage: {percent:.1f}%
  Interface Type: {disk.get('interface_type', 'Unknown')}
  Firmware Version: {disk.get('firmware_version', 'Unknown')}
  Status: {disk.get('status', 'Unknown')}
  Media Type: {disk.get('media_type', 'Unknown')}
  Partitions: {disk.get('partitions', 'Unknown')}

"""
            else:
                storage_content = "No storage information available.\n"
            
            self.storage_text.insert(tk.END, storage_content)
            self.storage_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load detailed system information: {e}")
    
    def update_detailed_system_info(self):
        """Update the detailed system information with live data"""
        if not hasattr(self, 'info_window') or not self.info_window.winfo_exists():
            self.live_update_active = False
            return
        
        if not self.live_update_active:
            return
        
        try:
            # Get fresh system info
            info = self.optimizer.get_system_info()
            if info and 'error' not in info:
                self.current_info = info
                
                # Update each tab
                self.update_windows_tab(info)
                self.update_cpu_tab(info)
                self.update_memory_tab(info)
                self.update_gpu_tab(info)
                self.update_storage_tab(info)
                
                # Update status
                import time
                self.status_label.config(text=f"Last updated: {time.strftime('%H:%M:%S')}")
            
            # Schedule next update
            if self.live_update_active:
                self.info_window.after(self.update_interval * 1000, self.update_detailed_system_info)
                
        except Exception as e:
            self.status_label.config(text=f"Update error: {str(e)[:50]}...")
            if self.live_update_active:
                self.info_window.after(self.update_interval * 1000, self.update_detailed_system_info)
    
    def refresh_detailed_system_info(self):
        """Manually refresh the detailed system information"""
        self.update_detailed_system_info()
    
    def on_interval_changed(self, event=None):
        """Handle interval change"""
        try:
            self.update_interval = int(self.interval_var.get())
        except ValueError:
            self.update_interval = 2
    
    def update_windows_tab(self, info):
        """Update Windows information tab"""
        try:
            windows_info = info.get('windows_version', {})
            windows_content = f"""Windows Version Information:
{'='*50}

Operating System: {windows_info.get('os_name', 'Unknown')}
Version: {windows_info.get('release', 'Unknown')}
Build Number: {windows_info.get('build_number', 'Unknown')}
Architecture: {windows_info.get('architecture', 'Unknown')}
Platform: {windows_info.get('platform', 'Unknown')}
Is Server: {windows_info.get('is_server', False)}
Display Version: {windows_info.get('display_version', 'Unknown')}
Product Name: {windows_info.get('product_name', 'Unknown')}
Build Lab: {windows_info.get('build_lab', 'Unknown')}

Compatibility Information:
{'='*50}

Version: {self.optimizer.windows_compatibility.get('version', 'Unknown')}
Build: {self.optimizer.windows_compatibility.get('build', 'Unknown')}
Supports PowerShell: {self.optimizer.windows_compatibility.get('supports_powershell', False)}
Supports WSL: {self.optimizer.windows_compatibility.get('supports_wsl', False)}
Supports Hyper-V: {self.optimizer.windows_compatibility.get('supports_hyper_v', False)}
Supports Windows Defender: {self.optimizer.windows_compatibility.get('supports_windows_defender', False)}
Supports Windows Update: {self.optimizer.windows_compatibility.get('supports_windows_update', False)}
Supports System Restore: {self.optimizer.windows_compatibility.get('supports_system_restore', False)}

Recommended Commands:
{', '.join(self.optimizer.windows_compatibility.get('recommended_commands', []))}
"""
            self.windows_text.config(state=tk.NORMAL)
            self.windows_text.delete(1.0, tk.END)
            self.windows_text.insert(tk.END, windows_content)
            self.windows_text.config(state=tk.DISABLED)
        except Exception as e:
            pass  # Silently handle errors during updates
    
    def update_cpu_tab(self, info):
        """Update CPU information tab"""
        try:
            cpu_info = info.get('cpu', {})
            if cpu_info and 'error' not in cpu_info:
                cpu_content = f"""CPU Information:
{'='*50}

Name: {cpu_info.get('name', 'Unknown')}
Brand: {cpu_info.get('brand', 'Unknown')}
Physical Cores: {cpu_info.get('physical_cores', 'Unknown')}
Total Cores: {cpu_info.get('total_cores', 'Unknown')}
Current Usage: {info.get('cpu_percent', 0):.1f}%
Current Frequency: {cpu_info.get('current_frequency', 0):.0f} MHz
Max Frequency: {cpu_info.get('max_frequency', 0):.0f} MHz
Min Frequency: {cpu_info.get('min_frequency', 0):.0f} MHz
Family: {cpu_info.get('family', 'Unknown')}
Model: {cpu_info.get('model', 'Unknown')}
Stepping: {cpu_info.get('stepping', 'Unknown')}
Microcode: {cpu_info.get('microcode', 'Unknown')}
Cache Size: {cpu_info.get('cache_size', 'Unknown')} KB
Vendor ID: {cpu_info.get('vendor_id', 'Unknown')}
"""
            else:
                cpu_content = f"""CPU Information:
{'='*50}

Basic Info:
Cores: {info.get('cpu_count', 'Unknown')}
Usage: {info.get('cpu_percent', 0):.1f}%

Detailed information not available.
"""
            self.cpu_text.config(state=tk.NORMAL)
            self.cpu_text.delete(1.0, tk.END)
            self.cpu_text.insert(tk.END, cpu_content)
            self.cpu_text.config(state=tk.DISABLED)
        except Exception as e:
            pass
    
    def update_memory_tab(self, info):
        """Update Memory information tab"""
        try:
            memory_info = info.get('memory', {})
            if memory_info and 'error' not in memory_info:
                total_mem = memory_info.get('total', 0) or 0
                used_mem = memory_info.get('used', 0) or 0
                available_mem = memory_info.get('available', 0) or 0
                swap_total = memory_info.get('swap_total', 0) or 0
                swap_used = memory_info.get('swap_used', 0) or 0
                cached = memory_info.get('cached', 0) or 0
                buffers = memory_info.get('buffers', 0) or 0
                
                memory_content = f"""Memory Information:
{'='*50}

Total RAM: {total_mem / (1024**3):.2f} GB
Used RAM: {used_mem / (1024**3):.2f} GB
Available RAM: {available_mem / (1024**3):.2f} GB
RAM Usage: {memory_info.get('percent', 0):.1f}%
Cached: {cached / (1024**3):.2f} GB
Buffers: {buffers / (1024**3):.2f} GB

Swap Information:
Total Swap: {swap_total / (1024**3):.2f} GB
Used Swap: {swap_used / (1024**3):.2f} GB
Swap Usage: {memory_info.get('swap_percent', 0):.1f}%

Memory Modules:
{'='*50}
"""
                
                memory_modules = memory_info.get('memory_modules', [])
                if memory_modules:
                    for i, module in enumerate(memory_modules):
                        capacity = module.get('capacity', 0) or 0
                        speed = module.get('speed', 0) or 0
                        manufacturer = module.get('manufacturer', 'Unknown')
                        part_number = module.get('part_number', 'Unknown')
                        
                        memory_content += f"""
Module {i+1}:
  Capacity: {capacity / (1024**3):.2f} GB
  Speed: {speed} MHz
  Manufacturer: {manufacturer}
  Part Number: {part_number}
  Bank Label: {module.get('bank_label', 'Unknown')}
  Device Locator: {module.get('device_locator', 'Unknown')}
"""
                else:
                    memory_content += "No detailed memory module information available.\n"
            else:
                memory_total = info.get('memory_total', 0) or 0
                memory_available = info.get('memory_available', 0) or 0
                memory_percent = info.get('memory_percent', 0) or 0
                
                memory_content = f"""Memory Information:
{'='*50}

Basic Info:
Total: {memory_total / (1024**3):.2f} GB
Available: {memory_available / (1024**3):.2f} GB
Usage: {memory_percent:.1f}%

Detailed information not available.
"""
            self.memory_text.config(state=tk.NORMAL)
            self.memory_text.delete(1.0, tk.END)
            self.memory_text.insert(tk.END, memory_content)
            self.memory_text.config(state=tk.DISABLED)
        except Exception as e:
            pass
    
    def update_gpu_tab(self, info):
        """Update GPU information tab"""
        try:
            gpu_info = info.get('gpu', [])
            if gpu_info:
                gpu_content = f"""GPU Information:
{'='*50}

"""
                for i, gpu in enumerate(gpu_info):
                    memory_total = gpu.get('memory_total', 0) or 0
                    memory_used = gpu.get('memory_used', 0) or 0
                    memory_free = gpu.get('memory_free', 0) or 0
                    memory_percent = gpu.get('memory_percent', 0) or 0
                    gpu_percent = gpu.get('gpu_percent', 0) or 0
                    temperature = gpu.get('temperature', 0) or 0
                    
                    gpu_content += f"""GPU {i+1}:
  Name: {gpu.get('name', 'Unknown')}
  Vendor: {gpu.get('vendor', 'Unknown')}
  Driver Version: {gpu.get('driver_version', 'Unknown')}
  Memory Total: {memory_total / 1024:.1f} GB
  Memory Used: {memory_used / 1024:.1f} GB
  Memory Free: {memory_free / 1024:.1f} GB
  Memory Usage: {memory_percent:.1f}%
  GPU Usage: {gpu_percent:.1f}%
  Temperature: {temperature}°C
  UUID: {gpu.get('uuid', 'Unknown')}
  PNP Device ID: {gpu.get('pnp_device_id', 'Unknown')}
  Status: {gpu.get('status', 'Unknown')}
  Availability: {gpu.get('availability', 'Unknown')}

"""
            else:
                gpu_content = "No GPU information available.\n"
            
            self.gpu_text.config(state=tk.NORMAL)
            self.gpu_text.delete(1.0, tk.END)
            self.gpu_text.insert(tk.END, gpu_content)
            self.gpu_text.config(state=tk.DISABLED)
        except Exception as e:
            pass
    
    def update_storage_tab(self, info):
        """Update Storage information tab"""
        try:
            disk_info = info.get('disk', [])
            if disk_info:
                storage_content = f"""Storage Information:
{'='*50}

"""
                for i, disk in enumerate(disk_info):
                    total = disk.get('total', 0) or 0
                    used = disk.get('used', 0) or 0
                    free = disk.get('free', 0) or 0
                    percent = disk.get('percent', 0) or 0
                    
                    storage_content += f"""Drive {i+1}:
  Device: {disk.get('device', 'Unknown')}
  Mount Point: {disk.get('mountpoint', 'Unknown')}
  File System: {disk.get('fstype', 'Unknown')}
  Model: {disk.get('model', 'Unknown')}
  Serial Number: {disk.get('serial_number', 'Unknown')}
  Size: {total / (1024**3):.2f} GB
  Used: {used / (1024**3):.2f} GB
  Free: {free / (1024**3):.2f} GB
  Usage: {percent:.1f}%
  Interface Type: {disk.get('interface_type', 'Unknown')}
  Firmware Version: {disk.get('firmware_version', 'Unknown')}
  Status: {disk.get('status', 'Unknown')}
  Media Type: {disk.get('media_type', 'Unknown')}
  Partitions: {disk.get('partitions', 'Unknown')}

"""
            else:
                storage_content = "No storage information available.\n"
            
            self.storage_text.config(state=tk.NORMAL)
            self.storage_text.delete(1.0, tk.END)
            self.storage_text.insert(tk.END, storage_content)
            self.storage_text.config(state=tk.DISABLED)
        except Exception as e:
            pass
    
    def show_about(self):
        """Show about dialog"""
        about_text = """OptimusPC v1.0.0
        
A comprehensive PC optimization tool designed to enhance system performance through intelligent resource management and maintenance automation.

Features:
• Memory optimization
• Temporary file cleanup
• Browser cache clearing
• Startup program analysis
• System performance monitoring
• Windows version compatibility
• Detailed hardware detection

Built with Python and Tkinter
© 2024 OptimusPC Team"""
        
        messagebox.showinfo("About OptimusPC", about_text)
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()
