"""GRC Evidence Collector: Checks GitHub settings and maps results to controls."""
import os

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

    
def check_branch_protected(headers, repo, branch):
    """GH-01: Is the default branch protected?

    Returns (status, detail). Status is "pass", "fail", or "error".
    """
    url = f"{API}/repos/{repo}/branches/{branch}/protection"
    try:
        response = requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as exc:
        return "error", f"Could not reach GitHub ({type(exc).__name__}); could not verify."
    if response.status_code == 200:
        return "pass", f"Branch '{branch}' has protection rules."
    if response.status_code == 404:
        return "fail", f"Branch '{branch}' has no protection rules."
    return "error", f"Unexpected response {response.status_code}; could not verify."


def check_pr_reviews_required(headers, repo, branch):
    """GH-02: Do pull requests need at least one approving review?

    Returns (status, detail). Status is "pass", "fail", or "error".
    """
    url = f"{API}/repos/{repo}/branches/{branch}/protection"
    try:
        response = requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as exc:
        return "error", f"Could not reach GitHub ({type(exc).__name__}); could not verify."

    if response.status_code == 404:
        return "fail", "No branch protection, so reviews are not required."
    if response.status_code != 200:
        return "error", f"Unexpected response {response.status_code}; could not verify."

    protection = response.json()
    reviews = protection.get("required_pull_request_reviews")

    if not reviews:
        return "fail", "No review required."
    if reviews["required_approving_review_count"] == 0:
        return "fail", "Pull requests do not require any reviews."
    return "pass", f"{reviews['required_approving_review_count']} approving review(s) required before merging."


def check_secret_scanning(repo_info):
    """GH-03: Is secret scanning enabled?

    Returns (status, detail). Status is "pass", "fail", or "error".
    """
    section = repo_info.get("security_and_analysis")
    if section is None:
        return "error", "Security settings not visible to this token; could not verify."
    scanning = section.get("secret_scanning", {})
    status = scanning.get("status")
    if status == "enabled":
        return "pass", "Secret scanning is enabled."
    return "fail", f"Secret scanning is {status}."


def check_dependabot(repo_info):
    """GH-04: Is Dependabot security updates enabled?

    Returns (status, detail). Status is "pass", "fail", or "error".
    """
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

    status, detail = check_branch_protected(headers, REPO, branch)
    print_result("GH-01", catalog, status, detail)

    status, detail = check_pr_reviews_required(headers, REPO, branch)
    print_result("GH-02", catalog, status, detail)

    status, detail = check_secret_scanning(repo_info)
    print_result("GH-03", catalog, status, detail)

    status, detail = check_dependabot(repo_info)
    print_result("GH-04", catalog, status, detail)


if __name__ == "__main__":
    main()
    