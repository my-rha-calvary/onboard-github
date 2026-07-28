#!/usr/bin/env python3

import os
import sys
import git  # From GitPython
from github import Github, GithubException, Auth # From PyGithub

# ==========================================
# CONFIGURATION - CHANGE THESE VARIABLES
# ==========================================
ORG = "my-rha-calvary"           # Replace with your actual GitHub Org name
TEAM_SLUG = "my-rha-cal-team"    # Replace with your team slug
# Replace the interactive input section with:

# ==========================================


def main():
    repo_name = os.environ.get("REPO_NAME", "").strip()
    if not repo_name:
        print("Error: REPO_NAME environment variable is required.")
        sys.exit(1)

    # Configure Git committer identity for GitPython
    os.environ["GIT_COMMITTER_NAME"] = "GitHub Action"
    os.environ["GIT_COMMITTER_EMAIL"] = "actions@github.com"
    os.environ["GIT_AUTHOR_NAME"] = "GitHub Action"
    os.environ["GIT_AUTHOR_EMAIL"] = "actions@github.com"

    # 0. Authenticate with GitHub SDK
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: Please set the GITHUB_TOKEN environment variable.")
        sys.exit(1)

    # g = Github(token)
    auth = Auth.Token(token)
    g = Github(auth=auth)

    try:
        org = g.get_organization(ORG)
    except GithubException as e:
        print(f"Failed to access organization '{ORG}': {e.data.get('message')}")
        sys.exit(1)

    # Automatically fetch the real Team ID based on the Slug
    print(f"🔍 Looking up team ID for '{TEAM_SLUG}'...")
    try:
        team = org.get_team_by_slug(TEAM_SLUG)
        actual_team_id = team.id
        print(f"✅ Found team '{TEAM_SLUG}' (ID: {actual_team_id})")
    except GithubException as e:
        print(f"❌ Failed to find team '{TEAM_SLUG}'. Make sure it exists and your token has org read access.")
        sys.exit(1)

    # Prompt for the new repository name
    try:
        repo_name = input("Enter new repository name: ").strip()
        if not repo_name:
            print("Repository name cannot be empty.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)

    full_repo = f"{ORG}/{repo_name}"

    # 1. Create Repository via GitHub SDK
    print(f"🚀 Creating repository: {full_repo}...")
    try:
        github_repo = org.create_repo(
            name=repo_name,
            private=False,
            auto_init=False
        )
    except GithubException as e:
        print(f"Failed to create repository: {e.data.get('message')}")
        sys.exit(1)

    print(f"🔑 Granting '{TEAM_SLUG}' maintain access to {repo_name}...")
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
        f.write(f"* @{ORG}/{TEAM_SLUG}\n")

    print("🛠️ Templating CI workflow...")
    ci_workflow = f"""name: CI Pipeline ({repo_name})

on:
  pull_request:
    branches: [ main ]

jobs:
  validate:
    name: Build & Test
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Run Diagnostics
        run: |
          echo "Validating repository: {full_repo}"
          echo "Running placeholder testing suites..."
"""
    with open(".github/workflows/ci.yml", "w") as f:
        f.write(ci_workflow)

    print("🚀 Templating Multi-Environment Matrix CD workflow...")
    cd_workflow = f"""name: CD Pipeline ({repo_name})

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    name: Deploy to ${{{{ matrix.environment }}}}
    runs-on: ubuntu-latest

    strategy:
      max-parallel: 1
      matrix:
        environment: [test, production]

    environment: ${{{{ matrix.environment }}}}

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Multi-Env Deployment Execution
        run: |
          echo "Executing deployment pipeline step for {repo_name}"
          echo "Current Target Environment: ${{{{ matrix.environment }}}}"
          echo "Deployment initiated successfully!"
"""
    with open(".github/workflows/cd.yml", "w") as f:
        f.write(cd_workflow)

    # 3. Git Operations via GitPython SDK
    print("📦 Initializing local Git repository and pushing via HTTPS...")
    local_repo = git.Repo.init(".")

    local_repo.index.add([".gitignore", ".github"])
    local_repo.index.commit("Initial commit: workflows with multi-env matrix strategy")

    local_repo.git.branch("-M", "main")

    auth_https_url = github_repo.clone_url.replace("https://", f"https://{token}@")

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
    print("🌐 Creating 'test' environment...")
    github_repo._requester.requestJsonAndCheck(
        "PUT",
        f"{github_repo.url}/environments/test"
    )

    print("🌐 Creating 'production' environment with protections...")
    github_repo._requester.requestJsonAndCheck(
        "PUT",
        f"{github_repo.url}/environments/production",
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

if __name__ == "__main__":
    main()
