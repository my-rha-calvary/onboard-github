#!/usr/bin/env python3
"""
Automates the creation and onboarding of GitHub repositories.

This script creates repositories, assigns team permissions, generates
the initial repository structure, copies CI/CD workflow templates,
initialises Git, pushes the first commit, configures branch protection,
and creates deployment environments based on a JSON configuration file.
"""

from pathlib import Path
import os
import sys
import git  # From GitPython
import json
from github import Github, GithubException, Auth  # From PyGithub
from github.GithubException import UnknownObjectException

# ==========================================
# CONFIGURATION - CHANGE THESE VARIABLES
# ==========================================
ORG = "my-rha-calvary"  # Replace with your actual GitHub Org name
REPOS = []
TOKEN = ""
# ==========================================


def read_config(config):
    """
    Read and parse the JSON configuration file.

    Args:
        config (str): Path to the configuration file.

    Returns:
        dict: Parsed configuration data.
    """
    with open(config, "r") as file:
        config_data = json.load(file)
    return config_data


def get_oganisation(config_data):
    """
    Retrieve the GitHub organisation name from the configuration.

    Args:
        config_data (dict): Parsed configuration data.

    Returns:
        str | None: GitHub organisation name, or None if not defined.
    """
    return config_data.get("organisation", None)

def get_repos(config_data):
    """
    Retrieve the list of repositories to be onboarded.

    Args:
        config_data (dict): Parsed configuration data.

    Returns:
        list | None: List of repository definitions, or None if not configured.
    """
    return config_data.get("repos", None)


def set_env(config):
    """
    Initialise the execution environment.

    Reads the configuration file, configures Git author/committer
    environment variables, and populates the global organisation,
    repository list, and GitHub token.

    Args:
        config (str): Path to the configuration file.
    """
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
    """
    Authenticate with GitHub using the GITHUB_TOKEN environment variable.

    Returns:
        github.Auth.Token: Authentication object used by the GitHub SDK.

    Raises:
        SystemExit: If the GITHUB_TOKEN environment variable is not set.
    """
    if not TOKEN:
        print("Error: Please set the GITHUB_TOKEN environment variable.")
        sys.exit(1)

    # g = Github(token)
    auth = Auth.Token(TOKEN)
    return auth


def check_repo_exists(auth, repo_name):
    """
    Check whether a GitHub repository already exists.

    Args:
        auth (github.Auth.Token): GitHub authentication object.
        repo_name (str): Repository name.

    Returns:
        bool: True if the repository exists, otherwise False.

    Raises:
        Exception: If an unexpected error occurs while querying GitHub.
    """
    g = Github(auth=auth)
    try:
        g.get_repo(f"{ORG}/{repo_name}")
        return True
    except UnknownObjectException:
        return False
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


def onboard_repos(auth):
    """
    Onboard all repositories defined in the configuration.

    Each repository is validated, checked for existence, and created
    if it does not already exist.

    Args:
        auth (github.Auth.Token): GitHub authentication object.

    Raises:
        Exception: If a repository configuration is invalid.
    """
    repos = REPOS
    for repo in repos:
        repo_name = repo.get("repo_name", None)
        repo_team_slug = repo.get("team_slug", None)
        repo_type = repo.get("repo_type", "infra")
        if repo_name is None or repo_team_slug is None:
            raise Exception(
                f"Review the configuration: {repo_name} or {repo_team_slug} cannot be None"
            )

        repo_exists = check_repo_exists(auth, repo_name)
        if repo_exists:
            print(f"{ORG}/{repo_name} already exists - skipping ...")
            continue

        onboard_repo(auth, repo_name, repo_type, repo_team_slug)

