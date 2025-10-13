# OptimusPC Progress Window

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Dict, List, Callable, Optional

class ProgressWindow:
    """Progress window showing optimization tasks with checkmarks and details"""
    
    def __init__(self, parent, title: str = "Optimization Progress"):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("500x400")
        self.window.resizable(True, True)
        
        # Center the window
        self.center_window()
        
        # Task tracking
        self.tasks = {}
        self.task_widgets = {}
        self.completed_tasks = set()
        
        # Callbacks
        self.on_task_complete: Optional[Callable] = None
        self.on_all_complete: Optional[Callable] = None
        
        self.create_widgets()
        
        # Prevent closing during optimization
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def center_window(self):
        """Center the progress window on the parent"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"500x400+{x}+{y}")
        
    def create_widgets(self):
        """Create progress window widgets"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Optimization Progress", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Initializing...")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.pack(pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))
        
        # Tasks frame with scrollbar
        tasks_frame = ttk.Frame(main_frame)
        tasks_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for tasks
        canvas = tk.Canvas(tasks_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tasks_container = scrollable_frame
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", 
                                   command=self.cancel_optimization)
        self.cancel_btn.pack(side=tk.RIGHT)
        
        self.close_btn = ttk.Button(button_frame, text="Close", 
                                   command=self.close_window, state=tk.DISABLED)
        self.close_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
    def add_task(self, task_id: str, task_name: str, description: str = ""):
        """Add a new task to the progress window"""
        task_frame = ttk.Frame(self.tasks_container)
        task_frame.pack(fill=tk.X, pady=2)
        
        # Checkbox (initially unchecked)
        checkbox_var = tk.BooleanVar()
        checkbox = ttk.Checkbutton(task_frame, variable=checkbox_var, state=tk.DISABLED)
        checkbox.pack(side=tk.LEFT, padx=(0, 10))
        
        # Task name
        task_label = ttk.Label(task_frame, text=task_name, font=("Arial", 10))
        task_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Details label
        details_label = ttk.Label(task_frame, text=description, 
                                font=("Arial", 8), foreground="gray")
        details_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Store task info
        self.tasks[task_id] = {
            'name': task_name,
            'description': description,
            'frame': task_frame,
            'checkbox': checkbox,
            'checkbox_var': checkbox_var,
            'task_label': task_label,
            'details_label': details_label,
            'status': 'pending'
        }
        
        self.task_widgets[task_id] = {
            'checkbox': checkbox,
            'checkbox_var': checkbox_var,
            'task_label': task_label,
            'details_label': details_label
        }
        
    def update_task_status(self, task_id: str, status: str, details: str = "", 
                          freed_space: float = 0):
        """Update task status with details"""
        if task_id not in self.tasks:
            return
            
        task = self.tasks[task_id]
        widgets = self.task_widgets[task_id]
        
        if status == 'running':
            task['status'] = 'running'
            widgets['task_label'].config(text=f"🔄 {task['name']}")
            widgets['details_label'].config(text="In progress...", foreground="blue")
            
        elif status == 'completed':
            task['status'] = 'completed'
            widgets['checkbox_var'].set(True)
            widgets['checkbox'].config(state=tk.NORMAL)
            
            # Strike through the task name
            widgets['task_label'].config(text=f"✅ {task['name']}")
            
            if details:
                widgets['details_label'].config(text=details, foreground="green")
            elif freed_space > 0:
                widgets['details_label'].config(
                    text=f"Freed {freed_space:.2f} MB", foreground="green"
                )
            else:
                widgets['details_label'].config(text="Completed", foreground="green")
                
            self.completed_tasks.add(task_id)
            
            # Call completion callback
            if self.on_task_complete:
                self.on_task_complete(task_id, task['name'], details, freed_space)
                
        elif status == 'error':
            task['status'] = 'error'
            widgets['task_label'].config(text=f"❌ {task['name']}")
            widgets['details_label'].config(text=f"Error: {details}", foreground="red")
            
        # Update progress bar
        self.update_progress_bar()
        
    def update_progress_bar(self):
        """Update the progress bar based on completed tasks"""
        total_tasks = len(self.tasks)
        completed_count = len(self.completed_tasks)
        
        if total_tasks > 0:
            progress = (completed_count / total_tasks) * 100
            self.progress_bar['value'] = progress
            
            if completed_count == total_tasks:
                self.progress_var.set("Optimization Complete!")
                self.cancel_btn.config(state=tk.DISABLED)
                self.close_btn.config(state=tk.NORMAL)
                
                if self.on_all_complete:
                    self.on_all_complete()
            else:
                self.progress_var.set(f"Progress: {completed_count}/{total_tasks} tasks completed")
                
    def set_tasks(self, tasks: List[Dict[str, str]]):
        """Set all tasks at once"""
        # Clear existing tasks
        for widget in self.tasks_container.winfo_children():
            widget.destroy()
            
        self.tasks.clear()
        self.task_widgets.clear()
        self.completed_tasks.clear()
        
        # Add new tasks
        for task in tasks:
            self.add_task(task['id'], task['name'], task.get('description', ''))
            
        self.update_progress_bar()
        
    def cancel_optimization(self):
        """Cancel the optimization process"""
        self.progress_var.set("Cancelling...")
        self.cancel_btn.config(state=tk.DISABLED)
        
        # This would be handled by the main optimization thread
        # For now, just close the window
        self.close_window()
        
    def close_window(self):
        """Close the progress window"""
        self.window.destroy()
        
    def on_close(self):
        """Handle window close event"""
        # Only allow closing if optimization is complete or cancelled
        if len(self.completed_tasks) == len(self.tasks) or not self.cancel_btn['state'] == 'normal':
            self.close_window()
        else:
            # Show warning
            import tkinter.messagebox as msgbox
            if msgbox.askyesno("Cancel Optimization", 
                             "Are you sure you want to cancel the optimization?"):
                self.cancel_optimization()
                
    def is_closed(self) -> bool:
        """Check if the window is closed"""
        try:
            return not self.window.winfo_exists()
        except:
            return True
