#!/usr/bin/env python3

from utils import copy_workflow_file
from pathlib import Path
import os
import sys
import git  # From GitPython
import json
from github import Github, GithubException, Auth # From PyGithub
from github.GithubException import UnknownObjectException

# ==========================================
# CONFIGURATION - CHANGE THESE VARIABLES
# ==========================================
ORG = "my-rha-calvary"           # Replace with your actual GitHub Org name
REPOS = []
TOKEN = ""
TEAM_SLUG = "my-rha-cal-team"    # Replace with your team slug
# ==========================================

def read_config(config):
    with open(config, 'r') as file:
        config_data = json.load(file)
    return config_data


def get_oganisation(config_data):
    return (config_data.get("organisation", None))


def get_repos(config_data):
    return (config_data.get("repos", None))


def set_env(config):
    # Configure Git committer identity for GitPython
    global ORG, REPOS, TOKEN
    config_data = read_config(config)

    os.environ["GIT_COMMITTER_NAME"] = "GitHub Action"
    os.environ["GIT_COMMITTER_EMAIL"] = "actions@github.com"
    os.environ["GIT_AUTHOR_NAME"] = "GitHub Action"
    os.environ["GIT_AUTHOR_EMAIL"] = "actions@github.com"
    ORG = get_oganisation(config_data)
    REPOS = get_repos(config_data)
    TOKEN = os.environ.get("GITHUB_TOKEN")



def github_auth():
    # 0. Authenticate with GitHub SDK
    if not TOKEN:
        print("Error: Please set the GITHUB_TOKEN environment variable.")
        sys.exit(1)

    # g = Github(token)
    auth = Auth.Token(TOKEN)
    return auth


def check_repo_exists(auth, repo_name):
    g = Github(auth=auth)
    try:
        g.get_repo(f"{ORG}/{repo_name}")
        return True
    except UnknownObjectException:
        return False
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


def onboard_repos(auth):
    repos = REPOS
    for repo in repos:
        repo_name = repo.get("repo_name", None)
        repo_team_slug = repo.get("team_slug", None)
        repo_type = repo.get("repo_type", "infra")
        if repo_name is None or repo_team_slug is None:
            raise Exception(f"Review the configuration: {repo_name} or {repo_team_slug} cannot be None")

        repo_exists = check_repo_exists(auth, repo_name)
        if repo_exists:
            print(f"{ORG}/{repo_name} already exists - skipping ...")
            continue

        onboard_repo(auth, repo_name, repo_type, repo_team_slug)


def onboard_repo(auth, repo_name, repo_type, team_slug):
    g = Github(auth=auth)
    try:
        org = g.get_organization(ORG)
    except GithubException as e:
        print(f"Failed to access organization '{ORG}': {e.data.get('message')}")
        sys.exit(1)

    # Automatically fetch the real Team ID based on the Slug
    print(f"🔍 Looking up team ID for '{team_slug}'...")
    try:
        team = org.get_team_by_slug(team_slug)
        actual_team_id = team.id
        print(f"✅ Found team '{team_slug}' (ID: {actual_team_id})")
    except GithubException as e:
        print(f"❌ Failed to find team '{team_slug}'. Make sure it exists and your token has org read access.")
        sys.exit(1)

    full_repo = f"{ORG}/{repo_name}"

    # 1. Create Repository via GitHub SDK
    print(f"🚀 Creating repository: {full_repo}...")
    try:
        github_repo = org.create_repo(
            name=repo_name,
            private=False, #TODO set to True in CalvaryCare org.
            auto_init=False
        )
    except GithubException as e:
        print(f"Failed to create repository: {e.data.get('message')}")
        sys.exit(1)

    print(f"🔑 Granting '{team_slug}' maintain access to {repo_name}...")
    try:
        team.update_team_repository(github_repo, "maintain")
        print("✅ Access granted successfully.")
    except GithubException as e:
        print(f"❌ Failed to grant access: {e.data.get('message')}")

    # 2. Local File Generation
    os.makedirs(repo_name, exist_ok=True)
    os.chdir(repo_name)

    open(".gitignore", "w").close()

    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/CODEOWNERS", "w") as f:
        f.write(f"* @{ORG}/{team_slug}\n")

    repo_root = Path(__file__).resolve().parent
    src_dir = Path(repo_root / "templates" / f"{repo_type}")
    dst_dir = ".github/workflows"
    for src_path in src_dir.glob("*.yaml"):

        # Ensure we are only reading files (skips nested folders if any)
        if src_path.is_file():
            # Match the exact filename for the destination
            dst_path = dst_dir / src_path.name

            try:
                # Read from the template
                with open(src_path, "r", encoding="utf-8") as f_src:
                    file_content = f_src.read()

                # Write to the workflows directory
                with open(dst_path, "w", encoding="utf-8") as f_dst:
                    f_dst.write(file_content)

                print(f"Processed: {src_path.name} -> {dst_path.name}")

            except Exception as e:
                print(f"Failed to process {src_path.name}: {e}")


