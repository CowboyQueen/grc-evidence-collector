"""Append-only, hash-chained evidence ledger."""
import hashlib
import json
import os
import subprocess

LEDGER = os.environ.get("GRC_LEDGER", "/var/lib/grc-ledger/ledger.jsonl")
GENESIS = "0" * 64


def last_entry_hash():
    """Hash of the newest ledger line, or GENESIS if the ledger is empty."""
    last = None
    with open(LEDGER) as f:
        for line in f:
            if line.strip():
                last = line.rstrip("\n")
    if last is None:
        return GENESIS
    return hashlib.sha256(last.encode("utf-8")).hexdigest()


def append_to_ledger(filename, digest, collected_at):
    """Append one hash-chained entry, written as the grc-collector account."""
    entry = {
        "collected_at": collected_at,
        "file": filename,
        "prev": last_entry_hash(),
        "sha256": digest,
    }
    line = json.dumps(entry, sort_keys=True) + "\n"
    subprocess.run(
        ["sudo", "-n", "-u", "grc-collector", "/usr/bin/tee", "-a", LEDGER],
        input=line.encode("utf-8"),
        stdout=subprocess.DEVNULL,
        check=True,
    )