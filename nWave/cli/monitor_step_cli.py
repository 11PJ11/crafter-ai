#!/usr/bin/env python3
"""
Real-time TDD step execution monitor.
Usage: python3 /tmp/monitor_step.py <agent_id>
"""
import sys
import time
import yaml
from pathlib import Path
from datetime import datetime

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
GRAY = '\033[90m'
RESET = '\033[0m'
BOLD = '\033[1m'

def clear_screen():
    print('\033[2J\033[H', end='')

def format_duration(minutes):
    if minutes < 1:
        return "< 1 min"
    elif minutes < 60:
        return f"{int(minutes)} min"
    else:
        hours = minutes / 60
        return f"{hours:.1f}h"

def get_phase_symbol(status):
    if status == "COMPLETED":
        return f"{GREEN}✅{RESET}"
    elif status == "IN_PROGRESS":
        return f"{YELLOW}🔄{RESET}"
    elif status == "SKIPPED":
        return f"{GRAY}⊘{RESET}"
    else:
        return f"{GRAY}⏳{RESET}"

def monitor_step(agent_id):
    exec_status_path = Path("docs/feature/des-hook-enforcement/execution-log.yaml")
    agent_output_path = Path(f"/tmp/claude/-mnt-c-Repositories-Projects-ai-craft/tasks/{agent_id}.output")

    last_phase_count = 0
    iteration = 0

    while True:
        clear_screen()
        iteration += 1

        # Header
        print(f"{BOLD}{BLUE}╔══════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{BLUE}║  🚀 DES Hook Enforcement - TDD Step Monitor           ║{RESET}")
        print(f"{BOLD}{BLUE}╚══════════════════════════════════════════════════════════╝{RESET}")
        print()

        # Read execution status
        try:
            with open(exec_status_path, 'r') as f:
                data = yaml.safe_load(f)

            exec_status = data.get('execution_status', {})
            current_step = exec_status.get('current_step', 'Unknown')
            checkpoint = exec_status.get('step_checkpoint', {})
            phases = checkpoint.get('phases', [])

            # Step info
            print(f"{BOLD}Step:{RESET} {current_step}")
            print(f"{BOLD}Agent:{RESET} {agent_id}")
            print(f"{BOLD}Time:{RESET} {datetime.now().strftime('%H:%M:%S')}")
            print()

            # Progress bar
            completed = sum(1 for p in phases if p.get('status') == 'COMPLETED')
            total = 7
            progress = int((completed / total) * 40)
            bar = f"{GREEN}{'█' * progress}{GRAY}{'░' * (40 - progress)}{RESET}"
            print(f"Progress: [{bar}] {completed}/{total} phases")
            print()

            # Phases
            print(f"{BOLD}TDD Phases:{RESET}")
            print("─" * 60)

            for phase in phases:
                idx = phase.get('phase_index', '?')
                name = phase.get('phase_name', 'Unknown')
                status = phase.get('status', 'NOT_STARTED')
                outcome = phase.get('outcome', '')
                duration = phase.get('duration_minutes', 0)
                notes = phase.get('notes', '')

                symbol = get_phase_symbol(status)
                duration_str = format_duration(duration) if duration else ""

                if status == "COMPLETED":
                    outcome_color = GREEN if outcome == "PASS" else RED
                    print(f"{symbol} Phase {idx}: {BOLD}{name}{RESET} [{outcome_color}{outcome}{RESET}] {GRAY}{duration_str}{RESET}")
                elif status == "IN_PROGRESS":
                    print(f"{symbol} Phase {idx}: {BOLD}{name}{RESET} [{YELLOW}IN PROGRESS{RESET}]")
                else:
                    print(f"{symbol} Phase {idx}: {GRAY}{name}{RESET}")

                # Show notes for last completed/in-progress phase
                if notes and (status == "COMPLETED" or status == "IN_PROGRESS"):
                    note_lines = notes.split('\n')
                    for line in note_lines[:2]:  # First 2 lines only
                        print(f"    {GRAY}↳ {line[:70]}{RESET}")

            print("─" * 60)
            print()

            # Activity indicator
            spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            spin = spinner[iteration % len(spinner)]

            # Check if agent still running
            if agent_output_path.exists():
                size = agent_output_path.stat().st_size / 1024  # KB
                print(f"{spin} Agent active | Output: {size:.1f} KB | Press Ctrl+C to exit")
            else:
                print(f"{RED}⚠ Agent output file not found{RESET}")

            # Detect completion
            if completed == total:
                print()
                print(f"{GREEN}{BOLD}🎉 Step {current_step} COMPLETE!{RESET}")
                break

            # Detect new phase
            if completed > last_phase_count:
                # Beep on progress
                print('\a', end='', flush=True)
                last_phase_count = completed

        except FileNotFoundError:
            print(f"{RED}❌ execution-log.yaml not found{RESET}")
        except Exception as e:
            print(f"{RED}❌ Error: {e}{RESET}")

        time.sleep(2)  # Update every 2 seconds

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 /tmp/monitor_step.py <agent_id>")
        sys.exit(1)

    try:
        monitor_step(sys.argv[1])
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Monitor stopped by user{RESET}")
        sys.exit(0)
