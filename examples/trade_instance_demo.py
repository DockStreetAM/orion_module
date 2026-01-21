#!/usr/bin/env python3
"""Trade Instance Demo - Demonstrates EclipseAPI trade instance workflow.

This script shows how to:
1. List recent trade instances
2. Get trade instance details
3. Get trade logs for an instance
4. Save detailed HTML trade logs
5. Query trade instances for a specific portfolio

Usage:
    poetry run python examples/trade_instance_demo.py
    poetry run python examples/trade_instance_demo.py --instance-id 4891
    poetry run python examples/trade_instance_demo.py --interactive
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from orionapi import EclipseAPI


def mask_username(username: str) -> str:
    """Mask username for display, showing first 3 chars and domain."""
    if "@" in username:
        local, domain = username.split("@", 1)
        if len(local) > 3:
            return f"{local[:3]}...@{domain}"
    return username[:3] + "..." if len(username) > 3 else username


def print_header(title: str):
    """Print a section header."""
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_subheader(title: str):
    """Print a subsection header."""
    print()
    print(f"--- {title} ---")


def format_date(date_str: str) -> str:
    """Format ISO date string for display."""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return date_str


def list_trade_instances(api: EclipseAPI, days: int = 30):
    """List recent trade instances."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    print_subheader(f"Recent Trade Instances (Last {days} Days)")
    print(f"Date range: {start_date} to {end_date}")
    print()

    instances = api.get_trade_instances(start_date, end_date)

    if not instances:
        print("No trade instances found in this date range.")
        return []

    # Print table header
    print(f"{'ID':<8} {'Status':<12} {'Orders':<8} {'Type':<20} {'Created'}")
    print("-" * 80)

    for inst in instances:
        inst_id = inst.get("id", "N/A")
        status = inst.get("executeStatus", "N/A")
        orders = inst.get("orderCount", 0)
        inst_type = inst.get("tradeInstanceType") or inst.get("tradeInstanceSubType") or "N/A"
        created = format_date(inst.get("createdDate"))

        print(f"{inst_id:<8} {status:<12} {orders:<8} {inst_type:<20} {created}")

    print(f"\nTotal: {len(instances)} trade instance(s)")
    return instances


def show_instance_details(api: EclipseAPI, instance_id: int):
    """Show details for a specific trade instance."""
    print_subheader(f"Instance {instance_id} Details")

    try:
        details = api.get_trade_instance(instance_id)
        print(json.dumps(details, indent=2, default=str))
        return details
    except Exception as e:
        print(f"Error retrieving instance {instance_id}: {e}")
        return None


def show_trade_logs(api: EclipseAPI, instance_id: int):
    """Show trade logs for a trade instance."""
    print_subheader(f"Trade Logs for Instance {instance_id}")

    try:
        logs = api.get_trade_instance_logs(instance_id)

        if not logs:
            print("No trade logs found for this instance.")
            return []

        for log in logs:
            log_id = log.get("id", "N/A")
            portfolio_name = log.get("portfolioName", "Unknown")
            portfolio_id = log.get("portfolioId", "N/A")
            application = log.get("application", "N/A")
            created = format_date(log.get("createdDate"))
            has_errors = log.get("hasErrors", False)

            print(f"\nLog ID: {log_id}")
            print(f"  Portfolio: {portfolio_name} (ID {portfolio_id})")
            print(f"  Application: {application}")
            print(f"  Created: {created}")
            if has_errors:
                print("  ** HAS ERRORS **")

        print(f"\nTotal: {len(logs)} trade log(s)")
        return logs
    except Exception as e:
        print(f"Error retrieving trade logs: {e}")
        return []


def save_detailed_trade_log(api: EclipseAPI, log_id: int, output_dir: Path = None):
    """Save detailed HTML trade log to file."""
    print_subheader("Saving Detailed Trade Log")

    if output_dir is None:
        output_dir = Path.cwd()

    output_file = output_dir / f"trade_log_{log_id}_detail.html"

    try:
        html_content = api.get_trade_log_detail(log_id)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"Saved to: {output_file}")
        print("  Open in browser to view trading engine decisions")

        # Try to extract some summary stats from HTML
        if "Trading Engine" in html_content:
            print("  Contains: Trading Engine decisions")
        if "Security" in html_content or "security" in html_content:
            print("  Contains: Security-level details")

        return str(output_file)
    except Exception as e:
        print(f"Error saving trade log {log_id}: {e}")
        return None


