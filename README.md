# Forge

**Forge** is a lightweight, Git-like version control system built in Python with a custom remote backend.  
It allows you to track files, commit changes, and synchronize repositories with a remote server using a simple CLI.

Forge works together with **Vault**, which acts as the remote storage layer where your repositories, commits, and files are stored.

---

## Architecture Overview

- **Forge** → CLI tool you run locally (version control client)
- **Vault** → Remote server that stores repositories, commits, and file data

When you push a repository using Forge, **your entire repo is stored remotely in Vault**.  
Cloning or forking a repo pulls data back from Vault to your local machine.

---

## Features

### Local Version Control
- Initialize a repository (`init`)
- Track files individually or all at once (`add`)
- Remove files from tracking (`remove`)
- Commit changes with messages (`commit`)
- Checkout previous commits (`checkout`)
- List commit history (`list commits`)
- `.forgeignore` support for ignoring files and folders

### Remote (Vault-powered)
- User authentication (`register`, `login`, `logout`)
- Push repositories to the remote Vault server (`push`)
- Clone repositories stored in Vault (`clone`)
- Fork repositories into your account (`fork`)
- List your repositories (`repos`)
- Delete remote repositories (`delete`)

---

## Installation

### Option 1: Python (Development)

This option is recommended if you are developing Forge or running it directly from source.

```bash
git clone https://github.com/ridit-jangra/Forge
cd Forge
pip install -r requirements.txt
python forge.py <command>
```

---

### Option 2: Executable (Recommended)

If you downloaded the compiled executable:

```bash
forge.exe <command>
```

No Python installation or configuration is required.

---

## Vault Configuration

⚠️ **Vault configuration is only required when using Forge via Python (development mode).**

When using the **compiled executable**, Vault configuration is **already set internally**, and you do not need to configure anything.

### Python-only Configuration

Forge connects to Vault using environment variables.

Optional `.env` file:

```env
FORGE_SERVER_URL=http://localhost:8000
FORGE_SESSION=.forge_session
```

If these variables are not set, sensible defaults are used.

---

## Usage

### Initialize Repository
```bash
forge init
```

### Track & Commit
```bash
forge add .
forge commit "Initial commit"
```

### Push to Vault (Remote)
```bash
forge push
```

Your repository, commits, and files are now **stored remotely in Vault**.

---

## Remote Operations

```bash
forge clone <owner_id>/<repo_name>
forge fork <owner_id>/<repo_name>
forge repos
forge delete
```

---

## `.forgeignore`

Example:

```text
node_modules
.env
*.log
dist
```

---

## Example Workflow

```bash
forge init
forge add .
forge commit "Initial commit"
forge push

forge clone 12/sample
```

---

## Limitations
- Text files only
- No branches or merges
- Linear history
- Early-stage project (breaking changes possible)

---

## License
MIT License
