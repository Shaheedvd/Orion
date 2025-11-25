<#
push_repo.ps1

Helper script to create a GitHub repository (using gh if available) and push current folder.
Run this script in PowerShell from the project root (where the .git folder is or will be created).

Usage examples:
.\push_repo.ps1 -RepoName Orion -Visibility public

This script will:
- Initialize git if needed
- Stage and commit files if there are no commits
- If GitHub CLI (gh) is installed and authenticated, create the repo and push using gh
- Otherwise prompt for the remote URL and push using git (you'll need to authenticate)

Security: This script does not store credentials. For best UX, install GitHub CLI and run `gh auth login` before running this script.
#>
param(
    [string]$RepoName = $(Split-Path -Leaf (Get-Location)),
    [ValidateSet('public','private')]
    [string]$Visibility = 'public'
)

function Run-GitCommand {
    param($cmd)
    Write-Host "> $cmd"
    iex $cmd
}

# Ensure git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git is not installed or not on PATH. Install Git for Windows first: https://git-scm.com/download/win"
    exit 1
}

# Initialize repo if needed
if (-not (Test-Path .git)) {
    Write-Host "Initializing git repository..."
    Run-GitCommand "git init"
}

# Stage files
Run-GitCommand "git add ."

# Commit if no commits
$hasCommits = $false
try {
    git rev-parse --verify HEAD > $null 2>&1
    if ($LASTEXITCODE -eq 0) { $hasCommits = $true }
} catch { $hasCommits = $false }

if (-not $hasCommits) {
    $msg = Read-Host -Prompt "Enter commit message (or press Enter for default)"
    if ([string]::IsNullOrWhiteSpace($msg)) { $msg = "Initial commit" }
    Run-GitCommand "git commit -m `"$msg`""
} else {
    Write-Host "Repository already has commits. Skipping initial commit."
}

# Ensure branch is main
Run-GitCommand "git branch -M main"

# If gh is installed, prefer using it
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "Detected GitHub CLI (gh). Checking authentication..."
    $auth = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "You are not authenticated with gh. Run: gh auth login"
        Write-Host "Opening gh auth login..."
        gh auth login
    }

    Write-Host "Creating repo $RepoName on GitHub (visibility: $Visibility) and pushing..."
    # Use --source and --push to create and push from local dir
    gh repo create $RepoName --$Visibility --source=. --remote=origin --push
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Repository created and pushed. Visit: https://github.com/$(gh api user --jq .login)/$RepoName"
        exit 0
    } else {
        Write-Error "gh repo create failed. You can still push manually."
    }
}

# gh not available: prompt for remote URL
$remote = Read-Host -Prompt "Enter remote URL (e.g. https://github.com/USERNAME/$RepoName.git)"
if ([string]::IsNullOrWhiteSpace($remote)) { Write-Error "No remote provided. Exiting."; exit 1 }

# Fix origin and push
Run-GitCommand "git remote remove origin 2>$null || echo ''"
Run-GitCommand "git remote add origin $remote"
Write-Host "Pushing to origin main. You may be prompted for credentials."
Run-GitCommand "git push -u origin main"

Write-Host "Done. If push succeeded, check your GitHub repo at: $remote"