def show_portfolio_instances(api: EclipseAPI, portfolio_id: int, days: int = 30):
    """Show trade instances for a specific portfolio."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    print_subheader(f"Trade Instances for Portfolio {portfolio_id}")
    print(f"Date range: {start_date} to {end_date}")
    print()

    try:
        instances = api.get_portfolio_trade_instances(portfolio_id, start_date, end_date)

        if not instances:
            print("No trade instances found for this portfolio.")
            return []

        for inst in instances:
            inst_id = inst.get("id", "N/A")
            status = inst.get("executeStatus", "N/A")
            orders = inst.get("orderCount", 0)
            created = format_date(inst.get("createdDate"))
            print(f"  Instance {inst_id}: {status}, {orders} orders, created {created}")

        print(f"\nTotal: {len(instances)} trade instance(s)")
        return instances
    except Exception as e:
        print(f"Error retrieving portfolio instances: {e}")
        return []


def interactive_mode(api: EclipseAPI):
    """Interactive mode for exploring trade data."""
    print_subheader("Interactive Mode")
    print("Commands:")
    print("  list [days]     - List recent trade instances (default: 30 days)")
    print("  details <id>    - Show instance details")
    print("  logs <id>       - Show trade logs for instance")
    print("  save <log_id>   - Save detailed trade log HTML")
    print("  portfolio <id>  - Show instances for portfolio")
    print("  quit            - Exit interactive mode")
    print()

    while True:
        try:
            cmd = input("trade> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting interactive mode.")
            break

        if not cmd:
            continue

        parts = cmd.split()
        command = parts[0].lower()

        if command in ("quit", "exit", "q"):
            print("Exiting interactive mode.")
            break
        elif command == "list":
            days = int(parts[1]) if len(parts) > 1 else 30
            list_trade_instances(api, days)
        elif command == "details":
            if len(parts) < 2:
                print("Usage: details <instance_id>")
                continue
            show_instance_details(api, int(parts[1]))
        elif command == "logs":
            if len(parts) < 2:
                print("Usage: logs <instance_id>")
                continue
            show_trade_logs(api, int(parts[1]))
        elif command == "save":
            if len(parts) < 2:
                print("Usage: save <log_id>")
                continue
            save_detailed_trade_log(api, int(parts[1]))
        elif command == "portfolio":
            if len(parts) < 2:
                print("Usage: portfolio <portfolio_id>")
                continue
            show_portfolio_instances(api, int(parts[1]))
        else:
            print(f"Unknown command: {command}")


def main():
    parser = argparse.ArgumentParser(
        description="Demo script for EclipseAPI trade instance workflow"
    )
    parser.add_argument(
        "--instance-id",
        type=int,
        help="Specific trade instance ID to explore",
    )
    parser.add_argument(
        "--portfolio-id",
        type=int,
        help="Portfolio ID to show trade instances for",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode",
    )
    parser.add_argument(
        "--save-log",
        type=int,
        metavar="LOG_ID",
        help="Save detailed HTML for a specific trade log ID",
    )
    args = parser.parse_args()

    # Load environment variables
    # Try examples/.env first, then project root .env
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    if (script_dir / ".env").exists():
        load_dotenv(script_dir / ".env")
    elif (project_root / ".env").exists():
        load_dotenv(project_root / ".env")
    else:
        print("Warning: No .env file found. Set ECLIPSE_USER and ECLIPSE_PWD env vars.")

    username = os.getenv("ECLIPSE_USER")
    password = os.getenv("ECLIPSE_PWD")

    if not username or not password:
        print("Error: ECLIPSE_USER and ECLIPSE_PWD environment variables required.")
        print("Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)

    print_header("Trade Instance Demo - EclipseAPI")
    print(f"Connecting as: {mask_username(username)}")

    try:
        api = EclipseAPI(usr=username, pwd=password)
        print("Successfully authenticated")
    except Exception as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)

    # Handle specific command-line options
    if args.save_log:
        save_detailed_trade_log(api, args.save_log)
        return

    if args.interactive:
        interactive_mode(api)
        return

    # Default workflow: list instances, then show details if instance-id provided
    instances = list_trade_instances(api, args.days)

    if args.instance_id:
        # Show details for specified instance
        show_instance_details(api, args.instance_id)
        logs = show_trade_logs(api, args.instance_id)

        # If there are logs, save the first one as HTML
        if logs:
            first_log_id = logs[0].get("id")
            if first_log_id:
                save_detailed_trade_log(api, first_log_id)

    elif instances:
        # If no specific instance, show details for the most recent one
        most_recent = instances[0]
        instance_id = most_recent.get("id")
        if instance_id:
            show_instance_details(api, instance_id)
            logs = show_trade_logs(api, instance_id)

            if logs:
                first_log_id = logs[0].get("id")
                if first_log_id:
                    save_detailed_trade_log(api, first_log_id)

    if args.portfolio_id:
        show_portfolio_instances(api, args.portfolio_id, args.days)

    print_subheader("Demo Complete")
    print("Run with --interactive for more exploration options.")


if __name__ == "__main__":
    main()
