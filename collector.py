"""GRC Evidence Collector: Checks GitHub settings and maps results to controls."""
import os
import hashlib
import json
import os
from datetime import datetime, timezone
import requests
import yaml

REPO = "CowboyQueen/grc-evidence-collector"
API = "https://api.github.com"
def load_token():
    """Get the token from environment, or from the .env file."""
    token = os.getenv("GITHUB_TOKEN")
    if not token and os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    token = line.strip().split("=", 1)[1]
    if not token:
        raise SystemExit("GITHUB_TOKEN not found. Add it to your .env file.")
    return token


def load_catalog():
    """read controls.yaml and return each check, looked up by its id."""
    with open("controls.yaml") as f:
        catalog = yaml.safe_load(f)
        return {check["id"]: check for check in catalog["checks"]}

def fetch_branch_protection(headers, repo, branch):
    """Fetch branch protection once, for every check that needs it."""
    url = f"{API}/repos/{repo}/branches/{branch}/protection"
    try:
        response = requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as exc:
        return {"error": type(exc).__name__}
    if response.status_code == 404:
        return {"protected": False}
    if response.status_code != 200:
        return {"error": f"status {response.status_code}"}
    return {"protected": True, "rules": response.json()}
    
def check_branch_protected(context):
    """GH-01: Is the default branch protected?

    Returns (status, detail). Status is "pass", "fail", or "error".
    """
    protection = context["protection"]
    branch = context["branch"]
    if "error" in protection:
        return "error", f"Could not read branch protection ({protection['error']}); could not verify."
    if protection["protected"]:
        return "pass", f"Branch '{branch}' has protection rules."
    return "fail", f"Branch '{branch}' has no protection rules."


def check_pr_reviews_required(context):
    """GH-02: Do pull requests need at least one approving review?

    Returns (status, detail). Status is "pass", "fail", or "error".
    """
    protection = context["protection"]
    if "error" in protection:
        return "error", f"Could not read branch protection ({protection['error']}); could not verify."
    if not protection["protected"]:
        return "fail", "No branch protection, so reviews are not required."
    reviews = protection["rules"].get("required_pull_request_reviews")
    if not reviews:
        return "fail", "No review required."
    count = reviews.get("required_approving_review_count", 0)
    if count == 0:
        return "fail", "Pull requests do not require any reviews."
    return "pass", f"{count} approving review(s) required before merging."


def check_secret_scanning(context):
    """GH-03: Is secret scanning enabled?

    Returns (status, detail). Status is "pass", "fail", or "error".
    """
    repo_info = context["repo_info"]
    section = repo_info.get("security_and_analysis")
    if section is None:
        return "error", "Secret scanning settings not visible to this token; could not verify."
    scanning = section.get("secret_scanning", {})
    status = scanning.get("status")
    if status is None:
        return "error", "Secret scanning status not reported; could not verify."
    if status == "enabled":
        return "pass", "Secret scanning is enabled."
    return "fail", f"Secret scanning is {status}."


def check_dependabot(context):
    """GH-04: Are Dependabot security updates enabled?

    Returns (status, detail). Status is "pass", "fail", or "error".
    """
    repo_info = context["repo_info"]
    section = repo_info.get("security_and_analysis")
    if section is None:
        return "error", "Security settings not visible to this token; could not verify."
    dependabot = section.get("dependabot_security_updates", {})
    status = dependabot.get("status")
    if status is None:
        return "error", "Dependabot security updates status not reported; could not verify."
    if status == "enabled":
        return "pass", "Dependabot security updates are enabled."
    return "fail", f"Dependabot security updates are {status}."


CHECKS = {
    "GH-01": check_branch_protected,
    "GH-02": check_pr_reviews_required,
    "GH-03": check_secret_scanning,
    "GH-04": check_dependabot,
}


def save_evidence(results):
    """Write results to a timestamped JSON file, with a SHA-256 hash file beside it."""
    collected_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    evidence = {
        "repository": REPO,
        "collected_at": collected_at,
        "collector_version": "0.1",
        "results": results,
    }
    body = json.dumps(evidence, indent=2, sort_keys=True)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()

    os.makedirs("evidence", exist_ok=True)
    stamp = collected_at.replace(":", "").replace("-", "")
    filename = f"evidence_{stamp}.json"
    with open(f"evidence/{filename}", "w") as f:
        f.write(body)
    with open(f"evidence/{filename}.sha256", "w") as f:
        f.write(f"{digest}  {filename}\n")
    return filename, digest


def print_result(check_id, catalog, status, detail):
    """Print one check result with its mapped controls."""
    check = catalog[check_id]
    frameworks = check["frameworks"]
    controls = ", ".join(frameworks["nist_800_53"] + frameworks["soc2"])
    print(f"[{status.upper()}] {check_id} {check['title']}")
    print(f"       {detail}")
    print(f"       Controls: {controls}")


def main():
    headers = {
        "Authorization": f"Bearer {load_token()}",
        "Accept": "application/vnd.github+json",
    }
    catalog = load_catalog()

    try:
        response = requests.get(f"{API}/repos/{REPO}", headers=headers, timeout=30) 
    except requests.RequestException as exc:
        raise SystemExit(f"Could not reach GitHub ({type(exc).__name__}).")  
    if response.status_code != 200:
        raise SystemExit(f"Could not read {REPO} (status {response.status_code}).")
    repo_info = response.json()
    branch = repo_info["default_branch"]
    context = {
        "repo_info": repo_info,
        "branch": branch,
        "protection": fetch_branch_protection(headers, REPO, branch),
    }
    results = []
    for check_id in catalog:
        check_function = CHECKS.get(check_id)
        if check_function is None:
            status, detail = "error", "No code exists for this check; could not verify."
        else:
            status, detail = check_function(context)
        print_result(check_id, catalog, status, detail)
        results.append({
            "check_id": check_id,
            "title": catalog[check_id]["title"],
            "status": status,
            "detail": detail,
            "frameworks": catalog[check_id]["frameworks"],
        })
    filename, digest = save_evidence(results)
    print(f"\nEvidence saved: evidence/{filename}")
    print(f"SHA-256: {digest}")

if __name__ == "__main__":
    main()
    