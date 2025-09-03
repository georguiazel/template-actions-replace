#!/usr/bin/env python3
import argparse
import json
import os
import sys
import io


# Ensure stdout uses UTF-8 encoding
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass


def parse_replacements(raw: str):
    """
    Converts 'A.B=1|C=2' into a list of pairs [('A.B', 1), ('C', 2)] with automatic casting:
      - 5, 3.14 → number
      - true/false/null → bool/None
      - everything else → string (quotes not required)
    """
    replacements = []
    for pair in raw.split("|"):
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        key = key.strip()

        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value.strip().strip('"').strip("'")
        replacements.append((key, parsed_value))
    return replacements


def set_by_path(obj, path_parts, value):
    """Creates intermediate dicts if they don’t exist and assigns the value at the end of the path."""
    current = obj
    for k in path_parts[:-1]:
        if k not in current or not isinstance(current[k], dict):
            current[k] = {}
        current = current[k]
    current[path_parts[-1]] = value


def set_value(obj, key, value):
    """
    Rules:
      - 'nested:K1.K2'  -> treat dots as a nested path
      - 'literal:K1.K2' -> treat the key literally (with dots)
      - default: if a literal key exists -> replace it; otherwise use nested path
    """
    if key.startswith("nested:"):
        dotted = key[len("nested:"):]
        set_by_path(obj, dotted.split("."), value)
        return

    if key.startswith("literal:"):
        literal = key[len("literal:"):]
        obj[literal] = value
        return

    if key in obj:
        obj[key] = value
    else:
        set_by_path(obj, key.split("."), value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", required=True, help="List of files separated by |")
    parser.add_argument("--replacements", required=True, help="Key=value pairs separated by |")
    args = parser.parse_args()

    files = [f for f in args.files.split("|") if f.strip()]
    replacements = parse_replacements(args.replacements)

    if not files:
        print("[X] No files received in --files", file=sys.stderr)
        sys.exit(1)
    if not replacements:
        print("[X] No replacements received in --replacements", file=sys.stderr)
        sys.exit(1)

    for file in files:
        if not os.path.exists(file):
            print(f"[X] File not found: {file}", file=sys.stderr)
            sys.exit(1)

        print(f"Processing file: {file}")
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"[X] File is not valid JSON: {file}", file=sys.stderr)
            sys.exit(1)

        # Apply replacements
        for key, val in replacements:
            set_value(data, key, val)

        # Write back updated JSON
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[OK] File updated: {file}")

        # Print updated content
        try:
            with open(file, "r", encoding="utf-8") as f:
                print("------ updated content ------")
                print(f.read())
                print("------ end of file ------")
        except Exception:
            pass


if __name__ == "__main__":
    main()
