# Publishing Checklist

## Before publishing
- [ ] Run the unit tests.
- [ ] Launch the app and manually check each page.
- [ ] Verify SDK comparison refreshes when inputs change.
- [ ] Confirm reports do not contain API keys.
- [ ] Review `git status` and ensure `.venv`, `.env`, backups, and secrets are ignored.
- [ ] Capture genuine screenshots using synthetic/non-sensitive data.
- [ ] Add screenshots under `docs/images/` and update the README gallery.
- [ ] Choose and add a license only if you intend to grant reuse rights.

## Commit and push
```powershell
git status
git add README.md requirements.txt docs
git add .
git diff --cached --check
git diff --cached --stat
git commit -m "Add project documentation and screenshots"
git push
```

Review the staged diff before committing. Do not add local credentials or private data.
