# Getting Started with Git: Installation and Setup Guide

Written by Fredrik Kämmerling, Project Manager, Company 3

## Sequence Steps for Windows (see for MAC below):

### Download Git (If you do not know you have it already):

1. Go to the [Git website](https://git-scm.com/downloads).
2. Download the Windows 64-bit installer.
3. Follow the installation instructions

### Generate SSH Key (If you do not have a SSH key added in GitLab already):

4. Press the **Windows key** and type `cmd`.
5. Open **Command Prompt** and type:
   ```bash
   ssh-keygen -t ed25519
   ```
6. Press **Enter** three times to accept the default location and skip setting a password for the ssh key.

### Copy SSH Key:

7. Navigate to the location where the key was saved, usually `C:/Users/<YourUserName>/.ssh/id_ed25519.pub`.
8. Right-click on `id_ed25519.pub` and choose **Open with** a text editor (e.g., Notepad).
9. Copy all the contents of the file, starting with `ssh-ed25519`.

### Add SSH Key to GitLab:

10. Go to [GitLab](https://gitlab.liu.se).
11. Click on your profile picture, then select **Preferences**.
12. In the left-hand menu, click **SSH Keys**.
13. Click **Add New Key**.
14. Paste the SSH key into the big text box and press **Add Key**.

### Open Git Bash:

15. Right-click in a folder where you want to save the repository.
16. Select **Show more options**.
17. Click **Open Git Bash here**.

### Clone Repository:

18. In the terminal, type:
    ```bash
    git clone git@gitlab.liu.se:tddc88-ht24/company3.git
    ```
19. Press **Enter**.
20. If prompted about the fingerprint, type **yes**.

### Error Handling (Optional):

- If you encounter the error `fatal: Could not read from remote repository`, type:
  ```bash
  git config --global user.email "yourLiUID@student.liu.se"
  ```
  Return to step 18.

## Sequence Steps for MAC:

### Download Git (If you do not know you have it already):

1. Open **Terminal** from **Applications** > **Utilities** or by pressing **Command + Space** and typing "Terminal".
2. Install Homebrew by typing
   `bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
`
   If you are propmted to enter a password, the password is the same one you use to log in to your computer.
3. When it is done installing, type
   ```bash
   brew install git
   ```

### Generate SSH Key (If you have not added a key already):

4. In **Terminal**, type:
   ```bash
   ssh-keygen -t ed25519
   ```
5. Press **Enter** three times to accept the default location and skip setting a password for the ssh key.

### Copy SSH Key:

6. In **Terminal**, type:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
7. Copy the output, starting with `ssh-ed25519`.

### Add SSH Key to GitLab:

8. Go to [GitLab](https://gitlab.liu.se).
9. Click on your profile picture, then select **Preferences**.
10. In the left-hand menu, click **SSH Keys**.
11. Click **Add New Key**.
12. Paste the SSH key into the big text box and press **Add Key**.

### Open Terminal:

13. Open a **Terminal** by pressing **Command + Space** and typing "Terminal" and **cd** to where you want to save your repository.

### Clone Repository:

14. In the terminal, type:
    ```bash
    git clone git@gitlab.liu.se:tddc88-ht24/company3.git
    ```
15. Press **Enter**.
16. If prompted about the fingerprint, type **yes**.

### Error Handling (Optional):

- If you encounter the error `fatal: Could not read from remote repository`, type:
  ```bash
  git config --global user.email "yourLiUID@student.liu.se"
  ```
  Return to step 14.

# Git Flow Integration Model

Written by Jonathan Hermansson and Emil Näslund Löthmark, Developers, Company 3

We will use **Git Flow** as our integration model. The key branches in this workflow are:

- **Main Branch**: Production-ready code.
- **Development Branch**: Integration branch for features and testing.

New branches should always be created from the `development` branch, and once complete, merged back into it. Testers should use the `development` branch to test before any changes are merged into the `main` branch.

## Cloning the Git Project

To clone the repository, use one of the following commands:

```bash
- Via HTTPS: `git clone https://gitlab.liu.se/tddc88-ht24/company3.git`
```

```bash
- Via SSH: `git clone git@gitlab.liu.se:tddc88-ht24/company3.git`
```

This will create a local copy of the remote repository.

## Basic Git Workflow

### See Current Branch

To check which branch you're on, use:

```bash
- `git branch`
```

The active branch will have a star `*` beside it. Use this and make sure you are on the `development` branch before proceeding to the next step.

### Create a Branch

No one should push changes directly to `main`. Instead, create a new branch for each feature or fix you're working on and name it accordingly:

eg.

```bash
- `git checkout -b feature/your-feature-name`
-  `fix/your-fix-name`
-  `docs/docname-update`
```

... and so on

This creates a new branch and switches to it.

### Implement Changes

Make your changes to the codebase as necessary.

### Stage Changes

After making changes, stage the files you modified:

```bash
- `git add file1 file2 …`
```

- or

```bash
- `git add .` (this adds all files in the folder)
```

Staging prepares your changes to be committed.

### Commit Changes

Commit the changes with a descriptive message:

```bash
- `git commit -m "Implemented change X"`
```

Committing saves your changes to the local repository.

### Pull from Remote `development` Branch

Before pushing, it’s a good practice to ensure your feature branch is up to date with the latest `development` changes:

```bash
- `git pull origin development`
```

This pulls any new changes from `development` into your feature branch and helps resolve conflicts before merging.

### Push Changes

Once your feature branch is up to date and all changes are committed, push your branch to the remote repository:

```bash
- `git push origin your-branch-name`
```

### Merge Changes (Done on GitLab)

Once your feature branch is pushed:

1. Create a merge request (MR) from your branch to the `development` branch in GitLab.
2. Assign the lead developer(?) (or the appropriate reviewer) to review the changes.
3. Ensure the option to **delete the source branch upon merge** is enabled.

This will initiate the review process and integrate your changes into `development`.

### Delete Your Working Branch Locally (After Merge)

After the merge request is approved and merged, delete your local feature branch:

```bash
- `git branch -d your-branch-name`
```

If the remote branch still exists (in case the option to delete it wasn't enabled during the merge), you can delete it manually:

```bash
- `git push origin --delete your-branch-name`
```

## Git Commands Cheat Sheet

| Command                             | Description                                              |
| ----------------------------------- | -------------------------------------------------------- |
| `git status`                        | Check the current status of your working directory       |
| `git add <file>`                    | Stage changes for commit                                 |
| `git commit -m "message"`           | Commit changes with a message                            |
| `git pull origin <branch>`          | Pull the latest changes from the remote branch           |
| `git push origin <branch>`          | Push changes to the remote branch                        |
| `git checkout <branch>`             | Switch to an existing branch                             |
| `git checkout -b <branch-name>`     | Create a new branch and switch to it                     |
| `git rebase <branch>`               | Rebase the current branch on top of the specified branch |
| `git merge <branch>`                | Merge the specified branch into the current branch       |
| `git log`                           | View the commit history                                  |
| `git branch -d <branch-name>`       | Delete a local branch                                    |
| `git push origin --delete <branch>` | Delete a remote branch                                   |

---