#     print("🛠️ Templating CI workflow...")
#     ci_workflow = f"""name: CI Pipeline ({repo_name})

# on:
#   push:
#     branches: [ main ]

# jobs:
#   validate:
#     name: Build & Test
#     runs-on: ubuntu-latest

#     steps:
#       - name: Checkout Code
#         uses: actions/checkout@v4

#       - name: Run Diagnostics
#         run: |
#           echo "Validating repository: {full_repo}"
#           echo "Running placeholder testing suites..."
# """
#     with open(".github/workflows/ci.yml", "w") as f:
#         f.write(ci_workflow)

#     print("🚀 Templating Multi-Environment Matrix CD workflow...")
#     cd_workflow = f"""name: CD Pipeline ({repo_name})

# on:
#   push:
#     branches: [ main ]

# jobs:
#   deploy:
#     name: Deploy to ${{{{ matrix.environment }}}}
#     runs-on: ubuntu-latest

#     strategy:
#       max-parallel: 1
#       matrix:
#         environment: [nonprod, prod]

#     environment: ${{{{ matrix.environment }}}}

#     steps:
#       - name: Checkout Code
#         uses: actions/checkout@v4

#       - name: Multi-Env Deployment Execution
#         run: |
#           echo "Executing deployment pipeline step for {repo_name}"
#           echo "Current Target Environment: ${{{{ matrix.environment }}}}"
#           echo "Deployment initiated successfully!"
# """
#     with open(".github/workflows/cd.yml", "w") as f:
#         f.write(cd_workflow)

    # 3. Git Operations via GitPython SDK
    print("📦 Initializing local Git repository and pushing via HTTPS...")
    local_repo = git.Repo.init(".")

    local_repo.index.add([".gitignore", ".github"])
    local_repo.index.commit("Initial commit: workflows with multi-env matrix strategy")

    local_repo.git.branch("-M", "main")

    os.environ["GIT_TERMINAL_PROMPT"] = "0"

    # Use 'x-access-token' as the username for GitHub App installation tokens
    auth_https_url = f"https://x-access-token:{TOKEN}@github.com/{ORG}/{repo_name}.git"

    remote = local_repo.create_remote("origin", auth_https_url)
    local_repo.git.push("-u", "origin", "main")

    print("✅ Main branch created and pushed with Matrix CI/CD workflows.")

    # 4. Apply Main Branch Protection Rules via GitHub SDK
    print("🔒 Applying branch protection rules to 'main'...")
    main_branch = github_repo.get_branch("main")
    main_branch.edit_protection(
        enforce_admins=True,
        required_approving_review_count=1,
        require_code_owner_reviews=True,
        dismiss_stale_reviews=True
    )

    # 5. Create Environments via SDK underlying API
    print("🌐 Creating 'nonprod' environment...")
    github_repo._requester.requestJsonAndCheck(
        "PUT",
        f"{github_repo.url}/environments/nonprod"
    )

    print("🌐 Creating 'production' environment with protections...")
    github_repo._requester.requestJsonAndCheck(
        "PUT",
        f"{github_repo.url}/environments/prod",
        input={
            "prevent_self_review": True,
            "reviewers": [
                {
                    "type": "Team",
                    "id": actual_team_id  # Using the dynamically fetched ID!
                }
            ]
        }
    )

    print(f"🎉 Repository {repo_name} successfully automated with sequential Matrix pipelines!")


def main():
    config = "config/config.json"
    set_env(config)
    auth = github_auth()
    onboard_repos(auth)


if __name__ == "__main__":
    main()
