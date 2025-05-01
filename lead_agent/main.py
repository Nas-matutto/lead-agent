"""
Main entry point for the Lead Agent application.
"""
import logging
from lead_agent.cli import main

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the CLI
    main()