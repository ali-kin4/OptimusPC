# OptimusPC Test Suite

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.optimizer import OptimusOptimizer
from src.config.settings import Config

class TestOptimusOptimizer(unittest.TestCase):
    """Test cases for OptimusOptimizer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = Mock()
        self.optimizer = OptimusOptimizer(self.config)
    
    def test_get_system_info(self):
        """Test system information retrieval"""
        info = self.optimizer.get_system_info()
        
        # Check that we get some system info
        self.assertIsInstance(info, dict)
        self.assertIn('cpu_count', info)
        self.assertIn('memory_total', info)
        self.assertIn('disk_total', info)
    
    @patch('src.utils.psutil_safe.psutil.virtual_memory')
    def test_optimize_memory(self, mock_memory):
        """Test memory optimization"""
        # Mock memory info
        mock_memory.return_value.used = 8000000000  # 8GB
        mock_memory.return_value.percent = 85.0
        
        result = self.optimizer.optimize_memory()
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_clear_temp_files(self):
        """Test temporary file cleanup"""
        with patch('os.path.exists', return_value=True):
            with patch.object(self.optimizer, '_clean_directory', return_value=(1024, 1)):
                result = self.optimizer.clear_temp_files()
                
                self.assertIsInstance(result, dict)
                self.assertIn('success', result)
                self.assertIn('freed_space_mb', result)
                self.assertIn('files_removed', result)

class TestConfig(unittest.TestCase):
    """Test cases for Config class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = Config()
    
    def test_default_config(self):
        """Test default configuration loading"""
        self.assertIn('general', self.config.config)
        self.assertIn('memory', self.config.config)
        self.assertIn('cleanup', self.config.config)
    
    def test_get_method(self):
        """Test configuration get method"""
        value = self.config.get('general.auto_cleanup')
        self.assertIsInstance(value, bool)
    
    def test_set_method(self):
        """Test configuration set method"""
        self.config.set('test.value', 'test')
        value = self.config.get('test.value')
        self.assertEqual(value, 'test')
    
    def test_get_cleanup_paths(self):
        """Test cleanup paths retrieval"""
        paths = self.config.get_cleanup_paths()
        self.assertIsInstance(paths, list)
        self.assertGreater(len(paths), 0)

if __name__ == '__main__':
    unittest.main()
