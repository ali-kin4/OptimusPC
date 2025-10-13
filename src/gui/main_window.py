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
        # CPU Info
        ttk.Label(parent, text="CPU:").grid(row=0, column=0, sticky=tk.W)
        self.cpu_label = ttk.Label(parent, text="Loading...")
        self.cpu_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Memory Info
        ttk.Label(parent, text="Memory:").grid(row=1, column=0, sticky=tk.W)
        self.memory_label = ttk.Label(parent, text="Loading...")
        self.memory_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Disk Info
        ttk.Label(parent, text="Disk:").grid(row=2, column=0, sticky=tk.W)
        self.disk_label = ttk.Label(parent, text="Loading...")
        self.disk_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Refresh button
        refresh_btn = ttk.Button(parent, text="Refresh", command=self.update_system_info)
        refresh_btn.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
    def create_optimization_widgets(self, parent):
        """Create optimization option widgets"""
        # Checkboxes for different optimization types
        self.memory_var = tk.BooleanVar(value=True)
        self.temp_var = tk.BooleanVar(value=True)
        self.cache_var = tk.BooleanVar(value=True)
        self.startup_var = tk.BooleanVar(value=False)
        self.geek_mode_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(parent, text="Memory Optimization", 
                       variable=self.memory_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(parent, text="Clear Temporary Files", 
                       variable=self.temp_var).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(parent, text="Clear Browser Cache", 
                       variable=self.cache_var).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(parent, text="Analyze Startup Programs", 
                       variable=self.startup_var).grid(row=1, column=1, sticky=tk.W)
        
        # Geek mode toggle
        geek_frame = ttk.Frame(parent)
        geek_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
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
            
            if info:
                cpu_text = f"{info.get('cpu_count', 'N/A')} cores, {info.get('cpu_percent', 0):.1f}% usage"
                self.cpu_label.config(text=cpu_text)
                
                memory_text = f"{info.get('memory_percent', 0):.1f}% used ({info.get('memory_available', 0) / (1024**3):.1f} GB available)"
                self.memory_label.config(text=memory_text)
                
                disk_text = f"{info.get('disk_percent', 0):.1f}% used ({info.get('disk_free', 0) / (1024**3):.1f} GB free)"
                self.disk_label.config(text=disk_text)
            else:
                self.cpu_label.config(text="Error loading info")
                self.memory_label.config(text="Error loading info")
                self.disk_label.config(text="Error loading info")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load system information: {e}")
    
    def start_optimization(self):
        """Start optimization process"""
        if self.running:
            return
            
        # Check if any optimization is selected
        if not any([self.memory_var.get(), self.temp_var.get(), 
                   self.cache_var.get(), self.startup_var.get()]):
            messagebox.showwarning("No Options Selected", 
                                 "Please select at least one optimization option.")
            return
            
        self.running = True
        self.geek_mode = self.geek_mode_var.get()
        
        # Create progress window
        self.progress_window = ProgressWindow(self.root, "Optimization Progress")
        
        # Setup tasks based on selected options
        tasks = []
        if self.memory_var.get():
            tasks.append({'id': 'memory', 'name': 'Memory Optimization', 
                         'description': 'Optimizing RAM usage and clearing system cache'})
        if self.temp_var.get():
            tasks.append({'id': 'temp', 'name': 'Temporary Files Cleanup', 
                         'description': 'Removing temporary files from system directories'})
        if self.cache_var.get():
            tasks.append({'id': 'cache', 'name': 'Browser Cache Cleanup', 
                         'description': 'Clearing browser cache files'})
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
            if self.memory_var.get():
                tasks.append('memory')
            if self.temp_var.get():
                tasks.append('temp')
            if self.cache_var.get():
                tasks.append('cache')
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

Built with Python and Tkinter
© 2024 OptimusPC Team"""
        
        messagebox.showinfo("About OptimusPC", about_text)
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()
