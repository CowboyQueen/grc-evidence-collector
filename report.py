"""Build an HTML dashboard from the newest evidence file."""
import json
import os

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

EVIDENCE_DIR = "evidence"
OUTPUT_DIR = "site"


def newest_evidence():
    """Return the file name of the most recent evidence file."""
    files = sorted(
        name for name in os.listdir(EVIDENCE_DIR)
        if name.startswith("evidence_") and name.endswith(".json")
    )
    if not files:
        raise SystemExit("No evidence files found. Run collector.py first.")
    return files[-1]


def group_by_repository(results):
    """Organize results as {repository: [results]}, keeping their order."""
    groups = {}
    for result in results:
        repo = result.get("repository", "unknown")
        groups.setdefault(repo, []).append(result)
    return groups


def count_statuses(results):
    """Count how many results pass, fail, or error."""
    counts = {
        "pass": 0,
        "fail": 0,
        "error": 0,
    }
    for result in results:
        counts[result["status"]] += 1
    return counts


def load_exceptions():
    """Return accepted exceptions, looked up by (repository, check_id)."""
    with open("exceptions.yaml") as f:
        data = yaml.safe_load(f)
    lookup = {}
    for exc in data.get("exceptions", []):
        if exc.get("status") == "accepted":
            lookup[(exc["repository"], exc["check_id"])] = exc
    return lookup


def main():
    name = newest_evidence()
    with open(os.path.join(EVIDENCE_DIR, name)) as f:
        evidence = json.load(f)

    exceptions = load_exceptions()
    for result in evidence["results"]:
        if result["status"] == "fail":
            result["exception"] = exceptions.get((result["repository"], result["check_id"]))
        else:
            result["exception"] = None

    groups = group_by_repository(evidence["results"])
    env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
    html = env.get_template("dashboard.html.j2").render(
        evidence_file=name,
        collected_at=evidence["collected_at"],
        groups=groups,
        counts={repo: count_statuses(items) for repo, items in groups.items()},
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
        f.write(html)
    print(f"Dashboard built from {name}: {OUTPUT_DIR}/index.html")


if __name__ == "__main__":
    main()