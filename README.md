# Automated Repository Provisioner

An automated, self-service tool for instantly creating and bootstrapping standardized GitHub repositories for your organization.

---

## 💡 What This Automation Does

When a team needs a new repository, this tool handles the entire setup process in seconds—eliminating manual configuration and ensuring all organization standards, security rules, and deployment pipelines are enforced automatically.

### Key Benefits & Automated Features

* **Instant Repository Creation**: Creates a private repository under your organization instantly.
* **Team Access Granted**: Automatically gives your team **Maintainer** access so everyone can start collaborating immediately.
* **Automatic Code Ownership**: Assigns code ownership (`CODEOWNERS`) to your team so pull requests are automatically routed to the right people.
* **Pre-Built Testing & Quality Checks**: Configures an automated Validation Pipeline (CI) that tests code whenever a pull request is opened.
* **Safe, Sequential Deployments**: Configures a Multi-Environment Pipeline (CD) that safely deploys code in sequence—testing first, then production.
* **Protected Main Branch**: Prevents direct pushing to the main branch. All changes must go through pull requests with required team approvals.
* **Production Guardrails**: Safeguards the production environment by requiring team review and preventing team members from self-approving production releases.

---

## 🚀 How to Create a New Repository

Any authorized team member can trigger this tool directly from GitHub:

1. Go to the **Actions** tab in this repository.
2. Select **Automation - Create New Repository** from the left sidebar.
3. Click the **Run workflow** dropdown button on the right.
4. Enter the **Repository Name** you wish to create.
5. Click **Run workflow**.

Within 1–2 minutes, your new repository will be created, configured, and ready for development.

---

## ⚙️ Organization Setup Guide (One-Time Setup)

To allow this workflow to create repositories and manage settings on behalf of your organization securely, a **GitHub App** must be set up. Follow these step-by-step instructions.

### Step 1: Create the GitHub App

1. Go to your Organization Settings:
   `https://github.com/organizations/YOUR_ORG_NAME/settings/apps`
2. Click **New GitHub App**.
3. Configure basic information:
   * **GitHub App name**: `Org Repo Provisioner` (or your preferred name)
   * **Homepage URL**: `https://github.com/YOUR_ORG_NAME`
4. Under **Webhook**, uncheck **Active** (no webhooks needed).

---

### Step 2: Configure Required Permissions

Scroll down to **Permissions** and set the following:

#### **Repository Permissions**
| Permission | Access | Purpose |
| :--- | :--- | :--- |
| **Administration** | **Read & write** | Creates repositories and branch protection rules |
| **Contents** | **Read & write** | Pushes initial project files and commits |
| **Environments** | **Read & write** | Creates test and production deployment targets |
| **Workflows** | **Read & write** | Manages CI/CD pipeline definition files |

#### **Organization Permissions**
| Permission | Access | Purpose |
| :--- | :--- | :--- |
| **Members** | **Read-only** | Automatically looks up team IDs by team slug |

Click **Create GitHub App** at the bottom of the page.

---

### Step 3: Install the App in Your Organization

1. After creation, click **Install App** on the left sidebar.
2. Click **Install** next to your organization name.
3. Select **All repositories** (allows managing organization-wide settings and new repos).
4. Click **Install**.

---

### Step 4: Generate App Credentials

1. Go back to your App's **General** settings tab.
2. Copy the **App ID** (a sequence of numbers near the top).
3. Scroll down to the **Private keys** section and click **Generate a private key**.
4. A `.pem` key file will download to your computer.

---

### Step 5: Save Secrets in GitHub Actions

Convert the private key file into a single line using Base64 encoding to prevent line-break formatting errors:

* **Mac / Linux Terminal**:
  ```bash
  base64 -i your-app-key.pem
