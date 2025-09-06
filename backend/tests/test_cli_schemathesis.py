#!/usr/bin/env python
"""
CLI runner for Schemathesis tests.
Can be run directly or via pytest.
"""

import subprocess
import sys


def run_schemathesis_cli():
    """Run Schemathesis via CLI for comprehensive API testing."""

    commands = [
        # Basic schema validation
        [
            "schemathesis",
            "run",
            "http://localhost:8000/openapi.json",
            "--base-url",
            "http://localhost:8000",
            "--checks",
            "all",
            "--hypothesis-max-examples",
            "10",
            "--hypothesis-deadline",
            "5000",
            "--show-errors-tracebacks",
        ],
        # Stateful testing
        [
            "schemathesis",
            "run",
            "http://localhost:8000/openapi.json",
            "--base-url",
            "http://localhost:8000",
            "--stateful",
            "links",
            "--hypothesis-max-examples",
            "5",
            "--show-errors-tracebacks",
        ],
        # Negative testing
        [
            "schemathesis",
            "run",
            "http://localhost:8000/openapi.json",
            "--base-url",
            "http://localhost:8000",
            "--checks",
            "negative_data_rejection",
            "--hypothesis-max-examples",
            "20",
            "--show-errors-tracebacks",
        ],
    ]

    print("=" * 60)
    print("Running Schemathesis CLI Tests")
    print("=" * 60)
    print("\nMake sure the API server is running at http://localhost:8000")
    print("Run with: uvicorn backend.main:app --reload")
    print("=" * 60)

    for i, cmd in enumerate(commands, 1):
        print(f"\n[Test Suite {i}/{len(commands)}]")
        print(f"Command: {' '.join(cmd)}")
        print("-" * 40)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            if result.returncode != 0:
                print(f"Test suite {i} failed with return code {result.returncode}")
        except FileNotFoundError:
            print("Schemathesis CLI not found. Install with: pip install schemathesis")
            sys.exit(1)
        except Exception as e:
            print(f"Error running test suite {i}: {e}")

    print("\n" + "=" * 60)
    print("All Schemathesis CLI tests completed")
    print("=" * 60)


if __name__ == "__main__":
    run_schemathesis_cli()
