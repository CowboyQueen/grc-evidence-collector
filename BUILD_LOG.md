# Build Log: GRC Evidence Collector

A public record of building a compliance automation tool from scratch,
with the GRC control behind each step.

## Step 1: Checked my toolchain — 10-20- 2026
**Goal** Confirm toolchain before building
**What I did:** Checked Git and Python versions in Cursor's terminal
**What I learned:** python and python3, and what "not on the PATH" means (the system did not find a program by name)
**GRC connection:** This is a mini baseline configuration check. Before trusting a system, you record what's installed and which version. That is NIST 800-53 CM-2 (Baseline Configuration) and CM-8 (System Component Inventory)
**Obstacle:** Python not sound and resolved with Python3. Found I was in Cursor's cloud and not my machine (ties to CM-8, system boundary). Knowing exactly where a system runs is a beginning question in any audit.

## Step 2: Setup WSL and configure Git — 10-20-2026
**Goal** Setup Linux environment and configure Git so work is attibuted to me
**What I did:** Installed WSL with Ubuntu 24.04.5 LTS (Windows Powershell as admin wsl --install, then wsl --update)
Created my Linux user and patched the system with (sudo apt update && sudo apt upgrade -y)
Moved from Windows filesystem (/mnt/c/users/) to my Linux home folder (~) since projects run faster and to avoid line-ending issues
Configured Git with
    My name
    my GitHub noreply email, so my real email remains private
    {main} as the default branch
    {core.autocrlf input} to handle Windows vs Linux line endings
**What I learned:** How to read the shell prompt username@mchine:location
Nothing after a command usually means it was successful
A "usage" message means bad syntax, not that it is broken
To check what a command saved instead of assuming it worked
**GRC connection:** SI-2 (Flaw remediation): patched the system before using it
Selecting an LTS release: auditors ask if a system runs vendor supported versions
AU-3/CM-3: every commit is attributable to a named author which  is the audit trail
Private email- privacy-by-design choice
**Obstacle:** WSL was not installed yet, so I installed
Pasting several {git config} commands at once failed with a usage error, and confirmed nothing was saved. fixed with typing one at a time and verifying each one. 
Connected WSL to GitHub with an SSH key. To eventually push code, you need to authenticated. An SSH key is a pair. Private key remains on the device and public key goes to GitHub

# Step 3: SSH key created and authenticated to GitHub — 10-20-2026
**Goal** Connect securely to prepare for push to GitHub
**What I did:** Created a connection to GitHub on my device by creating an SSH key fingerprint
**What I learned:** How to create the public/private key and hands-on understanding of why private never leaves my device
**GRC connection:** IA-2 (Identification and Authentication), IA-5 (Authenticator Management:the passphrase ptotects the key), and verifying the host fingerprint guards against impresonation, as in SC-23 (Session Authenticity)
**Obstacle:** No obstacles to report getting this completed

# Step 4: Create Project repository —10-21-2026
**Goal** Create and clone a repo
**What I did:** Created a repository in GitHub named "grc-evidence-collector" and added README file, .gitignore with a Python template and MIT license. selected SSH address and created the projects folder and connected GitHub with copied address. Inspected with {ls -la} and {git log --oneline}. Opened in Cursor from WSL and confirmed connection at the bottom left shows WSL:Ubuntu-24045
**What I learned:** A respository is the project files along with the history and stored in a hidden folder.
A license tells others how they can use and public repos should always include one
Every commit has a unique ID
{HEAD -> main, original/main means local and GitHub copy are synced}
**GRC connection:** CM-3 (Configuration Change Control) version conteol gives complete and ordered histoery of all changes
AU-9 (Protection of Audit Info) Commit IDs are content hashes so if altered, IDs change. That isthe same tamper IDs an evidence collector uses with SHA-256. {.gitignore} is a preventitive control against leaking secrets, relating to IA-5 and SC-28
**Obstacle:** Has a typo for the {git log}. Typed "online" instead of "oneline", Git errored as "unrecognized argument" rather than guessing. Cursor's New Text File creates and unnamed file with no location; New File in the Explorer panel is best.

# Step 5: Complete first push to Git — 10-21-2026
**Goal** Open the project in Cursor, create the build log, commit and push
**What I did:** Completed the first full cycle of a real change to the project, that will continue in each push (edit->stage->commit->push). Created a file in Cursor within the project. added all steps completed thus far, and completed a push to the Github repo
**What I learned:** How to connect create a file within the project. How to save changes and to prview before push. Stage {git add} which is a review before completing a push.
**GRC connection:** Staging is a puposeful review point where you choose what goes into the change, which is the same idea (CM-3) reviewing changes before approval
**Obstacle:** No obstacles to report getting this completed

# Step 6: Setup Python virtual environment — 10-22-2026
**Goal** Create a virtual environment to have a private folder of libraries just for this project
**What I did:** Installed venv tool, created hidden folder, and turned it on. Did the [.gitignore] so it does not got to GitHub
**What I learned:** What a virtual environment is, what a requirements file does, and that [pip list] shows dependencies that were not directly requested
**GRC connection:** a requirements file is a software inventory (CM-8, SR-4 supply chain)
**Obstacle:** No obstacles in completing.

# Step 7: Write the control catalog — 10-22-2026
**Goal** create a file that includes mapped controls, validate and commit
**What I did:** Created a yaml control folder. Created 4 controls mapped to NIST 800.53 and SOC2 in yaml. 
**What I learned:** YAML syntax, that keys are case, and indentation sensitive and how to read NIST contols
**GRC connection:** control mapping, "test once, comply many,"and that each mapped control is a claim you must be able to defend to and explain during audits
**Obstacle:** First round included a stray yaml line; Decsription vs description (case sensitivity matters). It is not the amount of controls, overmapping. It inflates coverage and falls apart during the testing phase. Short and defensible is best.

# Step 8: First call to the GitHub API — 10-22-2026
**Goal** Creating the code that walks through the catalog
**What I did:** Made sure secrets cannot be committed (before creating any),
**What I learned:** 
**GRC connection:** 
**Obstacle:** 