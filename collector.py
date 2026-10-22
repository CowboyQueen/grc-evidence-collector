"""GRC Evidence Collector: Step 8, first call to the GitHub API."""
import os
import requests
REPO = "CowboyQueen/grc-evidence-collector"
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


def main():
    headers = {
        "Authorization": f"Bearer {load_token()}",
        "Accept": "application/vnd.github+json",
    }
    url = f"https://api.github.com/repos/{REPO}"
    response = requests.get(url, headers=headers, timeout=30)

    print("Status code:", response.status_code)
    data = response.json()
    print("Repository:", data.get("full_name"))
    print("Default branch:", data.get("default_branch"))
    print("Visibility:", data.get("visibility"))


if __name__ == "__main__":
    main()
    