# GitHub Repository Onboarding Tool

## Overview

This script automates the creation and onboarding of GitHub repositories within an organisation.

For each repository defined in a configuration file, the tool:

- Creates the GitHub repository.
- Grants a GitHub team **Maintain** permissions.
- Generates the local repository structure.
- Creates `.gitignore`, `.pre-commit-config.yaml`, and `CODEOWNERS` files.
- Copies GitHub Actions workflow templates (repo-type specific & common workflows).
- Copies GitHub composite actions (e.g. `setup-environment`).
- Copies PR template (`PULL_REQUEST_TEMPLATE.md`).
- Initialises a local Git repository, commits, and pushes the `main` branch.
- Configures branch protection rules for the `main` branch.
- Creates GitHub deployment environments (`nonprod` and `prod`).

The goal is to standardise new repositories and ensure they follow organisational governance from day one.

---

## Features

- **Automated Repository Provisioning**: Create public/private repos dynamically under your GitHub organisation.
- **Team Access Management**: Automatically assign Maintain access to specified team slugs.
- **Template-Based Scaffolding**: Modular copying of CI/CD workflows, composite actions, PR templates, and pre-commit configurations based on `repo_type`.
- **Governance Controls**: Automatic `CODEOWNERS` file creation targeting assigned teams.
- **Branch Protection & Settings**: Automatic setup of PR review requirements, approval counts, code owner reviews, admin enforcement, and automatic deletion of head branches on PR merge.
- **Deployment Environments**: Automated setup of `nonprod` and `prod` environments with reviewer protections.

---

## Repository Structure

```
.
├── config/
│   └── config.json
├── templates/
│   ├── actions/
│   │   └── setup-environment/
│   │       └── actions.yaml
│   ├── common/
│   │   └── pr_title_check.yaml
│   ├── infra/
│   │   └── ...
│   ├── application/
│   │   └── ...
│   ├── .pre-commit-config.yaml
│   └── PULL_REQUEST_TEMPLATE.md
├── onboard-github.py
└── README.md
```

---

## Prerequisites

- **Python**: 3.10+
- **Git**: Installed and available in environment PATH
- **GitHub Token**: Personal Access Token (PAT) or GitHub App token with Organization & Repository Management permissions

### Python Dependencies

Install required libraries via pip:

```bash
pip install GitPython PyGithub
```

---

## GitHub Token Permissions

Set the `GITHUB_TOKEN` environment variable prior to running the script:

```bash
export GITHUB_TOKEN="<your-github-token>"
```

*On Windows (PowerShell):*

```powershell
$env:GITHUB_TOKEN="<your-github-token>"
```

---

## Configuration

Repository onboarding is driven by `config/config.json`.

### Example `config/config.json`:

```json
{
  "organisation": "my-rha-calvary",
  "repos": [
    {
      "repo_name": "terraform-network",
      "repo_type": "infra",
      "team_slug": "platform-team",
      "delete_branch_on_merge": true
    },
    {
      "repo_name": "application-api",
      "repo_type": "application",
      "team_slug": "backend-team",
      "delete_branch_on_merge": true
    },
    {
      "repo_name": "common-utility-repo",
      "repo_type": "",
      "team_slug": "dev-team"
    }
  ]
}
```

### Configuration Fields

| Field | Description |
|---|---|
| `organisation` | GitHub organisation slug (e.g. `my-rha-calvary`) |
| `repo_name` | Name of the GitHub repository to create |
| `repo_type` | Template directory under `templates/` matching the repository purpose (e.g. `infra`). Can be an empty string (`""`) to skip type-specific templates and only copy `common` workflows and `actions` |
| `team_slug` | GitHub team slug to grant Maintain permissions |
| `delete_branch_on_merge` | Optional boolean. Automatically delete head branches when PRs are merged. Defaults to `true` |

---

## Generated Repository Structure

Each generated repository will contain:

```
.
├── .github/
│   ├── CODEOWNERS
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── actions/
│   │   └── setup-environment/
│   │       └── actions.yaml
│   └── workflows/
│       ├── pr_title_check.yaml
│       └── <repo_type_workflows>.yaml  (if repo_type is non-empty)
├── .gitignore
└── .pre-commit-config.yaml
```

---

## Branch Protection & Repository Settings

### Main Branch Protection Rules

- Require pull request reviews (at least 1 approving review)
- Require Code Owner reviews
- Dismiss stale pull request approvals on new commits
- Enforce protection rules for administrators

### Repository Merge Settings

- Automatically delete head branches when pull requests are merged (`delete_branch_on_merge`: `true`)

### Deployment Environments

- `nonprod`: Standard deployment environment.
- `prod`: Protected production environment requiring team reviewer approval and preventing self-review.

---

## Running the Onboarding Script

Execute the script from the repository root:

```bash
python3 onboard-github.py
```

---

## Onboarding Architecture Flow

```
                     Read config/config.json
                               │
                               ▼
                    Authenticate with GitHub
                               │
                               ▼
                    Repository exists on GitHub?
                               │
                      ┌────────┴────────┐
                     Yes                No
                      │                 │
             Skip repo creation   Create GitHub repo
                                        │
                                        ▼
                             Assign Team Maintain Access
                                        │
                                        ▼
                             Generate Local Files
                       (CODEOWNERS, .gitignore, templates)
                                        │
                                        ▼
                            Copy Workflows & Actions
                        (Repo-specific, Common, Actions)
                                        │
                                        ▼
                             Git Init & Commit local
                                        │
                                        ▼
                             Push Main Branch to Remote
                                        │
                                        ▼
                            Apply Branch Protection
                                        │
                                        ▼
                           Create Nonprod & Prod Envs
                                        │
                                        ▼
                                    Complete
```

---

## Local Pre-commit Hook Setup

To enforce code quality checks locally before committing:

```bash
# 1. Install pre-commit
pip install pre-commit

# 2. Install git hooks
pre-commit install

# 3. Manually run checks across all files
pre-commit run --all-files
```
<!-- START_RELEASE_TABLE -->
| Repository | Latest Release | Release Notes |
| :--- | :--- | :--- |
| [my-rha-test-1](https://github.com/my-rha-calvary/my-rha-test-1) | `v1.0.0` | ## What's Changed * add readme by @rha-calvary in https://github.com/my-rha-calvary/my-rha-test-1/pu... |
| [my-rha-test-2](https://github.com/my-rha-calvary/my-rha-test-2) | `v1.0.0` | ## What's Changed * feat: add new release by @rha-calvary in https://github.com/my-rha-calvary/my-rh... |
| [my-rha-test-3](https://github.com/my-rha-calvary/my-rha-test-3) | `No Release` | N/A |
<!-- END_RELEASE_TABLE -->