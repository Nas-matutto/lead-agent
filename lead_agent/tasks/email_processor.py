"""
Background task for processing scheduled emails.
"""
import time
import logging
import threading
from datetime import datetime

from lead_agent.services.email_service import EmailService

logger = logging.getLogger(__name__)

class EmailProcessor(threading.Thread):
    """Thread to process scheduled emails."""
    
    def __init__(self, interval=60):
        """
        Initialize the email processor.
        
        Args:
            interval: Processing interval in seconds
        """
        super().__init__()
        self.interval = interval
        self.daemon = True  # Thread will exit when main thread exits
        self.running = True
    
    def run(self):
        """Run the processor."""
        logger.info("Starting email processor")
        
        while self.running:
            try:
                # Process pending emails
                EmailService.process_pending_emails()
                
                # Sleep for the specified interval
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"Error in email processor: {str(e)}")
                time.sleep(self.interval)
    
    def stop(self):
        """Stop the processor."""
        self.running = False