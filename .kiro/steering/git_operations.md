# Git Operations Authorization

Kiro is authorized to manage Git operations. For every task completion:

1. Run the pytest suite.
2. Run the GitHub Readiness Check hook.
3. If both pass, perform a git add, git commit (using Conventional Commits), and git push origin main.
4. If any check fails, stop and ask the user for guidance.

**Important:** Be very certain before pushing. Confirm ANY doubt with the user.