#TODO create functions: create folders/copy
def onboard_repo(auth, repo_name, repo_type, team_slug):
    """
    Create and initialise a GitHub repository.

    This function performs the complete repository onboarding process:
    - Creates the repository.
    - Grants team permissions.
    - Generates the local repository structure.
    - Copies workflow templates.
    - Creates the initial Git commit and pushes it.
    - Applies branch protection rules.
    - Creates GitHub deployment environments.

    Args:
        auth (github.Auth.Token): GitHub authentication object.
        repo_name (str): Name of the repository to create.
        repo_type (str): Repository template type used to select workflow templates.
        team_slug (str): GitHub team slug to grant maintain permissions.

    Raises:
        SystemExit: If a GitHub API operation fails.
    """
    g = Github(auth=auth)
    try:
        org = g.get_organization(ORG)
    except GithubException as e:
        print(f"Failed to access organization '{ORG}': {e.data.get('message')}")
        sys.exit(1)

    print(f"🔍 Looking up team ID for '{team_slug}'...")
    try:
        team = org.get_team_by_slug(team_slug)
        actual_team_id = team.id
        print(f"✅ Found team '{team_slug}' (ID: {actual_team_id})")
    except GithubException as e:
        print(
            f"❌ Failed to find team '{team_slug}'. Make sure it exists and your token has org read access."
        )
        sys.exit(1)

    full_repo = f"{ORG}/{repo_name}"

    # Create Repository via GitHub SDK
    print(f"🚀 Creating repository: {full_repo}...")
    try:
        github_repo = org.create_repo(
            name=repo_name,
            private=False,  # TODO set to True in CalvaryCare org.
            auto_init=False,
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

    repo_root = Path(__file__).resolve().parent

    # Define the new target directory path cleanly as a Path object
    repo_root = Path(__file__).resolve().parent

# Define the new target directory path cleanly as a Path object
    repo_root = Path(__file__).resolve().parent

    # Define the actions.yaml source and destination repo paths
    src_dir_actions = repo_root / "templates/actions/setup-environment"

    # Define the template source and destination repo paths
    src_dir = repo_root / "templates" / f"{repo_type}"
    target_repo_dir = repo_root / repo_name

    # Create the folder for the new repository
    target_repo_dir.mkdir(parents=True, exist_ok=True)

    # Create .gitignore using absolute paths
    gitignore_path = target_repo_dir / ".gitignore"
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write("# Default gitignore template\n")
        f.write("__pycache__/\n")

    # Create .github/workflows and .github/actions/setup-environment directories
    github_dir = target_repo_dir / ".github"
    workflows_dir = github_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    actions_dir = github_dir / "actions" / "setup-environment"
    actions_dir.mkdir(parents=True, exist_ok=True)

    # Write to CODEOWNERS using absolute paths
    codeowners_path = github_dir / "CODEOWNERS"
    with open(codeowners_path, "w", encoding="utf-8") as f:
        f.write(f"* @{ORG}/{team_slug}\n")

    # Copy Workflow Templates
    if not src_dir.exists():
        print(f"Error: Template source directory '{src_dir}' does not exist.")
    else:
        for src_path in src_dir.glob("*.yaml"):
            if src_path.is_file():
                dst_path = workflows_dir / src_path.name
                try:
                    dst_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")
                    print(f"Processed Workflow: {src_path.name} -> {dst_path.name}")
                except Exception as e:
                    print(f"Error processing workflow {src_path.name}: {e}")

    # Copy Action Templates (setup-environment)
    if not src_dir_actions.exists():
        print(f"Error: Action source directory '{src_dir_actions}' does not exist.")
    else:
        for src_path in src_dir_actions.glob("*.yaml"):
            if src_path.is_file():
                dst_path = actions_dir / src_path.name
                try:
                    dst_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")
                    print(f"Processed Action: {src_path.name} -> {dst_path.name}")
                except Exception as e:
                    print(f"Error processing action {src_path.name}: {e}")

    # Git Operations via GitPython SDK
    print("📦 Initializing local Git repository and pushing via HTTPS...")

    local_repo = git.Repo.init(str(target_repo_dir))

    files_to_stage = [
        str(target_repo_dir / ".gitignore"),
        str(target_repo_dir / ".github"),
    ]
    local_repo.index.add(files_to_stage)
    local_repo.index.commit("Initial commit: workflows with multi-env matrix strategy")
    local_repo.git.branch("-M", "main")
    os.environ["GIT_TERMINAL_PROMPT"] = "0"

    # Use 'x-access-token' as the username for GitHub App installation tokens
    auth_https_url = f"https://x-access-token:{TOKEN}@github.com/{ORG}/{repo_name}.git"
    remote = local_repo.create_remote("origin", auth_https_url)
    remote.push(refspec="main:main", set_upstream=True)

    print("✅ Main branch created and pushed with Matrix CI/CD workflows.")

    # Apply Main Branch Protection Rules via GitHub SDK
    print("🔒 Applying branch protection rules to 'main'...")
    main_branch = github_repo.get_branch("main")
    main_branch.edit_protection(
        enforce_admins=True,
        required_approving_review_count=1,
        require_code_owner_reviews=True,
        dismiss_stale_reviews=True,
    )

    # Create Environments via SDK underlying API
    print("🌐 Creating 'nonprod' environment...")
    github_repo._requester.requestJsonAndCheck(
        "PUT", f"{github_repo.url}/environments/nonprod"
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
                    "id": actual_team_id,  # Using the dynamically fetched ID!
                }
            ],
        },
    )

    print(
        f"🎉 Repository {repo_name} successfully automated with sequential Matrix pipelines!"
    )


def main():
    """
    Entry point for the repository onboarding script.

    Loads the configuration, authenticates with GitHub,
    and onboards all configured repositories.
    """
    config = "config/config.json"
    set_env(config)
    auth = github_auth()
    onboard_repos(auth)


if __name__ == "__main__":
    main()
