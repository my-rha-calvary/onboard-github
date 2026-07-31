# GitHub Repository Onboarding Tool

## Overview

This script automates the creation and onboarding of GitHub repositories within an organisation.

For each repository defined in a configuration file, the tool:

- Creates the GitHub repository.
- Grants a GitHub team **Maintain** permissions.
- Generates the initial repository structure.
- Creates a `.gitignore`.
- Creates a `CODEOWNERS` file.
- Copies GitHub Actions workflow templates.
- Initializes a local Git repository.
- Creates and pushes the initial commit.
- Configures branch protection for the `main` branch.
- Creates GitHub deployment environments.

The goal is to standardise new repositories and ensure they follow organisational governance from day one.

---

# Features

- Automated GitHub repository creation
- Team permission assignment
- Standard repository bootstrap
- GitHub Actions workflow templating
- Automatic CODEOWNERS generation
- Initial Git commit and push
- Main branch protection
- Creation of deployment environments
- Configuration-driven onboarding

---

# Repository Structure

```
.
├── config/
│   └── config.json
├── templates/
│   ├── infra/
│   ├── application/
│   └── ...
├── onboard.py
└── README.md
```

The **templates** directory contains workflow templates that are copied into each newly created repository.

---

# Prerequisites

- Python 3.10+
- Git installed
- GitHub Personal Access Token (PAT) or GitHub App token
- Access to the target GitHub organisation

Python packages:

```bash
pip install GitPython PyGithub
```

---

# GitHub Token Permissions

The token used by this script should have permissions to:

- Create repositories
- Read organisation information
- Read teams
- Manage repository permissions
- Configure branch protection
- Create deployment environments

The token must be exported before running the script.

Example:

```bash
export GITHUB_TOKEN=<your-token>
```

or on Windows

```powershell
$env:GITHUB_TOKEN="<your-token>"
```

---

# Configuration

Repository onboarding is driven by `config/config.json`.

Example:

```json
{
  "organisation": "my-org",
  "repos": [
    {
      "repo_name": "terraform-network",
      "repo_type": "infra",
      "team_slug": "platform-team"
    },
    {
      "repo_name": "application-api",
      "repo_type": "application",
      "team_slug": "backend-team"
    }
  ]
}
```

## Configuration Fields

| Field | Description |
|--------|-------------|
| organisation | GitHub organisation name |
| repo_name | Repository name |
| repo_type | Template folder under `templates/` |
| team_slug | GitHub team to grant Maintain access |

---

# Template Structure

Each repository type has its own template folder.

Example:

```
templates/
├── infra/
│   ├── build.yaml
│   └── deploy.yaml
│
├── application/
│   ├── build.yaml
│   └── release.yaml
```

All `.yaml` files are copied into:

```
.github/workflows/
```

inside the newly created repository.

---

# Generated Repository

Each repository will contain:

```
.
├── .github
│   ├── CODEOWNERS
│   └── workflows
│       ├── build.yaml
│       └── deploy.yaml
└── .gitignore
```

---

# Branch Protection

The script automatically configures protection on the `main` branch.

Settings include:

- Require pull request reviews
- Require one approval
- Require CODEOWNER reviews
- Dismiss stale approvals
- Enforce rules for administrators

---

# Deployment Environments

The following GitHub environments are created automatically.

## nonprod

Standard deployment environment.

## prod

Production environment configured with:

- Required reviewers
- Prevent self-review

---

# Running the Script

Run:

```bash
python onboard.py
```

The script will:

1. Read the configuration.
2. Authenticate with GitHub.
3. Check whether each repository already exists.
4. Create missing repositories.
5. Bootstrap the repository.
6. Push the initial commit.
7. Configure repository governance.

---

# Workflow

```
Read config
      │
      ▼
Authenticate to GitHub
      │
      ▼
Repository exists?
      │
 ┌────┴────┐
 │         │
Yes        No
 │         │
Skip    Create repository
             │
             ▼
Assign team permissions
             │
             ▼
Generate repository files
             │
             ▼
Copy workflow templates
             │
             ▼
Initial Git commit
             │
             ▼
Push to GitHub
             │
             ▼
Configure branch protection
             │
             ▼
Create deployment environments
             │
             ▼
Complete
```

---

# Notes

- Existing repositories are skipped.
- Repository names must be unique within the organisation.
- The configured GitHub team must already exist.
- Workflow templates are copied from the directory matching the configured `repo_type`.

---

# Future Enhancements

Potential improvements include:

- Configurable branch protection policies
- Repository topics
- Repository description
- Default labels
- Secrets and variables
- Repository rulesets
- Dependabot configuration
- License templates
- README templates
- Issue templates
- Pull request templates
- Template repositories
- Better logging
- Dry-run mode
- Parallel repository creation
- Unit tests
