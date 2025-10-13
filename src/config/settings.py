# OptimusPC Configuration Management

import json
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration management for OptimusPC"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_default_config()
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "general": {
                "auto_cleanup": True,
                "cleanup_interval_hours": 24,
                "backup_before_cleanup": True,
                "log_level": "INFO"
            },
            "memory": {
                "auto_optimize": True,
                "threshold_percent": 80,
                "force_gc": True
            },
            "cleanup": {
                "temp_files": True,
                "browser_cache": True,
                "recycle_bin": False,
                "windows_update_cache": True,
                "custom_paths": []
            },
            "gui": {
                "theme": "default",
                "window_size": [800, 600],
                "remember_position": True
            },
            "advanced": {
                "deep_scan": False,
                "exclude_system_files": True,
                "max_file_age_days": 30
            }
        }
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        # File is empty, use defaults
                        return
                    loaded_config = json.loads(content)
                    self._merge_config(loaded_config)
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in config file: {e}. Using defaults.")
                # Create a backup of the invalid config
                backup_file = self.config_file.with_suffix('.json.backup')
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        with open(backup_file, 'w', encoding='utf-8') as backup:
                            backup.write(f.read())
                    print(f"Invalid config backed up to: {backup_file}")
                except:
                    pass
            except IOError as e:
                print(f"Warning: Could not read config file: {e}. Using defaults.")
    
    def _merge_config(self, loaded_config: Dict[str, Any]):
        """Merge loaded config with defaults"""
        def merge_dict(default: dict, loaded: dict):
            for key, value in loaded.items():
                if key in default:
                    if isinstance(default[key], dict) and isinstance(value, dict):
                        merge_dict(default[key], value)
                    else:
                        default[key] = value
        
        merge_dict(self.config, loaded_config)
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'general.auto_cleanup')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def get_cleanup_paths(self) -> list:
        """Get list of paths to clean"""
        paths = []
        
        if self.get('cleanup.temp_files', True):
            paths.extend([
                os.path.expandvars('%TEMP%'),
                os.path.expandvars('%TMP%'),
                os.path.expanduser('~\\AppData\\Local\\Temp'),
            ])
        
        if self.get('cleanup.browser_cache', True):
            paths.extend([
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache'),
                os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache'),
            ])
        
        # Add custom paths
        custom_paths = self.get('cleanup.custom_paths', [])
        paths.extend(custom_paths)
        
        return paths
