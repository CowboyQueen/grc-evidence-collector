"""Check every evidence file against the append-only ledger."""
import hashlib
import json
import os
import sys

from ledger import GENESIS, LEDGER

EVIDENCE_DIR = "evidence"


def sha256_of(path):
    """Fingerprint a file's exact bytes."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    problems = []
    seen = {}
    prev = GENESIS

    with open(LEDGER) as f:
        lines = [line.rstrip("\n") for line in f if line.strip()]

    for number, line in enumerate(lines, start=1):
        entry = json.loads(line)
        if entry["prev"] != prev:
            problems.append(f"line {number}: chain broken (ledger altered before this line)")
        prev = hashlib.sha256(line.encode("utf-8")).hexdigest()

        name = entry["file"]
        if name in seen:
            problems.append(f"line {number}: {name} recorded twice (lines {seen[name]} and {number})")
        seen[name] = number

        path = os.path.join(EVIDENCE_DIR, name)
        if not os.path.exists(path):
            problems.append(f"{name}: in ledger but missing from {EVIDENCE_DIR}/")
        elif sha256_of(path) != entry["sha256"]:
            problems.append(f"{name}: FAILED, contents differ from the ledger")
        else:
            print(f"{name}: OK")

    for name in sorted(os.listdir(EVIDENCE_DIR)):
        if name.endswith(".json") and name not in seen:
            problems.append(f"{name}: not in ledger (unrecorded evidence)")

    if problems:
        print("\nINTEGRITY PROBLEMS:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print(f"\nAll {len(lines)} ledger entries verified; chain intact.")


if __name__ == "__main__":
    main()
    