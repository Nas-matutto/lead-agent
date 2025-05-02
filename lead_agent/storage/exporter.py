"""
Data export and storage module for Lead Agent.
"""
import os
import json
import logging
import csv
from datetime import datetime
from typing import Dict, List, Any

import pandas as pd

logger = logging.getLogger(__name__)

class DataExporter:
    """Exporter for lead data."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the data exporter.
        
        Args:
            config: Exporter configuration
        """
        self.config = config
        self.output_dir = config.get("output_dir", "data")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _get_filename(self, format: str) -> str:
        """
        Generate a timestamped filename.
        
        Args:
            format: File format
            
        Returns:
            Filename with path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"leads_{timestamp}.{format}")
    
    def export_leads(self, leads: List[Dict[str, Any]], format: str = "csv") -> str:
        """
        Export leads to a file.
        
        Args:
            leads: List of lead dictionaries
            format: Output format (csv, json, etc.)
            
        Returns:
            Path to the exported file
        """
        if not leads:
            logger.warning("No leads to export")
            return ""
            
        format = format.lower()
        filename = self._get_filename(format)
        
        try:
            if format == "csv":
                return self._export_csv(leads, filename)
            elif format == "json":
                return self._export_json(leads, filename)
            else:
                logger.warning(f"Unsupported format: {format}, using CSV instead")
                return self._export_csv(leads, filename)
        except Exception as e:
            logger.error(f"Error exporting leads: {str(e)}")
            return ""
    
    def _export_csv(self, leads: List[Dict[str, Any]], filename: str) -> str:
        """
        Export leads to CSV.
        
        Args:
            leads: List of lead dictionaries
            filename: Output filename
            
        Returns:
            Path to the exported file
        """
        # Convert to DataFrame for easier CSV export
        df = pd.DataFrame(leads)
        
        # Write to CSV
        df.to_csv(filename, index=False, quoting=csv.QUOTE_NONNUMERIC)
        
        logger.info(f"Exported {len(leads)} leads to {filename}")
        return filename
    
    def _export_json(self, leads: List[Dict[str, Any]], filename: str) -> str:
        """
        Export leads to JSON.
        
        Args:
            leads: List of lead dictionaries
            filename: Output filename
            
        Returns:
            Path to the exported file
        """
        with open(filename, "w") as f:
            json.dump(leads, f, indent=2)
            
        logger.info(f"Exported {len(leads)} leads to {filename}")
        return filename