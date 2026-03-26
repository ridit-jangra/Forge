# Forge

Forge is a lightweight version control system built from scratch. Designed to be simple, fast, and easy to understand — Forge gives you the core of a VCS without the complexity of Git.

## Installation

```bash
# using bun
bun add @ridit/forge -g

# using npm
npm install -g @ridit/forge
```

## Features

- **Init** — initialize a new Forge repository
- **Add** — stage files for commit
- **Commit** — snapshot your staged files with a message
- **Log** — view commit history per branch or globally
- **Checkout** — restore a previous commit
- **Branches** — create, switch, and manage isolated branches
- **Merge** — merge branches with conflict detection
- **Status** — view modified, staged, untracked, and deleted files
- **Checkpoints** — auto-saved snapshots when switching branches
- **ForgeIgnore** — `.forgeignore` support to exclude files

## CLI Commands

```bash
forge init                              initialize an empty repo

forge add .                             stage all files
forge add <path>                        stage a specific file

forge commit -m "message" -a           commit all staged files
forge commit -m "message"              commit staged files

forge log                              view commits in current branch
forge log -g                           view all commits globally

forge checkout <commitId>              restore a commit in current branch
forge checkout <commitId> -b <branch>  restore a commit in a specific branch

forge branch <name>                    create a new branch
forge branch <name> -s                 switch to a branch
forge branch <name> -d                 delete a branch
forge branch <name> -m <branch>        merge a branch into current branch

forge status                           show file statuses
```

## How It Works

Forge stores all data in a `.forge` folder at the root of your repository:

```
.forge/
├── commits/          ← global commit refs (lightweight)
├── branches/
│   └── main/
│       ├── branch.json       ← branch metadata + latest commit id
│       ├── checkpoint.json   ← auto-snapshot saved on branch switch
│       └── commits/          ← full commits with file blobs
├── repo.json         ← repo metadata + active branch
└── tempAddedFiles.json  ← staging area
```

## Branch System

- Every branch stores its own commit history
- Switching branches auto-saves a **checkpoint** of your current working state
- On switch back, Forge restores from checkpoint if it's up to date, otherwise falls back to the latest commit
- Merging compares changes since the **merge base** (last shared commit) and detects conflicts

## File Statuses

| Status      | Meaning                              |
| ----------- | ------------------------------------ |
| `untracked` | new file, not in last commit         |
| `modified`  | changed since last commit            |
| `staged`    | added to staging area                |
| `deleted`   | in last commit but removed from disk |

## License

MIT
