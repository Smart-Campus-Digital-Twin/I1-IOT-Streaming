#!/usr/bin/env python3
"""
MQTT Payload Schema Validator

Validates a JSON payload against contracts/payload.schema.json.

Usage:
  python scripts/validate-payload.py < payload.json
  python scripts/validate-payload.py payload.json
  echo '{"sensor_id": "...", ...}' | python scripts/validate-payload.py

Exit codes:
  0 = payload is valid
  1 = payload is invalid or schema not found
"""

import sys
import json
import argparse
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:
    print("ERROR: jsonschema library not installed. Install with: pip install jsonschema")
    sys.exit(1)


def load_schema(schema_path: Path) -> dict:
    """Load JSON Schema from file."""
    try:
        with open(schema_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Schema file not found: {schema_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Schema file is not valid JSON: {e}")
        sys.exit(1)


def load_payload(payload_arg: str) -> dict:
    """Load payload from file or stdin."""
    try:
        if payload_arg == "-" or payload_arg is None:
            # Read from stdin
            payload_text = sys.stdin.read()
        else:
            # Try to read as file first
            path = Path(payload_arg)
            if path.exists() and path.is_file():
                with open(path, "r") as f:
                    payload_text = f.read()
            else:
                # Treat as raw JSON string
                payload_text = payload_arg
        
        return json.loads(payload_text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Payload is not valid JSON: {e}")
        sys.exit(1)


def validate_payload(payload: dict, schema: dict) -> bool:
    """Validate payload against schema. Return True if valid, False otherwise."""
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(payload))
    
    if errors:
        print(f"INVALID: {len(errors)} validation error(s):\n")
        for i, error in enumerate(errors, 1):
            path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
            print(f"  [{i}] Path: {path}")
            print(f"      Message: {error.message}")
            if error.validator_value is not None:
                print(f"      Constraint: {error.validator} = {error.validator_value}")
            print()
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Validate MQTT sensor payload against contracts/payload.schema.json"
    )
    parser.add_argument(
        "payload",
        nargs="?",
        default="-",
        help="Path to payload JSON file, or raw JSON string, or '-' for stdin (default: stdin)"
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=None,
        help="Path to schema JSON file (default: contracts/payload.schema.json relative to repo root)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print exit code (suppress text output)"
    )
    
    args = parser.parse_args()
    
    # Determine schema path
    if args.schema:
        schema_path = args.schema
    else:
        # Look for schema in standard location
        current_dir = Path(__file__).parent
        repo_root = current_dir.parent
        schema_path = repo_root / "contracts" / "payload.schema.json"
    
    # Load and validate
    schema = load_schema(schema_path)
    payload = load_payload(args.payload)
    
    is_valid = validate_payload(payload, schema)
    
    if not args.quiet:
        if is_valid:
            print(f"✓ VALID: Payload conforms to schema")
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
