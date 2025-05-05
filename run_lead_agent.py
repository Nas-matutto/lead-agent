#!/usr/bin/env python
"""
Lead Agent launcher script.
"""
import os
import sys
import argparse
import logging
import subprocess

def run_api_server(port=5000):
    """Run the API server."""
    print(f"Starting Lead Agent API server on port {port}...")
    subprocess.call(
        [sys.executable, "api_server.py"],
        env=dict(os.environ, PORT=str(port))
    )

def run_cli(args):
    """Run the CLI with the specified arguments."""
    from lead_agent.cli import main
    print("Starting Lead Agent CLI...")
    sys.argv = ["lead-agent"] + args
    main()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Lead Agent launcher")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # API server command
    server_parser = subparsers.add_parser("server", help="Run the API server")
    server_parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    
    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run the CLI")
    cli_parser.add_argument("action", nargs="*", help="CLI action and arguments")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "server":
        run_api_server(args.port)
    elif args.command == "cli":
        run_cli(args.action)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()